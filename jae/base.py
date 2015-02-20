"""Base Class"""

from jsonschema import validate

from jae import db
class Base(object):
    def __init__(self):
	self.db = db.API()
        self.validator = validate
