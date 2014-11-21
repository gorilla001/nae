import webob
import logging
from nae import wsgi
from nae import image
from nae import db


LOG=logging.getLogger('eventlet.wsgi.server')

class ImageController(object):
    def __init__(self):
        self.image_api=image.API()
        self.db_api=db.API()

    def index(self,request):
        images=[]
        project_id=request.GET.pop('project_id')
        rs = self.db_api.get_images(project_id=project_id)
        for item in rs.fetchall():
            project_info = self.db_api.show_project(project_id=item[6]) 
            project_name = project_info.fetchone()[1]
            image={
                'ID':item[0],
                'ImageId':item[1],
                'ImageName':item[2],
		'ImageTag':item[3],
                'ImageSize':item[4],
                'ImageDesc':item[5],
                'ImageProject':project_name,
                'CreatedTime':item[9],
                'CreatedBy':item[10],
                'Status' : item[11],
                }
            images.append(image)
        return images 

    def show(self,request):
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        result = self.db_api.get_image(image_id)
        image_info=result.fetchone()
	if image_info is None:
		LOG.debug("image is None")	
		return None
        image={
                'ImageID':image_info[1],
                'ImageName':image_info[2],
                'ImageSize':image_info[3],
                'ImageDesc':image_info[4],
                'RepoPath':image_info[7],
		'Branch':image_info[8],
        }
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

    def create(self,request):
        image_name=request.json.pop('image_name')
        image_desc=request.json.pop('image_desc')
        project_id=request.json.pop('project_id')
        repo_path=request.json.pop('repo_path')
	repo_branch=request.json.pop('repo_branch')
        user_name=request.json.pop('user_name')
        created_time = utils.human_readable_time(time.time())

	img_limit = quotas.get_quotas().get('image_limit')	
	img_count = self.db_api.get_images(project_id)
	img_count = len(img_count.fetchall())	
	if img_count == img_limit :
	    LOG.info("images limit exceed,can not created anymore...")
	    return

	id=self.db_api.add_image(
                                  name=image_name,
				  tag="latest",
                                  desc=image_desc,
                                  project_id=project_id,
                                  repo = repo_path,
				  branch = repo_branch, 
                                  created= created_time,
                                  owner=user_name,
                                  status = 'building'
	)
        self.image_api.create_image_from_file(id,image_name,str(repo_path),str(repo_branch),user_name)
        result_json={}
        return result_json

    def delete(self,request):
        _image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        f_id=request.GET['force']
        image_info = self.db_api.get_image_by_id(_image_id).fetchone()
        image_id=image_info[1]
	self.db_api.update_image_status(
				  id=_image_id,
                                  status = "deleting")
        self.image_api.delete_image(_image_id,image_id,f_id)

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
