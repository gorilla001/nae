class Quotas(object):
    quotas = {
	'container_limit':12,
	'image_limit':12,
    }
    @property
    def images(self):
        return self.quotas.get('image_limit')
    
    @property
    def containers(self):
        return self.quotas.get('container_limit')
 
