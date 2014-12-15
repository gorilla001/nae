#!/usr/bin/env python

from setuptools import setup

setup(name='jae',
      version='1.0',
      description='app engine',
      author='nmg',
      author_email='minguon@jumei.com',
      url='https://git.oschina.net/nmg/nae.git',

      packages=['jae',
		'jae.common',
		'jae.api',
		'jae.api.container',
		'jae.api.image',
		'jae.container',
		'jae.container.api',
		'jae.image',
		'jae.image.api',
		'jae.db',
		'jae.scheduler',
		'jae.network',
	       ],

      scripts=['bin/jae-api',
	       'bin/jae-container',
	       'bin/jae-image'],

      data_files=[('/etc/jae',['etc/jae.conf',
			       'etc/api-paste.ini',
			      ]
		 )]
)
