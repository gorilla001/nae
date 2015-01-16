from jae import wsgi
from jae.api import containers
from jae.api import images
from jae.api import projects
from jae.api import users 
from jae.api import repos 
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self._setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_routes(self):
        """
        The following `mapper.resource` will generated the following routes:
        """
        
        self.mapper.resource('container','containers',
			     controller=containers.create_resource(),
			     member={'start':'POST',
				     'stop':'POST',
                                     'reboot':'POST',
				     'commit':'POST',
                                     'destroy':'POST',
                                     'refresh':'POST'})
        self.mapper.resource('image',
                             'images',
			     controller=images.create_resource(),
                             member={'destroy':'POST'})

        self.mapper.connect('/images/commit',
			     controller=images.create_resource(),
                             action='commit',
                             conditions={'method':['POST']})

                            
        """Not used anymore."""
        #self.mapper.connect('/baseimages',
        #                controller=images.create_resource(),
        #                action='baseimage',
        #                conditions={'method':['GET']})
			     
        self.mapper.resource('project','projects',
			     controller=projects.create_resource())

        self.mapper.resource('user','users',
			     controller=users.create_resource())

        self.mapper.resource('repository','repos',
			     controller=repos.create_resource())
