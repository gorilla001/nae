import webob
import logging
from nae import wsgi
from nae import image
from nae import db
from nae.utils import isotime


LOG=logging.getLogger('eventlet.wsgi.server')

class ImageController(object):
    def __init__(self):
        self.image_api=image.API()
        self.db_api=db.API()

    def index(self,request):
        images=[]
        project_id=request.GET.get('project_id')
        query = self.db_api.get_images(project_id)
        if query is not None:
            for item in query:
                image={'id':item.prefix,
                       'name':item.name,
		       'tag':item.tag,
                       'size':item.size,
                       'desc':item.desc,
                       'project_id':item.project_id,
                       'created':isotime(item.created),
                       'user_id':item.user_id,
                       'status' : item.status}
                images.append(image)

        return images 

    def show(self,request,id):
	image = {}
        query = self.db_api.get_image(id)
	if query is not None:
            image = {'id' : query.prefix,
                     'name' : query.name,
		     'tag' : query.tag,
                     'size' : query.size,
                     'desc' : query.desc,
                     'project_id' : query.project_id,
                     'created' : isotime(query.created),
                     'user_id' : query.user_id,
                     'status' : query.status}

        return image 

    def inspect(self,request):
	image={}
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        result = self.image_api.inspect_image(image_id)
        if result.status_code == 200:
            image.update(result.json())   
        if result.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image_id)}
            image.update(result.json()) 
        return image 

    def create(self,request,body):
        name = body.get('name')
        desc = body.get('desc')
        project_id = body.get('project_id')
        repos = body.get('repos')
	branch = body.get('branch')
        user_id = body.get('user_id')

        """
	img_limit = quotas.get_quotas().get('image_limit')	
	img_count = self.db_api.get_images(project_id)
	img_count = len(img_count.fetchall())	
	if img_count == img_limit :
	    LOG.info("images limit exceed,can not created anymore...")
	    return
        """
	try:
	    self.db_api.add_image(dict(
                name=name,
	        tag="latest",
       	        desc=desc,
       	        project_id=project_id,
                repos = repos,
                branch = branch, 
                user_id = user_id,
                status = 'building'))
	except:
	    return {"status":500}
	"""
        self.image_api.create_image_from_file(id,image_name,str(repo_path),str(repo_branch),user_name)
	"""
        return {"status":200} 

    def delete(self,request,id):
	self.db_api.update_image(id=id,status="deleting")
 	"""	
        self.image_api.delete_image(_image_id,image_id,f_id)
	"""
	return {"status":200}

    def edit(self,request):
        _img_id=request.GET.pop('id')
        _img_info = self.db_api.get_image(_img_id).fetchone()
        img_id = _img_info[1]
	name = utils.random_str()
	port = utils.get_random_port()
	kwargs={
		"Image":img_id,
	    	}
	eventlet.spawn_n(self.image_api.edit,kwargs,name,port)
	
	return {
		"url":"http://{}:{}".format(config.docker_host,port),
		"name":name,
		}

    def commit(self,request):
	repo = request.GET.pop('repo')
	tag = request.GET.pop('tag')
	ctn = request.GET.pop('ctn')
	id = request.GET.pop('id')
 	proj_id = request.GET.pop('proj_id')

	img_limit = quotas.get_quotas().get('image_limit')	
	img_count = self.db_api.get_images(proj_id)
	img_count = len(img_count.fetchall())	
	if img_count == img_limit :
	    LOG.info("images limit exceed,can not created anymore...")
	    return { "status":100 }

	self.image_api.commit(repo,tag,ctn,id)

    def conflict(self,request):
	_id=request.environ['wsgiorg.routing_args'][1]['image_id']
	ctn_info=self.db_api.get_containers_by_image(_id)
	ctn_list=[]
	for item in ctn_info.fetchall():
		ctn_name=item[2]
		owner=item[10]
		ctn = {
			"Name":ctn_name,
			"Owner":owner,
		}
		ctn_list.append(ctn)
	LOG.debug(ctn_list)
	return ctn_list

def create_resource():
    return wsgi.Resource(ImageController())
