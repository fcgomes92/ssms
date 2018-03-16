import json
from logging import getLogger

import falcon

from ssms import hooks
from ssms.models import Admin, Client
from ssms.schemas import AdminSchema, ClientSchema, UserSchema
from ssms.util.response import format_error, format_errors, format_response

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_user)
class UsersListResource(object):

    def on_get(self, req, resp, *args, **kwargs):
        user = req.user
        schema = UserSchema()
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

    def on_get(self, req, resp):
        admins = Admin.get_all()
        schema = AdminSchema()
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

        schema = AdminSchema()

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
@falcon.before(hooks.require_admin)
class ClientListResource(object):
    def on_get(self, req, resp):
        users = Client.get_all()
        schema = ClientSchema()
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

        schema = ClientSchema()

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
@falcon.before(hooks.require_admin)
class ClientDetailResource(object):
    def on_get(self, req, resp, client, *args, **kwargs):
        schema = ClientSchema()
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

        schema = ClientSchema()

        client, errors = schema.load(data, instance=client, partial=True)

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
        schema = ClientSchema()

        client.delete()

        schema.context['remove_fields'] = ['seed', 'password']
        data, errors = schema.dump(client)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)
