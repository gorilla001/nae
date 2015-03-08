class Host(object):
    def __init__(self,addr,port):
	pass

class WeightedHost(object):
    def __init__(self,id,weight,addr,port):
	self.id     = id
	self.weight = weight
	self.addr   = addr
	self.port   = port

    def __repr__(self):
	return repr((self.id,self.weight,self.addr,self.port))
