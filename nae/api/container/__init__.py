from nae import wsgi
from nae.api.container import containers
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self.resource=containers.create_resource()
	self.setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def setup_routes(self):
	self.mapper.resource('container','containers',
			     controller=self.resource,
			     member={'start':'POST',
				     'stop':'POST',
                                     'reboot':'POST',
				     'commit':'POST',
                                     'destroy':'POST'})
