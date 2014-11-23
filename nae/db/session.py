import sqlalchemy
from nae.common import cfg

CONF=cfg.CONF


_ENGINE=None
_MAKER=None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        connection = CONF.db_connection 
        url = sqlalchemy.engine.url.make_url(connection)

	engine_args = {
	    "echo":bool(CONF.sql_show),
	    "convert_unicode":bool(convert_unicode),
	    "pool_size":100,
	    "pool_recycle":3600,
	}
	_ENGINE = sqlalchemy.create_engine(url,**engine_args)

    return _ENGINE


def get_session(autocommit=True,expire_on_commit=False):
    global _MAKER
    if _MAKER is None:
        _MAKER=get_maker(engine=get_engine())     

    return _MAKER()

def get_maker(engine):
    maker= sqlalchemy.orm.sessionmaker(bind=engine,
					  autocommit=True,
					  expire_on_commit=False)

    return maker 
