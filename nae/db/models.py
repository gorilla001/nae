from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship,backref
from sqlalchemy.sql import text

Model = declarative_base()

class BaseModel(Model):
    __abstract__ = True
    __table_args__ = {
	'mysql_engine': 'InnoDB',
	'mysql_charset': 'utf8'
    }
    def save(self,session):
	session.add(self)	
	session.flush()

    def update(self,values):
	for k,v in values.iteritems():
	    setattr(self,k,v)

class Project(BaseModel):
    __tablename__ = 'projects'
   
    id = Column(String(32),primary_key=True)
    name = Column(String(50))
    desc = Column(String(300),default='')
    created = Column(DateTime, default=func.now())


class Image(BaseModel):
    __tablename__ = 'images'
    
    id = Column(String(32),primary_key=True)
    uuid = Column(String(64))
    name = Column(String(50)) 
    tag = Column(String(50)) 
    desc = Column(String(300))
    project_id= Column(String(32))
    repos = Column(String(300))
    branch = Column(String(150))
    created = Column(DateTime, default=func.now())
    user_id= Column(String(32))
    status = Column(String(100))

class Container(BaseModel):

    __tablename__ = 'containers'
 
    id = Column(String(32),primary_key=True)
    uuid = Column(String(64))
    name = Column(String(50))
    env = Column(String(30))
    project_id= Column(String(32))
    repos= Column(String(300))
    branch= Column(String(300))
    image_id = Column(String(32))
    created = Column(DateTime, default=func.now())
    user_id= Column(String(30))
    status = Column(String(100))

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(String(32),primary_key=True)
    name = Column(String(60))
    email = Column(String(150))
    role_id = Column(Integer)
    project_id= Column(String(32))
    created = Column(DateTime, default=func.now())

class Repos(BaseModel):
    __tablename__ = 'repos'

    id = Column(String(32),primary_key=True)
    repo_path = Column(String(300))
    project_id= Column(String(32))
    created = Column(DateTime, default=func.now())

class Network(BaseModel):
    __tablename__ = 'networks'

    id = Column(Integer,primary_key=True,autoincrement=True)
    public_host = Column(String(100))
    public_port = Column(String(30))
    private_host = Column(String(100))
    private_port = Column(String(30))
    container_id = Column(String(32))
    created = Column(DateTime, default=func.now())
