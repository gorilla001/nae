from nae import wsgi
from nae.api.container import containers
from nae.api.image import images
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
        #self.resource=containers.create_resource()
	self._setup_route()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_route(self):
        self.mapper.resource('container','containers',
			     controller=containers.create_resource(),
			     member={'start':'POST',
				     'stop':'POST',
                                     'reboot':'POST',
				     'commit':'POST',
                                     'destroy':'POST'})
        self.mapper.resource('image','images',
			     controller=images.create_resource(),
			     member={'start':'POST',
				     'stop':'POST',
                                     'reboot':'POST',
				     'commit':'POST',
                                     'destroy':'POST'})
