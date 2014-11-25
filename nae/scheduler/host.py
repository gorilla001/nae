class Host(object):
    def __init__(self,addr,port):
	pass
class WeightedHost(object):
    def __init__(self,weight,addr,port):
	self.weight = weight
	self.addr = addr
	self.port = port

    def __repr__(self):
	return repr((self.weight,self.addr,self.port))
