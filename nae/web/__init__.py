from nae import wsgi
from nae.web import controller 
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self._setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_routes(self):

        self.mapper.resource('image','images',
                             controller=controller.create_resource())

