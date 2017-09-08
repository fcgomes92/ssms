import falcon


def require_auth(req, resp, resource, params):
    if not req.auth:
        raise falcon.HTTPError(falcon.HTTP_403)


def require_admin(req, resp, resource, params):
    if req.user.type != 'admin':
        raise falcon.HTTPError(falcon.HTTP_403)
