from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship,backref
from sqlalchemy.sql import text

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
   
    id = Column(String(32),primary_key=True)
    name = Column(String(50))
    desc = Column(String(300),default='')
    created = Column(DateTime, default=func.now())

class Image(BaseModel,JaeBase):
    __tablename__ = 'images'
    
    id = Column(String(32),primary_key=True)
    prefix = Column(String(30))
    name = Column(String(50)) 
    tag = Column(String(50)) 
    size = Column(String(50))
    desc = Column(String(300))
    project_id= Column(String(32),ForeignKey('projects.id'),nullable=True)
    project = relationship('Project',cascade="delete")
    repos = Column(String(300))
    branch = Column(String(150))
    created = Column(DateTime, default=func.now())
    user_id = Column(String(30))
    status = Column(String(100))

class Container(BaseModel,JaeBase):
    __tablename__ = 'containers'
 
    id = Column(String(32),primary_key=True)
    prefix = Column(String(30))
    name = Column(String(50))
    env = Column(String(30))
    project_id= Column(String(32),ForeignKey('projects.id'),nullable=True)
    project = relationship('Project',cascade="delete")
    repos= Column(String(300))
    branch= Column(String(300))
    image_id = Column(String(32),ForeignKey('images.id'),nullable=True)
    created = Column(DateTime, default=func.now())
    user_id= Column(String(30))
    status = Column(String(100))

class User(BaseModel,JaeBase):
    __tablename__ = 'users'

    id = Column(String(32),primary_key=True)
    name = Column(String(60))
    email = Column(String(150))
    role_id = Column(Integer)
    project_id= Column(String(32),ForeignKey('projects.id',ondelete="CASCADE",onupdate='CASCADE'))
    created = Column(DateTime, default=func.now())

class Repos(BaseModel,JaeBase):
    __tablename__ = 'repos'

    id = Column(String(32),primary_key=True)
    repo_path = Column(String(300))
    project_id= Column(String(32),ForeignKey('projects.id'),nullable=True)
    project = relationship('Project',cascade="delete")
    created = Column(DateTime, default=func.now())

class Network(BaseModel,JaeBase):
    __tablename__ = 'networks'

    id = Column(Integer,primary_key=True,autoincrement=True)
    public_host = Column(String(100))
    public_port = Column(String(30))
    private_host = Column(String(100))
    private_port = Column(String(30))
    container_id = Column(String(32),ForeignKey('containers.id'),nullable=True)
    created = Column(DateTime, default=func.now())
