from nae import wsgi
from nae.web.controller import images 
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self._setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_routes(self):

        self.mapper.resource('image','images',
                             controller=images.create_resource())

class StaticRouter(wsgi.Router):
    def __init__(self):
        self.mapper=routes.Mapper()
	self._setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_routes(self):
