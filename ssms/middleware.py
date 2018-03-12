import falcon

import base64

import jwt

from ssms.models import User


class NonBlockingAuthentication(object):
    @staticmethod
    def process_token(token):
        try:
            user = User.get_by_token(token)
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPError(falcon.HTTP_401, title='Expired Token')
        except jwt.DecodeError:
            raise falcon.HTTPError(falcon.HTTP_401, title='Reading token error')
        except Exception:
            raise falcon.HTTPError(falcon.HTTP_403, title='Token error')
        else:
            if user:
                return user, token
            else:
                raise falcon.HTTPError(falcon.HTTP_404)

    @staticmethod
    def process_basic(auth):
        email, password = base64.b64decode(auth).decode().split(':')

        user = User.get_by_email(email)

        if user:
            hashed_password, seed = User.hash_password(password, user.seed)
            if user.password == hashed_password:
                return user, None
            else:
                raise falcon.HTTPError(falcon.HTTP_403)
        else:
            raise falcon.HTTPError(falcon.HTTP_404)

    def process_sent_auth(self, _type, _auth_string):
        # the basic auth to get a token
        if _type.lower() == 'basic':
            user, token = self.process_basic(_auth_string.encode())
            return user, token, 'basic'

        # the token auth to handle all other auths and refresh token ones too
        if _type.lower() == 'token':
            user, token = self.process_token(_auth_string.encode())
            return user, token, 'token'

        raise falcon.HTTPError(falcon.HTTP_401)

    def process_url_auth(self, auth):
        if not auth:
            return None, None, None

        try:
            _type, _auth_string = auth.split('=', 1)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_401)
        else:
            return self.process_sent_auth(_type, _auth_string)

    def process_auth(self, auth):
        if not auth:
            return None, None, None

        # check the auth type (basic|token)
        try:
            _type, _auth_string = auth.split(' ')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_401)
        else:
            return self.process_sent_auth(_type, _auth_string)

    def process_request(self, req, resp, *args, **kwargs):
        """Process the request before routing it.

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.
        """

    def process_resource(self, req, resp, resource, params, *args, **kwargs):
        """Process the request after routing.

        Note:
            This method is only called when the request matches
            a route to a resource.

        Args:
            req: Request object that will be passed to the
                routed responder.
            resp: Response object that will be passed to the
                responder.
            resource: Resource object to which the request was
                routed.
            params: A dict-like object representing any additional
                params derived from the route's URI template fields,
                that will be passed to the resource's responder
                method as keyword arguments.
        """
        if req.query_string:
            user, token, auth_type = self.process_url_auth(req.query_string)
        else:
            user, token, auth_type = self.process_auth(req.auth)
        setattr(req, 'user', user)
        setattr(req, 'token', token)
        setattr(req, 'auth_type', auth_type)

    def process_response(self, req, resp, resource, req_succeeded, *args, **kwargs):
        """Post-processing of the response (after routing).

        Args:
            req: Request object.
            resp: Response object.
            resource: Resource object to which the request was
                routed. May be None if no route was found
                for the request.
            req_succeeded: True if no exceptions were raised while
                the framework processed and routed the request;
                otherwise False.
        """


class LoggerMiddleware(object):
    def __init__(self, logger):
        self.logger = logger

    def process_request(self, req, resp, *args, **kwargs):
        self.logger.info('[REQUEST] {0} {1}'.format(req.method, req.relative_uri))

    def process_response(self, req, resp, *args, **kwargs):
        self.logger.info('[RESPONSE] {0} {1} {2}'.format(req.method, req.relative_uri, resp.status[:3]))
