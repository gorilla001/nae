import sqlalchemy
from jae.common import cfg
from jae.common.cfg import Bool, Int

CONF=cfg.CONF


_ENGINE=None
_MAKER=None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        connection = CONF.db_connection 
        url = sqlalchemy.engine.url.make_url(connection)

        if CONF.sql_show:
	    echo = Bool(CONF.echo)
        else:
	    echo = False

	if CONF.pool_size:
	    pool_size = Int(CONF.pool_size)
	else:
	    pool_size = 100
	
	if CONF.pool_recycle:
	    pool_recycle = Int(CONF.pool_recycle)
	else:
	    pool_recycle = 3600

	engine_args = {
	    "echo":echo,
	    "convert_unicode":True,
	    "pool_size":pool_size,
	    "pool_recycle":pool_recycle,
	}
	_ENGINE = sqlalchemy.create_engine(url,**engine_args)

    return _ENGINE


def get_session(autocommit=True,expire_on_commit=False):
    global _MAKER
    if _MAKER is None:
        _MAKER=get_maker(engine=get_engine())     

    return _MAKER()

def get_maker(engine):
    """change expire_on_commit=False to expire_on_commit=True"""
    maker= sqlalchemy.orm.sessionmaker(bind=engine,
					  autocommit=True,
					  expire_on_commit=True)

    return maker 
