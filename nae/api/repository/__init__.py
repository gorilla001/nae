from nae import wsgi
from nae.api.repository import repositories 
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self.resource=repositories.create_resource()
	self.setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def setup_routes(self):
	self.mapper.connect('/hgs',
				controller=self.resource,
				action='index',
				conditions={'method':['GET']})
        self.mapper.connect('/hgs',
				controller=self.resource,
				action='create',
				conditions={'method':['POST']})
        self.mapper.connect('/hgs/{id}',
				controller=self.resource,
				action='delete',
				conditions={'method':['DELETE']})
