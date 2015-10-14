from nae.common import cfg
import os
#import tempita
from jinja2 import Environment, FileSystemLoader
import webob.response

CONF = cfg.CONF


def render(template_file, **vars):
    template_dir = os.path.join(os.path.dirname(__file__), "template")
    #template_file = os.path.join(template_dir,template)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    response = template.render(vars)
    #template = tempita.HTMLTemplate.from_filename(template_file)
    #response = template.substitute(vars)
    return webob.response.Response(body=response, content_type='text/html')
