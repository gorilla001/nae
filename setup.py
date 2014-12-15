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
		'nae.api',
		'nae.container',
		'nae.image',
		'nae.db',
		'nae.scheduler',
		'nae.network',
	       ],

      scripts=['bin/nae'],

      data_files=[('/etc/nae',['etc/nae.conf',
			       'etc/api-paste.ini',
			      ]
		 )]
)
