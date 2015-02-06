import uuid
import copy
import webob.exc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.util import object_state
from sqlalchemy import inspect
import jsonschema

from jae import wsgi
from jae import base
from jae.common.timeutils import isotime
from jae.common import log as logging
from jae.common.response import Response, ResponseObject

LOG = logging.getLogger(__name__)

class Controller(base.Base):
    def __init__(self):
	super(Controller,self).__init__()

    def index(self,request):
        """
        List all users of the project identified by `project_id`.
        This method returns a disctionary list and
        echo dictionary contains the following keys:
            - id      the id of the user
            - name    the name of the user
            - email   the email address of the user
            - role_id the role_id of the user e.g. '0' '1' 
            - created the created time of the use
        If no use found, empty list will returned.
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
        """Get user detail according `id`"""
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
        add user db entry for specified project.
       
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

        name=body.get("name","")
        email=body.get("email","")
        role_id=body.get("role_id","")
        project_id=body.get("project_id","")
	project = self.db.get_project(project_id) 
        
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
        """delete user by `id`"""
        try:
            self.db.delete_user(id)
        except:
            raise
        """return webob.exc.HTTPNoContent() seems more better."""
        return webob.exc.HTTPNoContent()

def create_resource():
    return wsgi.Resource(Controller())
