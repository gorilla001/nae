

CONTAINER_DEFAULT_LIMIT=10
IMAGE_DEFAULT_LIMIT=10

class Quotas(object):
    quotas = {
	'container_limit': CONTAINER_DEFAULT_LIMIT,
	'image_limit': IMAGE_DEFAULT_LIMIT,
    }

    @property
    def images(self):
        return self.quotas.get('image_limit')
    
    @property
    def containers(self):
        return self.quotas.get('container_limit')
 
