#!/usr/bin/env python
# This file is used for quotas configration.

DEFAULT_CONTAINER_LIMIT=10
DEFAULT_IMAGE_LIMIT=10

class Quotas(object):
    quotas = {
	'container_limit': DEFAULT_CONTAINER_LIMIT,
	'image_limit': DEFAULT_IMAGE_LIMIT,
    }

    @property
    def images(self):
        return self.quotas.get('image_limit')
    
    @property
    def containers(self):
        return self.quotas.get('container_limit')
 
