import uuid
import copy
import webob.exc
from sqlalchemy.exc import IntegrityError

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
        List all projects.
        
        This method returns a dictionary list and each dict containers the following keys:
            - id
            - name
            - desc
            - created
        If no projects found, empty list will be returned.
        """
        projects=[]
        project_instances = self.db.get_projects()
	if project_instances:
	    for instance in project_instances:
                project = {
                    'id': instance.id,
                    'name': instance.name,
                    'desc': instance.desc,
                    'created': isotime(instance.created)
                    }
                projects.append(project)

        return ResponseObject(projects) 

    def show(self,request,id):
        """
        Show project detail according to project `id`.
      
        This method returns a dictionary with following keys:
            - id
            - name
            - desc
            - created
            - users
            - repos
            - images
            - containers
        If no project found, empty dictionary will be returned.
        """
        project_instance = self.db.get_project(id)
	if project_instance is None:
            return {}

        """get project user list."""
	user_list = [] 
	for user_instance in project_instance.users:
            user = {
                "id": user_instance.id, 
                "name": user_instance.name,
                "email": user_instance.email,
                "role_id": user_instance.role_id,
                "created" : isotime(user_instance.created)
                } 
            user_list.append(user)

        """"get project repo list."""
 	repo_list =[]
	for repo_instance in project_instance.repos:
	    repo = { "id":repo_instance.id,
		     "repo_path": repo_instance.repo_path,
                     "created": isotime(repo_instance.created)}
            repo_list.append(repo)

        """"get project image list."""
        image_list = []
        for image_instance in project_instance.images:
            image = {
                'id': image_instance.id,
                'uuid': image_instance.uuid,
                'name': image_instance.name,
		'tag': image_instance.tag,
                'desc': image_instance.desc,
                'project_id': image_instance.project_id,
                'created': isotime(image_instance.created),
                'user_id': image_instance.user_id,
                'status' : image_instance.status
                }
            image_list.append(image)

        """Get containes list"""
        container_list = []
        for item in project_instance.containers:
            container = {
                'id': item.id,
                'name': item.name,
                'uuid': item.uuid,
                'env': item.env,
                'project_id': item.project_id,
                'repos': item.repos,
                'branch': item.branch,
                'image_id': item.image_id,
                'network': item.network,
                'created': item.created,
                'user_id': item.user_id,
                'host_id': item.host_id,
                'status': item.status
                }             
            container_list.append(container)

        project = {
            "id": project_instance.id,
            "name": project_instance.name,
            "desc": project_instance.desc,
            "created": isotime(project_instance.created),
	    "users" : user_list,
            "repos" : repo_list,
            "images": image_list,
            "containers": container_list
            }
        
        return ResponseObject(project) 

    def create(self,request,body):
        """
        For creating project, body should be None and
        should contains the following params:
            - name the project name
            - desc the description for the project
        All the above params are not optional and have no default value.
        """
        schema = { 
            "type": "object",
            "properties": {
                 "name": {"type": "string","minLength":1,"maxLength":255},
                 "desc": {"type": "string"},
             }
        }
        try:
            self.validator(body,schema)
        except:
            raise

        name = body.pop("name")
        desc = body.pop("desc")

        try:
            self.db.add_project(dict(
			id = uuid.uuid4().hex, 
                        name = name,
                        desc = desc))
        except:
            raise

        return webob.exc.HTTPOk() 

    def delete(self,request,id):
        """
        Delete project identified by `id`.
        """
        LOG.info("DELETE +job delete %s" % id)
        try:
            self.db.delete_project(id)
        except IntegrityError,err:
	    LOG.error(err)
            LOG.info("DELETE -job delete = ERR")
	    return Response(500) 

        LOG.info("DELETE -job delete = OK")
        """return webob.exc.HTTPNoContent() seems more better."""
        return webob.exc.HTTPNoContent()

    def update(self, request, body):
        """Update project information"""
        return NotImplementedError()

     

def create_resource():
    return wsgi.Resource(Controller()) 
