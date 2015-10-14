import uuid
import json
from nae.common import cfg
from nae.common import log as logging

from nae.common.cfg import Str, Int
from nae.common import client
import requests

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class API(object):
    def __init__(self):
        self.host = Str(CONF.host)
        self.port = Int(CONF.port)
        self.headers = {'Content-Type': 'application/json'}
        self.http = client.HTTPClient()

    def create(self, name, kwargs):
        """
        Create temporary container for image online edit.
        """
        data = {
            'Hostname': '',
            'User': '',
            'Memory': '',
            'MemorySwap': '',
            'AttachStdin': False,
            'AttachStdout': False,
            'AttachStderr': False,
            'PortSpecs': [],
            'Tty': True,
            'OpenStdin': True,
            'StdinOnce': False,
            'Env': [],
            'Cmd': ["/opt/webssh/term.js/example/index.js"],
            'Dns': None,
            'Image': None,
            'Volumes': {},
            'VolumesFrom': '',
            'ExposedPorts': {"17698/tcp": {}}
        }
        data.update(kwargs)
        resp = self.http.post("http://%s:%s/containers/create?name=%s" % \
                            (self.host,self.port,name),
                            headers={'Content-Type':'application/json'},
                            data=json.dumps(data))

        return resp

    def start(self, host, port, uuid):
        """start container for image online edit."""
        data = {
            'Binds': [],
            'Links': [],
            'LxcConf': {},
            'PublishAllPorts': False,
            'PortBindings':
            {"17698/tcp": [{"HostIp": host,
                            "HostPort": str(port)}]},
            'Cmd': ["/opt/webssh/term.js/example/index.js"],
            'Privileged': False,
            'Dns': [],
            'VolumesFrom': [],
            'CapAdd': [],
            'CapDrop': []
        }
        resp = self.http.post("http://%s:%s/containers/%s/start" % \
                                 (self.host,self.port,uuid),
                                 headers={'Content-Type':'application/json'},
                                 data=json.dumps(data))

        return resp

    def inspect(self, name):
        """
        Inspect image by image `name`.
        """
        resp = self.http.get("http://%s:%s/images/%s/json" % \
                                (self.host,self.port,name))
        return resp.status_code, resp.json()

    def build(self, name, data):
        """
        Build image with name `name` and data `data`.
        The `data` must be a tar stream and must contain a ``Dockerfile``

        :params name: image name
        :params data: tar stream data with ``Dockerfile``
        """
        resp = self.http.post(
            "http://%s:%s/build?t=%s" % (self.host, self.port, name),
            headers={'Content-Type': 'application/tar'},
            data=data)
        return resp.status_code

    def delete(self, repository, tag):
        """
        Delete image from private image registry
        
        :param repository: image repository
        :param tag       : image tag
        """
        image_registry_endpoint = CONF.image_registry_endpoint
        if not image_registry_endpoint:
            LOG.error('no registry endpoint found!')
            return 404
        if not image_registry_endpoint.startswith("http://"):
            image_registry_endpoint = "http://" + image_registry_endpoint

        resp = self.http.delete("%s/v1/repositories/%s/tags/%s" % \
				(image_registry_endpoint,repository,tag))
        return resp.status_code

    def tag(self, name, tag="latest"):
        """
        Tag image to specified tag.If tag not provided, "latest" will be used.

        :params name: image name
        :params tag : image tag, default is ``latest``
        """
        image_registry_endpoint = CONF.image_registry_endpoint
        if not image_registry_endpoint:
            LOG.error('no registry endpoint found!')
            return 404
        if image_registry_endpoint.startswith("http://"):
            image_registry_endpoint = image_registry_endpoint.replace(
                "http://", "")
        host = Str(CONF.host)
        port = Int(CONF.port)

        resp = self.http.post(
            "http://%s:%s/images/%s:%s/tag?repo=%s/%s&force=1&tag=%s" %
            (host, port, name, tag, image_registry_endpoint, name, tag))
        return resp.status_code, "%s/%s" % (image_registry_endpoint, name)

    def push(self, name, tag="latest"):
        """
        Push image to image private registry.
 
        :params name: image name
        :params tag : image tag,default is latest
        """
        resp = self.http.post("http://%s:%s/images/%s/push?tag=%s" % \
                                (self.host,self.port,name,tag),
           headers={'X-Registry-Auth':uuid.uuid4().hex})
        return resp.status_code

    def destroy(self, name):
        """
        Destroy image by image `name`
 
        :params name: image name
        """
        resp = self.http.post("http://%s:%s/containers/%s/stop" % \
                              (self.host,self.port,name))

        resp = self.http.delete("http://%s:%s/containers/%s" % \
                              (self.host,self.port,name))

    def commit(self, container, repository, tag):
        """
        Commit container to image

        :params container : the container to be commited
        :params repository: the image repository 
        :params tag       : the image tag
        """
        resp = self.http.post("http://%s:%s/commit?author=&comment=&container=%s&repo=%s&tag=%s" % \
                              (self.host,self.port,container,repository,tag))
        return resp
