from  session import get_session
import models
from sqlalchemy.orm import joinedload
from sqlalchemy import asc


def model_query(model,**kwargs):
    model = model
    session = get_session()
    with session.begin():
        query = session.query(model).filter_by(**kwargs)

    return query

### image api ###

def add_image(values):
    session = get_session()
    with session.begin():
	image_ref=models.Image()
	image_ref.update(values)
	image_ref.save(session=session)	

def get_images(project_id):
    if project_id is None:
	return model_query(models.Image).\
               order_by(asc(models.Image.created)).\
               all()
    return model_query(models.Image,
		       project_id=project_id).\
                      order_by(asc(models.Image.created)).all()

def get_image(id):
    return model_query(models.Image,id=id).first()

def update_image(id,**values):
    return model_query(models.Image,
		       id=id).update(values)

def delete_image(id):
    return model_query(models.Image,id=id).delete()

### cotainer api ###

def add_container(values):
    session = get_session()
    with session.begin():
        model=models.Container()
        model.update(values)
        model.save(session=session)

def get_containers(project_id=None,user_id=None):
    if project_id is None and user_id is None:
	return model_query(models.Container).all()
    if project_id is None:
	return model_query(models.Container,
			   user_id=user_id).all()
    if user_id is None:
	return model_query(models.Container,
			   project_id=project_id).all()
	
    return model_query(models.Container,
		       project_id=project_id,
		       user_id=user_id).all()

def get_containers_by_host(host_id):
    if not host_id:
	return []
    return model_query(models.Container,
		       host_id=host_id).all()

def get_container(id):
    return model_query(models.Container,
		       id=id).first()

def delete_container(id):
    return model_query(models.Container,
			id=id).delete()

def update_container(id,**value):
    return model_query(models.Container,id=id).update(value)


def add_project(values):
    session = get_session()
    with session.begin():
        model=models.Project()
        model.update(values)
        model.save(session=session)

def get_projects():
    return model_query(models.Project).\
                           order_by(models.Project.created).\
			   all()

def get_project(id):
#    return model_query(models.Project). \
#		       options(joinedload('users')). \
#		       filter_by(id=id).\
#		       first()
#
    return model_query(models.Project,id=id).first()

def delete_project(id):
    return model_query(models.Project,id=id).delete()

def update_project():
    pass
### user api ###

def add_user(values,project):
    session = get_session()
    with session.begin():
        user_ref=models.User()
        user_ref.update(values)
        user_ref.projects.add(project)
        user_ref.save(session=session)
    return user_ref

def get_users(project_id):
    if project_id is None:
        return model_query(models.User).all()
    return model_query(models.User,
		       project_id=project_id).all()

def get_user(name):
    return model_query(models.User,
		       name=name).first()

def delete_user(id):
    return model_query(models.User,
                       id=id).delete()

### repo api ###

def add_repo(values):
    session = get_session()
    with session.begin():
        repo_ref=models.Repos()
        repo_ref.update(values)
        repo_ref.save(session=session)
    
def get_repo(id):
    return model_query(models.Repos,id=id).first()

def get_repos(project_id):
    if project_id is None:
        return model_query(models.Repos).all()
    return model_query(models.Repos,
                       project_id=project_id).all()

def delete_repo(id):
    return model_query(models.Repos,id=id).delete()

### network api ###

def add_network(values):
    session=get_session()
    with session.begin():
        model=models.Network()
        model.update(values)
        model.save(session=session)

def get_network(id):
    return model_query(models.Network,
                       id=id).first() 

def get_networks(container_id):
    return model_query(models.Network,
                      container_id=container_id).all()


### host api ###

def get_hosts():
    return model_query(models.Host).all()

def get_host(host_id):
    return model_query(models.Host,
		       id=host_id).first()


### register host ###

def register(values):
    session = get_session()
    with session.begin():
        model = models.Host()
        model.update(values)
        model.save(session=session)

def register_update(id,**values):
    return model_query(models.Host,id=id).update(values)

### base images ###
def get_base_images():
    return model_query(models.BaseImage).all()

def get_base_image(image_id):
    return model_query(models.BaseImage,
                       id = image_id).first()
