import sqlalchemy

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        connection = "mysql://jaecpn:jaecpn@localhost/jaecpn"
        url = sqlalchemy.engine.url.make_url(connection)

	engine_args = {
	    "echo":False,
	    "convert_unicode":True,
	    "pool_size":100,
	    "pool_recycle":3600,
	}
	_ENGINE = sqlalchemy.create_engine(url,**engine_args)

	return _ENGINE


def get_session(autocommit=True,expire_on_commit=False):
    engine = get_engine() 
    session = sqlalchemy.orm.sessionmaker(bind=engine,
					  autocommit=True,
					  expire_on_commit=False)

    return session()
