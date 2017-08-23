import os

import falcon

from .images import ImageCollection, ImageItem, ImageStore

def create_app(image_store):
    api = falcon.API()
    api.add_route('/images', ImageCollection(image_store))
    api.add_route('/images/{name}', ImageItem(image_store))
    return api

def get_app():
    storage_path = os.environ.get('LOOK_STORAGE_PATH', './images')
    image_store = ImageStore(storage_path)
    return create_app(image_store=image_store)
