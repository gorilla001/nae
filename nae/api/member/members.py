from nae import wsgi
from nae import db

class MemberController(object):
    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        users=[]
        project_id = request.GET.get('project_id')
        rs = self.db_api.get_users(project_id=project_id)
        for item in rs.fetchall():
            user={
                'Id':item[0],
                'UserID':item[1],
                'Email':item[2],
                'RoleID':item[5],
                'Created':item[6],
                }
            users.append(user)

        return result_json

    def show(self,request):
        user_id=request.environ['wsgiorg.routing_args'][1]['id']
	proj_id=request.GET.get('project_id')
	_user_info=self.db_api.get_user(user_id,proj_id)	
	user_info=_user_info.fetchone()	
	if user_info is not None:
	    user = {
		"UserID":user_info[1],
		"Email":user_info[2],
		"RoleID":user_info[5],
	    }
            return user 
	return {}

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
        user_id=request.json.pop('user_name')
        email=request.json.pop('user_email')
        role_id=request.json.pop('role_id')
        project_id=request.json.pop('project_id')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_user(
                user_id = user_id,
                user_email = email,
                role_id = role_id,
                project_id = project_id,
                created = created)
        
        result_json = {"status":200}
        return result_json

    def delete(self,request):
        user_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_user(user_id)
        result='{"status":200}'
        return result

def create_resource():
    return wsgi.Resource(MemberController())
