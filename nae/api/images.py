import webob
import uuid
import requests
import json
from jsonschema import SchemaError, ValidationError
from requests import exceptions
from sqlalchemy.exc import IntegrityError

from nae import wsgi
from nae import image
from nae.base import Base
from nae.common.timeutils import isotime
from nae.common import log as logging
from nae.common import cfg
from nae.common import quotas
from nae.common.exception import BodyEmptyError, ParamNoneError
from nae.common.response import Response, ResponseObject
from nae.common.view import View
from nae.common import utils
from nae.common import client

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

QUOTAS = quotas.Quotas()

_IMAGE_LIMIT = 12


class Controller(Base):
    def __init__(self):
        super(Controller, self).__init__()

        self.http = client.HTTPClient()

    def index(self, request):
        """
        List all images accorind to `project_id`.
        This method returns a dictionary list and each dict contains the following keys:
            - id
            - uuid
            - name
            - tag
            - desc
            - project_id
            - created
            - user_id
            - status
        If no images found, empty list will be returned.
        """
        images = []
        project_id = request.GET.get('project_id')
        if not project_id:
            LOG.error("project_id cannot be None")
            return webob.exc.HTTPNotFound()
        project_instance = self.db.get_project(project_id)
        if project_instance is None:
            LOG.error("no such project %s" % project_id)
            return webob.exc.HTTPNotFound()
        for image_instance in project_instance.images:
            image = {
                'id': image_instance.id,
                'uuid': image_instance.uuid,
                'name': image_instance.name,
                'tag': image_instance.tag,
                'desc': image_instance.desc,
                'project_id': image_instance.project_id,
                'created': isotime(image_instance.created),
                'user_id': image_instance.user_id,
                'status': image_instance.status
            }
            images.append(image)

        return ResponseObject(images)

    def show(self, request, id):
        """
        Show the image detail according to `id`.

        :parmas id: the image id

        This method returns a dictionary with the following keys:
            - id
            - uuid
            - name
            - repos
            - tag 
            - desc
            - project_id
            - created
            - user_id
            - status
        If no image found, empty dictionary will be returned.    
        """
        image = {}
        query = self.db.get_image(id)
        if query is not None:
            image = {
                'id': query.id,
                'uuid': query.uuid,
                'name': query.name,
                'repos': query.repos,
                'tag': query.tag,
                'desc': query.desc,
                'project_id': query.project_id,
                'created': isotime(query.created),
                'user_id': query.user_id,
                'status': query.status
            }

        return ResponseObject(image)

    def create(self, request, body=None):
        """
        For creating image, body should not be None and
        should contains the following params:
            - project_id  the project's id which the image belong to
            - name        the image name
            －desc        the image description
            - repos       the repos contains `Dockerfile`
            - branch      the branch
            - user_id     the user who created the image
        All the above params are not optional and have no default value.
        """
        """This schema is used for data validate"""
        schema = {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "minLength": 32,
                    "maxLength": 64,
                    "pattern": "^[a-zA-Z0-9]*$",
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255
                },
                "desc": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255
                },
                "repos": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255
                },
                "branch": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255
                },
                "user_id": {
                    "type": "string",
                    "minLength": 32,
                    "maxLength": 64,
                    "pattern": "^[a-zA-Z0-9]*$",
                },
            },
            "required": ["project_id", "name", "desc", "repos", "branch",
                         "user_id"]
        }
        try:
            self.validator(body, schema)
        except (SchemaError, ValidationError) as ex:
            LOG.error(ex)
            return webob.exc.HTTPBadRequest(explanation="Bad Paramaters")

#if not body:
#    LOG.error('body cannot be empty!')
#    return webob.exc.HTTPBadRequest()

#project_id = body.get('project_id')
#if not project_id:
#    LOG.error('project_id cannot be None!')
#    return webob.exc.HTTPBadRequest()

        limit = QUOTAS.images or _IMAGE_LIMIT
        query = self.db.get_images(project_id)
        if len(query) >= limit:
            LOG.error("images limit exceed,can not created anymore...")
            return webob.exc.HTTPMethodNotAllowed()

        #name = body.get('name',utils.random_str())
        #desc = body.get('desc','')

        #repos = body.get('repos')
        #if not repos:
        #    LOG.error('repos cannot be None!')
        #    return webob.exc.HTTPBadRequest()

        #branch = body.get('branch')
        #if not branch:
        #    LOG.error("branch cannot be None!")
        #    return webob.exc.HTTPBadRequest()

        #user_id = body.get('user_id')
        #if not user_id:
        #    LOG.error('user_id cannot be None!')
        #    return webob.exc.HTTPBadRequest()
        image_service_endpoint = CONF.image_service_endpoint
        if not image_service_endpoint:
            LOG.error("image service endpoint not found!")
            return webob.exc.HTTPNotFound()
        try:
            image = self.http.post(image_service_endpoint, \
				  headers={'Content-Type':'application/json'}, \
				  data=json.dumps(body))
        except exceptions.ConnectionError as ex:
            LOG.error("Connect to remote server Error %s" % ex)
            return webob.exc.HTTPInternalServerError()
        except exceptions.ConnectTimeout as ex:
            LOG.error("Connect to remote server Timeout. %s " % ex)
            return webob.exc.HTTPRequestTimeout()
        except exceptions.MissingSchema as ex:
            LOG.error("The URL schema (e.g. http or https) is missing. %s" %
                      ex)
            return webob.exc.HTTPBadRequest()
        except exceptions.InvalidSchema as ex:
            LOG.error("The URL schema is invalid. %s" % ex)
            return webob.exc.HTTPBadRequest()

        return ResponseObject(image.json())

    def delete(self, request, id):
        """
        Delete image from db and registry.
        This method contains the following three steps:
           1. delete db entry
           2. delete image from private image registry
           3. delete local image
        """
        image_instance = self.db.get_image(id)
        if not image_instance:
            LOG.warning("no such image %s" % id)
            return webob.exc.HTTPNotFound()
        """Delete image from database"""
        self.db.delete_image(id)
        """Delete image from image registry"""
        image_service_endpoint = CONF.image_service_endpoint
        if not image_service_endpoint:
            LOG.error("no image service endpoint found!")
            return webob.exc.HTTPNotFound()

        if not image_service_endpoint.startswith("http://"):
            image_service_endpoint += "http://"

        try:
            response = self.http.delete("%s/%s" % \
			(image_service_endpoint,id))
        except ConnectionError, err:
            LOG.error(err)
            return webob.exc.HTTPInternalServerError()

        return Response(response.status_code)

    def update(self, request, body):
        """Updated image information"""
        return NotImplementedError()

    def edit(self, request, id):
        """
        Edit image online.
        This method not used any more.
        """
        image_service_endpoint = CONF.image_service_endpoint
        if not image_service_endpoint:
            LOG.error("no image service endpoint found!")
            return webob.exc.HTTPNotFound()
        if not image_service_endpoint.startswith("http://"):
            image_service_endpoint += "http://"
        try:
            response = self.http.get("%s/%s/edit" %
                                     (image_service_endpoint, id))
        except:
            raise
        return ResponseObject(response.json())

    def destroy(self, request, id):
        """Destroy temporary containers for image online edit."""
        image_service_endpoint = CONF.image_service_endpoint
        if not image_service_endpoint:
            LOG.error("no image service endpoint found!")
            return webob.exc.HTTPNotFound()
        if not image_service_endpoint.startswith("http://"):
            image_service_endpoint += "http://"
        try:
            response = self.http.post("%s/%s/destroy" %
                                      (image_service_endpoint, id))
        except:
            raise
        return ResponseObject(response.json())

    def commit(self, request):
        """Commit container to a New image."""
        repo = request.GET.pop('repo')
        tag = request.GET.pop('tag')
        ctn = request.GET.pop('ctn')
        id = request.GET.pop('id')
        project_id = request.GET.pop('proj_id')

        limit = QUOTAS.images or _IMAGE_LIMIT
        query = self.db.get_images(project_id)
        if len(query) >= limit:
            LOG.error("images limit exceed,can not created anymore...")
            return webob.exc.HTTPMethodNotAllowed()

        image_service_endpoint = CONF.image_service_endpoint
        if not image_service_endpoint:
            LOG.error("no image service endpoint found!")
            return webob.exc.HTTPNotFound()
        if not image_service_endpoint.startswith("http://"):
            image_service_endpoint += "http://"
        try:
            data = {
                "repository": repo,
                "tag": tag,
                "container_id": ctn,
                "id": id,
                "project_id": project_id
            }
            response = self.http.post(
                "%s/commit" % image_service_endpoint,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data))
        except:
            raise
        return ResponseObject(response.json())

    def conflict(self, request):
        """
        This method is used for conflict resolve
        """
        _id = request.environ['wsgiorg.routing_args'][1]['image_id']
        ctn_info = self.db.get_containers_by_image(_id)
        ctn_list = []
        for item in ctn_info.fetchall():
            ctn_name = item[2]
            owner = item[10]
            ctn = {"Name": ctn_name, "Owner": owner, }
            ctn_list.append(ctn)
        LOG.debug(ctn_list)
        return ctn_list

    def baseimage(self, request):
        """
        This method used for getting the baseimage
        """
        base_image_list = []
        image_instances = self.db.get_base_images()
        for instance in image_instances:
            image = {
                "id": instance.id,
                "repository": instance.repository,
                "tag": instance.tag
            }
            base_image_list.append(image)
        return ResponseObject(base_image_list)


def create_resource():
    return wsgi.Resource(Controller())
