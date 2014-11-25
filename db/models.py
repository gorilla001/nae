from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

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
   
    ID = Column(Integer,primary_key=True,autoincrement=True)
    Name = Column(String(50))
    Desc = Column(String(300),default='')
    '''
    Hgs = Column(String(500))
    Imgs = Column(String(500),default='')
    Admin = Column(String(30))
    Members = Column(String(500),default='')
    '''
    Created = Column(String(150)) 

class Image(BaseModel,JaeBase):
    __tablename__ = 'images'
    
    ID = Column(Integer,primary_key=True,autoincrement=True)
    ImageID = Column(String(30))
    ImageName = Column(String(50)) 
    ImageSize = Column(String(50))
    ImageDesc = Column(String(300))
    ProjectID = Column(String(300))
    RepoPath = Column(String(300))
    Branch = Column(String(150))
    Created = Column(String(150))
    Owner = Column(String(30))
    Status = Column(String(100))

class Container(BaseModel,JaeBase):
    __tablename__ = 'containers'
 
    Id = Column(Integer,primary_key=True,autoincrement=True)
    ID = Column(String(50))
    Name = Column(String(50))
    Env = Column(String(30))
    Project = Column(Integer)
    Hgs = Column(String(300))
    Code = Column(String(300))
    Image = Column(String(300))
    '''
    AccessMethod = Column(String(500))
    '''
    Created = Column(String(150))
    Owner = Column(String(30))
    Status = Column(String(100))

class User(BaseModel,JaeBase):
    __tablename__ = 'users'

    Id = Column(Integer,primary_key=True,autoincrement=True)
    ID = Column(String(30))
    Email = Column(String(150))
    Name = Column(String(60))
    Project = Column(Integer)
    Role = Column(Integer)
    Created = Column(String(150)) 

class Repo(BaseModel,JaeBase):
    __tablename__ = 'repos'

    Id = Column(Integer,primary_key=True,autoincrement=True)
    Content = Column(String(300))
    Project = Column(Integer)
    Created = Column(String(150))

class NetWork(BaseModel,JaeBase):
    __tablename__ = 'network'

    Id = Column(Integer,primary_key=True,autoincrement=True)
    ContainerID = Column(String(50))
    PublicHost = Column(String(100))
    PublicPort = Column(String(30))
    PrivateHost = Column(String(100))
    PrivatePort = Column(String(30))
