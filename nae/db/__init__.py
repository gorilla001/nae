import sys
import os


class API(object):
    def __init__(self):
        self.__backend = None

    def __get_backend(self):
        if not self.__backend:
            self.__backend = __import__('nae.db.api', None, None, '*')
        return self.__backend

    def __getattr__(self, key):
        backend = self.__get_backend()
        return getattr(backend, key)
