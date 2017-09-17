import falcon

from ssms.models import Admin, Client
from ssms.util.response import format_response, format_error, format_errors
from ssms import hooks

import json

from logging import getLogger

logger = getLogger(__name__)


@falcon.before(hooks.require_admin)
class AdminListResource(object):
    schema = Admin.schema()

    def on_get(self, req, resp):
        admins = Admin.get_all()
        self.schema.context['remove_fields'] = ['seed', 'password']
        data, errors = self.schema.dump(admins, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp):
        data = json.loads(req.stream.read(req.content_length or 0))

        admin, errors = self.schema.load(data)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            admin.set_password(admin.password)
            admin.save()

            self.schema.context['remove_fields'] = ['seed', 'password']
            data, errors = self.schema.dump(admin)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


def get_client(req, resp, resource, params):
    client_id = params.get('client_id', None)
    if not client_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    client = Client.get_by_id(client_id)

    if not client:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['client'] = client


class ClientListResource(object):
    schema = Client.schema()

    def on_get(self, req, resp):
        users = Client.get_all()
        data, errors = self.schema.dump(users, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp):
        data = json.loads(req.stream.read(req.content_length or 0))

        user, errors = self.schema.load(data)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            user.set_password(user.password)
            user.save()

            self.schema.context['remove_fields'] = ['seed', 'password']
            data, errors = self.schema.dump(user)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(get_client)
class ClientDetailResource(object):
    schema = Client.schema()

    def on_get(self, res, resp, client, *args, **kwargs):
        data, errors = self.schema.dump(client)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, client, *args, **kwargs):
        data = json.loads(req.stream.read(req.content_length or 0))

        print(client)
        print(data)

        client, errors = self.schema.dump(client)
        client.update(data)

        client, errors = self.schema.load(client)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            client.save()

            data, errors = self.schema.dump(client)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)
