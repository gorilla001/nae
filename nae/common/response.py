from webob import Response


class Response(Response):
    def __init__(self,status_code=200):
	super(Response,self).__init__()		
	self.status_code = status_code 
	self.json = {"status":self.status_code}
