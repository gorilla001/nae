from jae import wsgi
from jae.image import images
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self._setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def _setup_routes(self):

        self.mapper.resource('image','images',
                             controller=images.create_resource(),
                             member={'destroy':'POST',
                                     'commit':'POST'})
