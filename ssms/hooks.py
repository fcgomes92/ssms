import falcon

from ssms.models import UsersEnum, Admin, Client, User, Ingredient, Order, Product


def require_auth(req, resp, resource, params):
    if not req.auth:
        raise falcon.HTTPError(falcon.HTTP_403)


def require_token_auth(req, resp, resource, params):
    auth_type = getattr(req, 'auth_type', None)
    token = getattr(req, 'token', None)
    user = getattr(req, 'user', None)
    if auth_type != 'token' or not token or not user:
        raise falcon.HTTPError(falcon.HTTP_403)


def require_admin(req, resp, resource, params):
    if req.user.user_type != UsersEnum.admin:
        raise falcon.HTTPError(falcon.HTTP_403)


def require_user(req, resp, resource, params):
    if not req.user:
        raise falcon.HTTPError(falcon.HTTP_403)


def get_client(req, resp, resource, params):
    client_id = params.get('client_id', None)
    if not client_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    client = Client.get_by_id(client_id)

    if not client:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['client'] = client


def get_ingredient(req, resp, resource, params):
    ingredient_id = params.get('ingredient_id', None)
    if not ingredient_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    ingredient = Ingredient.get_by_id(ingredient_id)

    if not ingredient:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['ingredient'] = ingredient


def get_product(req, resp, resource, params):
    product_id = params.get('product_id', None)
    if not product_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    product = Product.get_by_id(product_id)

    if not product:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['product'] = product


def get_order(req, resp, resource, params):
    order_id = params.get('order_id', None)
    if not order_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    order = Order.get_by_id(order_id)

    if not order:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['order'] = order
