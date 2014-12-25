import uuid
import copy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.util import object_state
from sqlalchemy import inspect

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
        users=[]
        project_id = request.GET.get('project_id')
        project = self.db.get_project(project_id)
        
        #query = self.db.get_users(project_id=project_id)
	#print query
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
        
        name=body.get('name')
        email=body.get('email')
        role_id=body.get('role_id')
        project_id=body.get('project_id')
	project = self.db.get_project(project_id) 
        #print type(project)
        #state = object_state(project)
        #print state.detached
        #print state.session
        session = inspect(project).session 
        #project = state.session.expunge(project)
        #print project
        
        try:
            user_ref=self.db.add_user(session,
                        dict(id = uuid.uuid4().hex,
                             name = name,
                             email = email,
                             role_id = role_id),
                             #project = copy.deepcopy(project))
                             project = project)
        except IntegrityError,err:
	    LOG.error(err)
	    return Response(500) 
        
        return Response(200) 

    
    def delete(self,request,id):
        self.db.delete_user(id)

        return Response(200) 

def create_resource():
    return wsgi.Resource(Controller())
