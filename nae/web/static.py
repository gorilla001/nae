import webob
import os

class ServerStaticFiles:
    def __init__(self):	
        self.static_path = os.path.join(os.path.dirname(__file__),"static")  

    @webob.dec.wsgify
    def __call__(self,req):	
	resp=webob.Response()
	version = {"version":"{}".format(self.version)}
	resp.json=version
	return resp

    @classmethod
    def factory(cls,global_conf,**local_conf):
	return ServerStaticFiles() 
