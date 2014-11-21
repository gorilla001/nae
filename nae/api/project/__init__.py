from nae import wsgi
from nae.api.project import projects
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self.resource=projects.create_resource()
	self.setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def setup_routes(self):
	self.mapper.connect('/projects',
				controller=self.resource,
				action='index',
				conditions={'method':['GET']})
        self.mapper.connect('/projects',
				controller=self.resource,
				action='create',
				conditions={'method':['POST']})
        self.mapper.connect('/projects/{id}',
				controller=self.resource,
				action='delete',
				conditions={'method':['DELETE']})
        self.mapper.connect('/projects/{id}',
				controller=self.resource,
				action='show',
				conditions={'method':['GET']})
        self.mapper.connect('/projects/{id}',
				controller=self.resource,
				action='update',
				conditions={'method':['PUT']})

