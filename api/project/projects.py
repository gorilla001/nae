import wsgi

class ProjectController(object):
    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        result_json=[]
        user_id = request.GET.get('user_id')
        if user_id == 'admin':
            project_info = self.db_api.get_projects()
            for item in project_info.fetchall():
                project={
                    'ProjectId':item[0],
                    'ProjectName':item[1],
                    'ProjectDesc':item[2],
                    'ProjectHgs':'',
                    'ProjectImgs':'',
                    'ProjectAdmin':item[5],
                    'ProjectMembers':'',
                    'CreatedTime':item[7],
                }
                result_json.append(project)
        else:
            project_ids = utils.get_projects(user_id=user_id)
            for project_id in project_ids:
                project_info = utils.get_project_info(project_id) 
                project_id = project_id
                project={
                    'ProjectId':project_id,
                    'ProjectName':project_info[1],
                    'ProjectDesc':project_info[2],
                    'ProjectHgs':'',
                    'ProjectImgs':'',
                    'ProjectAdmin':project_info[5],
                    'ProjectMembers':'',
                    'CreatedTime':project_info[7],
                 }
                result_json.append(project)
        return result_json

    def show(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        result = self.db_api.show_project(project_id=project_id)
        project_info = result.fetchone()
        project_name= project_info[1]
        project_desc = project_info[2]
        hgs=self.db_api.get_hgs(project_id = project_id)
        hg_list=list()
        for _item in hgs.fetchall():
            hg = _item[1]
            hg_list.append(hg)
        project_hgs = ' '.join(hg_list) 

	_user_info = self.db_api.get_users_by_role(project_id,1)
	user_info=_user_info.fetchall()
	project_admin = []
	for item in user_info:
	    admin=item[1]
	    project_admin.append(admin)	
	project_admin=' '.join(project_admin)

        _members = self.db_api.get_users(project_id=project_id)
        project_members=list()
        for memb in _members.fetchall():
               project_members.append(memb[1]) 
        project_members=' '.join(project_members)
        project_created = project_info[7]
        result = self.db_api.get_images(project_id=project_id)
        project_imgs=[]
        for item in result.fetchall():
            img_name = item[2]
            project_imgs.append(img_name)
        project_imgs=' '.join(project_imgs)
        result_json={}
        result_json = {
                    "id" : project_id,
                    "name":project_name,
                    "desc":project_desc,
                    "admin":project_admin,
                    "members":project_members,
                    "hgs":project_hgs,
                    "imgs":project_imgs,
                    "created":project_created,
                    }
        return result_json

    def inspect(self,request):
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        result = self.image_api.inspect_image(image_id)
        result_json={}
        if result.status_code == 200:
            result_json=result.json()   
        if result.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image_id)}
            result_json=errors
        return result_json

    def create(self,request):
        project_name=request.json.pop('project_name')
        project_admin=request.json.pop('project_admin')
        project_desc=request.json.pop('project_desc')
        admin_email=request.json.pop('admin_email')
        created_time = utils.human_readable_time(time.time())

        project_id=self.db_api.add_project(
                #str(project_name),
                project_name,
                '',
                #str(project_admin),
                project_admin,
                '',
                #str(project_desc),
                project_desc,
                #str(created_time),
                created_time,
                )
        self.db_api.add_user(
            user_id = project_admin,
            user_name = '',
            user_email = admin_email,
            project_id = project_id,
            role_id = 1, # 0 for admin
            created = created_time,
        )
        result_json={"status":200}
        return result_json

    def delete(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_project(project_id)
        self.db_api.delete_containers(project_id)
        self.db_api.delete_images(project_id)
        self.db_api.delete_users(project_id)
        self.db_api.delete_hgs(project_id)
        result_json={}
        return result_json

    def update(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        project_name = request.GET['name']
        project_desc = request.GET['desc']
        project_members = request.GET['members']
        project_hgs = request.GET['hgs']
        self.db_api.update_project(
                project_id = project_id,
                project_name = project_name,
                project_desc = project_desc,
                project_members = '',
                project_hgs = '',
                )
        members_list = str(project_members).split()
        self.db_api.delete_users(project_id)
        for member in members_list:
            self.db_api.add_user(
                    project_id = project_id,
                    user_id = member,
                    user_name = '',
                    created = utils.human_readable_time(time.time()),

                )
        hg_list = str(project_hgs).split()
        self.db_api.delete_hgs(project_id)
        for hg in hg_list:
            self.db_api.add_hg(
                    project_id = project_id,
                    hg_name = hg,
                    image_id = ''
                    )

        return {"status":"200"}

def create_resource():
    return wsgi.Resource(ProjectController()) 
