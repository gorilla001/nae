from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import text

Model = declarative_base()


class BaseModel(Model):
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    def save(self, session):
        session.add(self)
        session.flush()

    def update(self, values):
        for k, v in values.iteritems():
            setattr(self, k, v)


class ProjectUserAssociation(BaseModel):
    __tablename__ = 'project_user_association'
    project_id = Column(String(32),
                        ForeignKey('projects.id',
                                   ondelete='CASCADE'),
                        primary_key=True)
    user_id = Column(String(32),
                     ForeignKey('users.id',
                                ondelete='CASCADE'),
                     primary_key=True)


class Project(BaseModel):
    __tablename__ = 'projects'

    id = Column(String(32), primary_key=True)
    name = Column(String(50))
    desc = Column(String(300), default='')
    created = Column(DateTime, default=func.now())

    users = relationship("User",
                         secondary="project_user_association",
                         lazy="joined",
                         collection_class=set,
                         cascade="all,delete-orphan",
                         single_parent=True)


class Image(BaseModel):
    __tablename__ = 'images'

    id = Column(String(32), primary_key=True)
    uuid = Column(String(64))
    name = Column(String(50))
    tag = Column(String(50))
    desc = Column(String(300))
    project_id = Column(String(32),
                        ForeignKey('projects.id',
                                   ondelete='CASCADE'))
    project = relationship("Project",
                           backref=backref('images',
                                           lazy="joined",
                                           uselist=True,
                                           cascade='delete,all'))
    repos = Column(String(300))
    branch = Column(String(150))
    created = Column(DateTime, default=func.now())
    user_id = Column(String(32))
    status = Column(String(100))


class Container(BaseModel):

    __tablename__ = 'containers'

    id = Column(String(32), primary_key=True)
    uuid = Column(String(64))
    name = Column(String(50))
    env = Column(String(30))
    project_id = Column(String(32),
                        ForeignKey('projects.id',
                                   ondelete='CASCADE'))
    project = relationship("Project",
                           backref=backref('containers',
                                           lazy="joined",
                                           uselist=True,
                                           cascade='delete,all'))
    repos = Column(String(300))
    branch = Column(String(300))
    image_id = Column(String(32))
    created = Column(DateTime, default=func.now())
    user_id = Column(String(30))
    host_id = Column(String(32))
    fixed_ip = Column(String(32))
    status = Column(String(100))


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(String(32), primary_key=True)
    """NOTE(nmg):name can't be unique cause one user maybe belong to multiple project.
    name = Column(String(60),unique=True,nullable=False)"""
    name = Column(String(60), nullable=False)
    email = Column(String(150))
    role_id = Column(Integer)
    created = Column(DateTime, default=func.now())

    projects = relationship(Project,
                            secondary="project_user_association",
                            lazy="joined",
                            collection_class=set,
                            cascade="all,delete-orphan",
                            single_parent=True)


class Repos(BaseModel):
    __tablename__ = 'repos'

    id = Column(String(32), primary_key=True)
    repo_path = Column(String(300))
    project_id = Column(String(32),
                        ForeignKey('projects.id',
                                   ondelete='CASCADE'))
    project = relationship("Project",
                           backref=backref('repos',
                                           lazy='joined',
                                           uselist=True,
                                           cascade='delete,all'))

    created = Column(DateTime, default=func.now())


class Network(BaseModel):
    __tablename__ = 'networks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String(64))
    fixed_ip = Column(String(32))
    created = Column(DateTime, default=func.now())


"""not used anymore.
class Network(BaseModel):
    __tablename__ = 'networks'

    id = Column(Integer,primary_key=True,autoincrement=True)
    public_host = Column(String(100))
    public_port = Column(String(30))
    private_host = Column(String(100))
    private_port = Column(String(30))
    container_id = Column(String(32))
    created = Column(DateTime, default=func.now())
"""


class Host(BaseModel):
    __tablename__ = 'hosts'

    id = Column(String(32), primary_key=True)
    host = Column(String(20))
    port = Column(Integer)
    zone = Column(String(10))


class BaseImage(BaseModel):
    __tablename__ = 'baseimages'
    id = Column(String(32), primary_key=True)
    uuid = Column(String(64))
    repository = Column(String(50))
    tag = Column(String(50))
    desc = Column(String(300), default='base image')
    created = Column(DateTime, default=func.now())
