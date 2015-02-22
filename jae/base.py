"""Base Class"""

import eventlet
from jsonschema import validate

from jae import db
class Base(object):
    def __init__(self):
	self.db = db.API()
        self.validator = validate

    def run_task(func,*args):
        """Generate a greenthread to run the `func` with the `args`"""
        eventlet.spawn_n(func,*args)
