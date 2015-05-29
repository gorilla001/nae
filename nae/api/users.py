import uuid
import copy
import webob.exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.util import object_state
from sqlalchemy import inspect
import jsonschema

from nae import wsgi
from nae import base
from nae.common.timeutils import isotime
from nae.common import log as logging
from nae.common.response import Response, ResponseObject

LOG = logging.getLogger(__name__)

class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

    def index(self,request):
        """
        List all users according to `project_id`.
        This method returns a dictionary list and each dict contains the following keys:
            - id       the unique 64 bytes uuid
            - name     the user name
            - email    user's email address
            - role_id  user's role_id
            - created  when user be added
        If no use found, empty list will be returned.
        """
        users=[]
        project_id = request.GET.get('project_id')
        project = self.db.get_project(project_id)
        
        for item in project.users:
            user={
                'id':item.id,
                'name':item.name,
                'email':item.email,
                'role_id':item.role_id,
                'created':isotime(item.created),
                }
            users.append(user)

        return ResponseObject(users)

    def show(self,request,id):
        """
        Show the use detail according to user `id`.
         
        :params id: the user id
 
        This method returns a dictionary with the following keys:
            - id         unique 64 bytes uuid
            - name       user's name
            - email      user's email address
            - role_id    user's role_id, which identified the current user
                         as super-user or normal-user.
            - projects   the project lists the user belong to
            - created    when the user be added   
        If no user found, empty dictionary will be returned.
        """
	query = self.db.get_user(id)	
        if query is None:
            LOG.error("no such user %s" % id)
	    return ResponseObject({'projects':[]}) 

        projects_list = []
        project_instances = query.projects
        for project in project_instances:
            project = {"id": project.id,
                       "name": project.name,
                       "desc": project.desc,
                       "created": isotime(project.created)}
            projects_list.append(project)

        user={'id':query.id,
              'name':query.name,
              'email':query.email,
              'role_id':query.role_id,
	      'projects':projects_list,
              'created':isotime(query.created)}

	return ResponseObject(user) 

    def create(self,request,body):
        """
        Add user db entry for specified project.
       
        NOTE(nmg):`project` isa `project instance` which
                   get from db. you must insert a `project
                   instance` object in model `User`'s `projects`
                   attribute.and deepcoy is used for disattach session
                   which `project` attached.
        FIXME(nmg):this is ugly,try to fixed it.
        """ 
        
        schema = {
            "type": "object",
            "properties": {
                "name" : { 
                    "type":"string", 
                    "minLength": 1, 
                    "maxLength": 255
                },
                "email": { 
                    "type":"string",
                    "pattern": "^.*@.*$",
                },
                "role_id": { 
                    "enum" : [ '0', '1', '2' ]
                },
                "project_id" : {
                    "type": "string",
                    "minLength": 32,
                    "maxLength": 64,
                    "pattern": "^[a-zA-z0-9]*$",
                 } 
             }
        }
        try:
            self.validator(body,schema)
        except jsonschema.exceptions.ValidationError as ex:
            LOG.error(ex)
            return webob.exc.HTTPBadRequest()

        name       = body.pop("name","")
        email      = body.pop("email","")
        role_id    = body.pop("role_id","")
        project_id = body.pop("project_id","")
	project    = self.db.get_project(project_id) 
        
        try:
            user_ref=self.db.add_user(dict(id = uuid.uuid4().hex,
                             name = name,
                             email = email,
                             role_id = role_id),
                             project = project)
        except IntegrityError,err:
	    LOG.error(err)
	    return webob.exc.HTTPInternalServerError() 
        
        return webob.exc.HTTPCreated() 

    
    def delete(self,request,id):
        """
        Delete user identified by `id`.
        """
        try:
            self.db.delete_user(id)
        except:
            raise
        """return webob.exc.HTTPNoContent() seems more better."""
        return webob.exc.HTTPNoContent()

    def update(self, request, body):
        """Update user informathion"""
        return NotImplementedError()

def create_resource():
    return wsgi.Resource(Controller())
