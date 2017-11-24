import falcon

from ssms.models import Admin, Client, User
from ssms.util.response import format_response, format_error, format_errors
from ssms import hooks

import json

from logging import getLogger

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_user)
class UsersListResource(object):
    schema = User.schema

    def on_get(self, req, resp, *args, **kwargs):
        user = req.user
        schema = self.schema()
        schema.context['remove_fields'] = ['seed', 'password']

        data, errors = schema.dump(user)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class AdminListResource(object):
    schema = Admin.schema

    def on_get(self, req, resp):
        admins = Admin.get_all()
        schema = self.schema()
        schema.context['remove_fields'] = ['seed', 'password']
        data, errors = schema.dump(admins, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp):
        data = json.loads(req.stream.read(req.content_length or 0))

        schema = self.schema()

        admin, errors = schema.load(data)

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

            schema.context['remove_fields'] = ['seed', 'password']
            data, errors = schema.dump(admin)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
class ClientListResource(object):
    schema = Client.schema

    def on_get(self, req, resp):
        users = Client.get_all()
        schema = self.schema()
        schema.context['remove_fields'] = ['seed', 'password']
        data, errors = schema.dump(users, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp):
        data = json.loads(req.stream.read(req.content_length or 0))

        schema = self.schema()

        user, errors = schema.load(data)

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

            schema.context['remove_fields'] = ['seed', 'password']
            data, errors = schema.dump(user)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.get_client)
class ClientDetailResource(object):
    schema = Client.schema

    def on_get(self, req, resp, client, *args, **kwargs):
        schema = self.schema()
        schema.context['remove_fields'] = ['seed', 'password']

        data, errors = schema.dump(client)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, client, *args, **kwargs):
        data = json.loads(req.stream.read(req.content_length or 0))

        schema = self.schema()

        client, errors = schema.dump(client)

        client.update(data)

        client, errors = schema.load(client)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            client.save()

            schema.context['remove_fields'] = ['seed', 'password']
            data, errors = schema.dump(client)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)

    def on_delete(self, req, resp, client, *args, **kwargs):
        schema = self.schema()

        client.delete()

        schema.context['remove_fields'] = ['seed', 'password']
        data, errors = schema.dump(client)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)
