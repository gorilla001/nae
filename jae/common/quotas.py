class Quotas(object):
    quotas = {
	'container_limit':10000,
	'image_limit':10000,
    }
    @property
    def images(self):
        return self.quotas.get('image_limit')
    
    @property
    def containers(self):
        return self.quotas.get('container_limit')
 
