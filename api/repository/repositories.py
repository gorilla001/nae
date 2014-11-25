import wsgi

class RepoController(object):

    def __init__(self):
        self.db_api=db.API()

    def index(self,request):
        repos=[]
        project_id = request.GET.get('project_id')
        rs = self.db_api.get_hgs(project_id=project_id)
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
        hg_addr=request.json.pop('hg_addr')
        created=utils.human_readable_time(time.time()) 
        self.db_api.add_hg(
                project_id = project_id,
                hg_addr = hg_addr,
                created = created,
        )
        result_json = {"status":200}
        return result_json

    def delete(self,request):
        hg_id=request.environ['wsgiorg.routing_args'][1]['id']
        self.db_api.delete_hg(hg_id)
        result='{"status":200}'
        return result

def create_resource():
    return wsgi.Resource(RepoController())

