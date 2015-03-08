import webob

class ShowVersion:
    def __init__(self,version):	
        self.version = version

    @webob.dec.wsgify
    def __call__(self,req):	
	resp=webob.Response()
	version = {"version":"{}".format(self.version)}
	resp.json=version
	return resp

    @classmethod
    def factory(cls,global_conf,**local_conf):
	return ShowVersion(local_conf['version'])
