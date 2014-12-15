"""Base Class"""

from nae import db
class Base(object):
    def __init__(self):
	self.db = db.API()
