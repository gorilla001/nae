from nae import wsgi
from nae.api.image import images
import routes

class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper=routes.Mapper()
	self.resource=images.create_resource()
	self.setup_routes()
	super(APIRouter,self).__init__(self.mapper)

    def setup_routes(self):
        self.mapper.connect('/images',
        		controller=self.resource,
        		action='index',
        		conditions={'method':['GET']})
        
        self.mapper.connect('/images/{image_id}',
        		controller=self.resource,
        		action='show',
        		conditions={'method':['GET']})
        
        self.mapper.connect('/images/{image_id}/inspect',
        		controller=self.resource,
        		action='inspect',
        		conditions={'method':['GET']})
        
        self.mapper.connect('/images',
        		controller=self.resource,
        		action='create',
        		conditions={'method':['POST']})
        
        self.mapper.connect('/images/{image_id}',
        		controller=self.resource,
        		action='delete',
        		conditions={'method':['DELETE']})
        
	self.mapper.connect('/images/edit',
        		controller=self.resource,
        		action='edit',
        		conditions={'method':['POST']})
        
	self.mapper.connect('/images/commit',
        		controller=self.resource,
        		action='commit',
        		conditions={'method':['POST']})
        
	self.mapper.connect('/images/conflict/{image_id}',
        		controller=self.resource,
        		action='conflict',
        		conditions={'method':['GET']})

