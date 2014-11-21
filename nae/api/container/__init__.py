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
        self.mapper.connect('/containers',
        		controller=self.resource,
        		action='index',
        		conditions={'method':['GET']},
        )
        self.mapper.connect('/containers/{container_id}',
        		controller=self.resource,
        		action='delete',
        		conditions={'method':['DELETE']},
        )
        
        self.mapper.connect('/containers/{container_id}',
        		controller=self.resource,
        		action='show',
        		condition={'method':['GET']},
        )
        
        self.mapper.connect('/containers/{container_id}',
        		controller=self.resource,
        		action='inspect',
        		conditions={'method':['GET']},
        )

        self.mapper.connect('/containers/{container_id}/stop',
        		controller=self.resource,
        		action='stop',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/start',
        		controller=self.resource,
        		action='start',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/reboot',
        		controller=self.resource,
        		action='reboot',
        		conditions={'method':['POST']},
        )
        self.mapper.connect('/containers/{container_id}/commit',
        		controller=self.resource,
        		action='commit',
        		conditions={'method':['POST']},
        )
        
        self.mapper.connect('/containers/{container_id}/destroy',
        		controller=self.resource,
        		action='destroy',
        		conditions={'method':['POST']},
        )

        
        self.mapper.connect('/containers',
        		controller=self.resource,
        		action='create',
        		conditions={'method':['POST']},
        )
