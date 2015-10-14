from nae.container import wsgi
from nae.container import containers
import routes


class APIRouter(wsgi.Router):
    def __init__(self):

        self.mapper = routes.Mapper()
        self._setup_route()
        super(APIRouter, self).__init__(self.mapper)

    def _setup_route(self):
        self.mapper.resource('container',
                             'containers',
                             controller=containers.create_resource(),
                             member={
                                 'start': 'POST',
                                 'stop': 'POST',
                                 'reboot': 'POST',
                                 'commit': 'POST',
                                 'destroy': 'POST',
                                 'refresh': 'POST'
                             })
