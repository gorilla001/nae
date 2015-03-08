import sqlalchemy
from nae.common import cfg
from nae.common.cfg import Bool, Int

CONF=cfg.CONF


_ENGINE=None
_MAKER=None


DEFAULT_POOL_SIZE = 100
DEFAULT_POOL_RECYCLE = 3600

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        connection = CONF.db_connection 
        url = sqlalchemy.engine.url.make_url(connection)

        echo = False
        if CONF.sql_show:
	    echo = Bool(CONF.echo)

        pool_size = DEFAULT_POOL_SIZE 
	if CONF.pool_size:
	    pool_size = Int(CONF.pool_size)
	
        poll_recycle = DEFAULT_POOL_RECYCLE
	if CONF.pool_recycle:
	    pool_recycle = Int(CONF.pool_recycle)

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
