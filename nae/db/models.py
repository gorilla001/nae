from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

BaseModel = declarative_base()

class JaeBase(object):
    def save(self,session):
	session.add(self)	
	session.flush()
    def update(self,values):
	for k,v in values.iteritems():
	    setattr(self,k,v)

class Project(BaseModel,JaeBase):
    __tablename__ = 'projects'
   
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(50))
    desc = Column(String(300),default='')
    '''
    Hgs = Column(String(500))
    Imgs = Column(String(500),default='')
    Admin = Column(String(30))
    Members = Column(String(500),default='')
    '''
    created = Column(String(150)) 

class Image(BaseModel,JaeBase):
    __tablename__ = 'images'
    
    id = Column(Integer,primary_key=True,autoincrement=True)
    prefix = Column(String(30))
    name = Column(String(50)) 
    size = Column(String(50))
    desc = Column(String(300))
    project_id= Column(Integer,ForeignKey('projects.id'),nullable=True)
    project=relationship(Project)
			 
    repo = Column(String(300))
    branch = Column(String(150))
    created = Column(String(150))
    owner = Column(String(30))
    status = Column(String(100))

class Container(BaseModel,JaeBase):
    __tablename__ = 'containers'
 
    id = Column(Integer,primary_key=True,autoincrement=True)
    prefix = Column(String(30))
    name = Column(String(50))
    env = Column(String(30))
    project_id = Column(Integer)
    repos= Column(String(300))
    branch= Column(String(300))
    image = Column(String(300))
    network = Column(Integer,ForeignKey('networks.id'),nullable=True)
    created = Column(String(150))
    user_id= Column(String(30))
    status = Column(String(100))

class User(BaseModel,JaeBase):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(60))
    email = Column(String(150))
    role_id = Column(Integer)
    project_id = Column(Integer)
    created = Column(String(150)) 

class Repo(BaseModel,JaeBase):
    __tablename__ = 'repos'

    id = Column(Integer,primary_key=True,autoincrement=True)
    content = Column(String(300))
    project_id = Column(Integer)
    created = Column(String(150))

class Network(BaseModel,JaeBase):
    __tablename__ = 'networks'

    id = Column(Integer,primary_key=True,autoincrement=True)
    #ContainerID = Column(String(50))
    public_host = Column(String(100))
    public_port = Column(String(30))
    private_host = Column(String(100))
    private_port = Column(String(30))
