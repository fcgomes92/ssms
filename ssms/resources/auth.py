import falcon

from ssms.util.response import format_response
from ssms.hooks import require_auth

import json

from logging import getLogger

logger = getLogger(__name__)


@falcon.before(require_auth)
class UserAuthenticationResource(object):
    def on_post(self, req, resp, *args, **kwargs):
        user = getattr(req, 'user')

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(format_response(user.get_token()), ensure_ascii=False)
