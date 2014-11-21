#!/usr/bin/env python

from setuptools import setup

setup(name='nae',
      version='1.0',
      description='app engine',
      author='nmg',
      author_email='minguon@jumei.com',
      url='https://git.oschina.net/nmg/nae.git',

      packages=['nae',
		'nae.api',
		'nae.api.container',
		'nae.api.image',
		'nae.api.member',
		'nae.api.project',
		'nae.api.repository',
		'nae.container',
		'nae.image',
		'nae.db',
	       ],

      scripts=['bin/nae-api'],

      data_files=[('/etc/nae',['etc/nae.conf',
			       'etc/api-paste.ini',
			      ]
		 )]
)
