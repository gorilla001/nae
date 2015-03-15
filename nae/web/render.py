from nae.common import cfg
import os
import tempita
import webob.response

CONF=cfg.CONF

def render(template, **vars):
    template_file = os.path.join(os.path.dirname(__file__),"template",template)
    template = tempita.HTMLTemplate.from_filename(template_file)
    response = template.substitute(vars) 
    return webob.response.Response(body=response,content_type='text/html')
