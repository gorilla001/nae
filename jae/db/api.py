from  session import get_session
import models
from sqlalchemy.orm import joinedload


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
	model=models.Image()
	model.update(values)
	model.save(session=session)	

def get_images(project_id):
    if project_id is None:
	return model_query(models.Image).all()
    return model_query(models.Image,
		       project_id=project_id).all()

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

#def update_container_prefix_and_status(id,prefix,status):
#    return model_query(models.Container,
#		       id=id).update({
#		              'prefix':prefix,
#		              'status':status})
#
#def update_container_status(id,status):
#    return model_query(models.Container
#		       id=id).update({
#		             'status':status})
# 
### project api ###

def add_project(values):
    session = get_session()
    with session.begin():
        model=models.Project()
        model.update(values)
        model.save(session=session)

def get_projects(user_id):
    if user_id is None:
	return model_query(models.Project).\
			   all()
    return model_query(models.Project,
		       user_id=user_id).\
                       all() 

def get_project(id):
    return model_query(models.Project,id=id).\
		       first()

def delete_project(id):
    return model_query(models.Project,id=id).delete()

def update_project():
    pass
### user api ###

def add_user(values):
    session = get_session()
    with session.begin():
        model=models.User()
        model.update(values)
        model.save(session=session)

def get_users(project_id):
    if project_id is None:
        return model_query(models.User).all()
    return model_query(models.User,
		       project_id=project_id).all()

def get_user(id):
    return model_query(models.User,
		       id=id).first()

def delete_user(id):
    return model_query(models.User,id=id).delete()

### repo api ###

def add_repo(values):
    session = get_session()
    with session.begin():
        model=models.Repos()
        model.update(values)
        model.save(session=session)
    
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
