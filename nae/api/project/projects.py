from nae import wsgi
from nae import db

class ProjectController(object):
    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        projects=[]
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
                projects.append(project)
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
                projects.append(project)
        return projects 

    def show(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        result = self.db_api.show_project(project_id=project_id)
        project_info = result.fetchone()
        project_name= project_info[1]
        project_desc = project_info[2]

        query=self.db_api.get_repos(project_id = project_id)
        repos=[]
        for item in query.fetchall():
            repo = item[1]
            repos.append(hg)
        project_repos = ' '.join(repos) 

	admins = []
	query = self.db_api.get_users_by_role(project_id,1)
	for item in query.fetchall():
	    admin=item[1]
	    admins.append(admin)	
	project_admin=' '.join(admins)

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
        project = {
                    "id" : project_id,
                    "name":project_name,
                    "desc":project_desc,
                    "admin":project_admin,
                    "members":project_members,
                    "hgs":project_hgs,
                    "imgs":project_imgs,
                    "created":project_created,
                    }
        return project 

    def inspect(self,request):
        image_id=request.environ['wsgiorg.routing_args'][1]['image_id']
        inspect = self.image_api.inspect_image(image_id)
        result={}
        if inspect.status_code == 200:
            result=inspect.json()   
        if inspect.status_code == 404:
            errors={"errors":"404 Not Found:no such image {}".format(image_id)}
            result=errors
        return result

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
        

    def delete(self,request):
        project_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_project(project_id)
        self.db_api.delete_containers(project_id)
        self.db_api.delete_images(project_id)
        self.db_api.delete_users(project_id)
        self.db_api.delete_hgs(project_id)

        return {"status":200}

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
        repo_list = str(project_hgs).split()
        self.db_api.delete_repos(project_id)
        for hg in hg_list:
            self.db_api.add_repo(
                    project_id = project_id,
                    repo_name = repo,
                    image_id = ''
                    )

        return {"status":"200"}

def create_resource():
    return wsgi.Resource(ProjectController()) 
