import wsgi

class RepoController(object):

    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        repos=[]
        project_id = request.GET.get('project_id')
        rs = self.db_api.get_repos(project_id=project_id)
        for item in rs.fetchall():
            repo={
                'Id':item[0],
                'Content':item[1],
                'Created':item[3],
                }
            repos.append(repo)
        return repos 

    def create(self,request):
        project_id=request.json.pop('project_id')
        repo_path=request.json.pop('repo_path')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_repo(
                project_id = project_id,
                repo_path= repo_path,
                created = created,
        )
        ret = {"status":200}
        return ret

    def delete(self,request):
        repo_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_repo(hg_id)
        result='{"status":200}'
        return result

def create_resource():
    return wsgi.Resource(RepoController())

