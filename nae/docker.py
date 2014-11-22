import requests

class API(object):
    def __init__(self):
        self.url = "http://{}:{}".format(config.docker_host,config.docker_port) 
        self.headers={'Content-Type':'application/json'}

    def create_container(name,data):
        _url = "{}/containers/create?name={}".format(self.url,name)
        return request.post(_url,data=data)

    def start_container(self,id,data):
        _url="{}/containers/{}/start".format(self.url,id)
        return request.post(_url,data=data) 

    def stop_container(self,id):
        _url="{}/containers/{}/stop?t=10".format(self.url,id)
	return requests.post(_url)	

    def inspect_container(self,id):
	_url="{}/containers/{}/json".format(self.url,id)
	return requests.get(_url) 

    def delete_container(self,id,v):
        _url="{}/containers/{}?v={}".format(self.url,ctn_id,v)
	return requests.delete(_url)
    
    def destroy_container(self,name):
        self.stop_container(name)
        self.delete_container(name,1)
