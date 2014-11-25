from  session import get_session
import models


def model_query(model,filed_name,value):
    model = model
    session = get_session()
    with session.begin():
        query = session.query(model).filter_by(filed_name = value)

    return query

### image api ###

def add_image(values):
    session = get_session()
    with session.begin():
	model=models.Image()
	model.update(values)
	model.save(session=session)	

def get_images(project_id):
    model = models.Image
    query = model_query(model,'ProjectID',project_id)

    return query.all()

def get_image(id):
    model = models.Image
    query = model_query(model,'ID',id)

    return query.first()

def update_image(id,img_id,size,status):
    model=models.Image 
    query=model_query(model,'ID',id)

    return query.update({
		'ImageId':img_id,
		'ImageSize':size,
		'Status':status})
    


def delete_image(img_id):
    model = models.Image
    query = model_query(model,'ID',img_id)

    return query.delete() 


### cotainer api ###

def add_container(values):
    session = get_session()
    with session.begin():
        model=models.Container()
        model.update(values)
        model.save(session=session)

def get_containers(project_id):
    model=models.Container
    query = model_query(model,'ProjectID',project_id)

    return query.all()

def get_container(id):
    model=models.Container
    query = model_query(model,'ID',id)

    return query.first()

def delete_container(id):
    model=models.Container
    query = model_query(model,'ID',id)

    return query.delete()

def update_container_id_and_status(id,ctn_id,status):
    model=models.Container
    query=model_query(model,'Id',id)
 
    return query.update({
		'ContainerID':ctn_id,
		'Status':status
		})

def update_container_status(id,status):
    model=models.Container
    query=model_query(model,'Id',id)

    return query.update({
		'Status':status
		})
 
def get_container_status(id):
    model=models.Container
    query=model_query(model,'Id',id)

    return query.first()

### project api ###

def add_project(values):
    session = get_session()
    with session.begin():
        model=models.Container()
        model.update(values)
        model.save(session=session)

def get_projects():
    model = models.Project
    query=model_query(model) 
    return query

def get_project(project_id):
    model=models.Project
    query=model_query(model,'ID',project_id)

    return query.first()

def delete_project():
    model=models.Project
    query = model_query(model,'ID',id)

    return query.delete()

def update_project():
    pass
### user api ###

def add_user(values):
    session = get_session()
    with session.begin():
        model=models.User()
        model.update(values)
        model.save(session=session)

def delete_user(id):
    model=models.User
    query = model_query(model,'ID',id)

    return query.delete()

### repo api ###

def add_repo(values):
    session = get_session()
    with session.begin():
        model=models.Repo()
        model.update(values)
        model.save(session=session)
    
def get_repo(image_id):
    model=models.Repo
    query=model_query(model,'ImageID',image_id)

    return query.first()

def get_repos(project_id):
    model=models.Repo
    query=model_query(model,'ProjectID',project_id)

    return query.all()

def delete_repo(id):
    model=models.Repo
    query=model_query(model,'Id',id)

    return query.delete()

### network api ###

def add_network(values):
    session=get_session()
    with session.begin():
        model=models.NetWork()
        model.update(values)
        model.save(session=session)

def get_network(ctn_id):
    model=models.NetWork
    query=model_query(model,'ContainerID',ctn_id)
    
    return query.all()
