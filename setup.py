#!/usr/bin/env python

from setuptools import setup

setup(name='nae',
      version='1.0',
      description='app engine',
      author='nmg',
      author_email='minguon@jumei.com',
      url='https://git.oschina.net/nmg/nae.git',
      packages=['nae',
                'nae.common',
                'nae.common.rpc',
                'nae.api',
                'nae.container',
                'nae.image',
                'nae.db',
                'nae.scheduler',
                'nae.network',
                'nae.web',
                'nae.web.controller',
                'nae.web.template', ],
      package_data={'nae.web.template': ['*.html']},
      scripts=['bin/nae-api', 'bin/nae-container', 'bin/nae-image',
               'bin/nae-web'],
      data_files=[('/etc/nae', ['etc/nae.conf',
                                'etc/api-paste.ini', ])])
