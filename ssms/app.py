import falcon

from decouple import config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ssms.util.storage import SimpleBaseStore

import logging

DEBUG = config('DEBUG', cast=bool, default=False)

# set the storege module
storage_path = config('STORAGE_PATH', './images')
storage = SimpleBaseStore(storage_path)

# set the db connection
engine = create_engine(config('DATABASE_URI', None), echo=False)
Session = sessionmaker(bind=engine)


def route_version(version, route):
    return '/' + version + route


def set_routes(api):
    from ssms.resources import users, ingredients

    _versions = ['v1', ]
    api.add_route(route_version(_versions[0], '/admins'), users.AdminListResource())
    api.add_route(route_version(_versions[0], '/clients'), users.ClientListResource())
    api.add_route(route_version(_versions[0], '/ingredients'), ingredients.IngredientListResource())
    api.add_route(route_version(_versions[0], '/ingredients/{ingredient_id}'), ingredients.IngredientDetailResorce())


def configure_logging():
    _default_logging_format = '[%(asctime)s][%(name)s]: %(message)s'
    if DEBUG:
        logging.basicConfig(level=config('LOGGING_LEVEL', cast=int, default=logging.ERROR),
                            filename='./logging.log',
                            filemode='w',
                            format=config('LOGGING_FORMAT', default=_default_logging_format))
    else:
        logging.basicConfig(level=config('LOGGING_LEVEL', cast=int, default=logging.ERROR),
                            format=config('LOGGING_FORMAT', default=_default_logging_format))


def register_middleware():
    from ssms.middleware import NonBlockingAuthentication, LoggerMiddleware

    return [
        NonBlockingAuthentication(),
        LoggerMiddleware(logging.getLogger(__name__)),
    ]


def create_app():
    # create the app
    api = falcon.API(middleware=register_middleware())

    # set all project routes
    set_routes(api)

    configure_logging()

    return api


def get_app():
    return create_app()
