from nae import wsgi
from nae import db
from nae.utils import isotime
import uuid
from sqlalchemy.exc import IntegrityError
import logging

LOG = logging.getLogger('eventlet.wsgi.server')

class Controller(object):
    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        users=[]
        project_id = request.GET.get('project_id')
        query = self.db_api.get_users(project_id=project_id)
        for item in query:
            user={
                'id':item.id,
                'name':item.name,
                'email':item.email,
                'role_id':item.role_id,
		'project_id':item.project_id,
                'created':isotime(item.created),
                }
            users.append(user)

        return users 

    def show(self,request,id):
	query = self.db_api.get_user(id)	
        if query is None:
	    return {}
        user={'id':query.id,
              'name':query.name,
              'email':query.email,
              'role_id':query.role_id,
	      'project_id':query.project_id,
              'created':isotime(query.created)}
	return user 

    def create(self,request,body):
        name=body.get('name')
        email=body.get('email')
        role_id=body.get('role_id')
        project_id=body.get('project_id')
        try:
            self.db_api.add_user(dict(
		id = uuid.uuid4().hex,
                name = name,
                email = email,
                role_id = role_id,
                project_id = project_id))
        except IntegrityError,err:
	    LOG.error(err)
	    return {"status":500}
        
        return {"status":200} 

    
    def delete(self,request,id):
        self.db_api.delete_user(id)

        return {"status":200} 

def create_resource():
    return wsgi.Resource(Controller())
