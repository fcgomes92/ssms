import falcon

from ssms import hooks
from ssms.models import Order
from ssms.util.response import format_errors, format_error, format_response

import json

from logging import getLogger

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class OrderListResource(object):
    schema = Order.schema

    def on_get(self, req, resp, *args, **kwargs):
        schema = self.schema()
        orders = Order.get_all()

        data, errors = schema.dump(orders, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp, *args, **kwargs):
        schema = self.schema()
        data = json.loads(req.stream.read(req.content_length or 0))

        data.pop('type', None)

        order, errors = schema.load(data)

        if errors:
            logger.error(errors)
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            order.save()

            data, errors = schema.dump(order)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
@falcon.before(hooks.get_order)
class OrderDetailResource(object):
    schema = Order.schema

    def on_get(self, res, resp, order, *args, **kwargs):
        schema = self.schema()
        data, errors = schema.dump(order)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, order, *args, **kwargs):
        schema = self.schema()
        data = json.loads(req.stream.read(req.content_length or 0))

        order, errors = schema.dump(order)
        order.update(data)

        order, errors = schema.load(order)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            order.save()

            data, errors = schema.dump(order)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)

    def on_delete(self, req, resp, order, *args, **kwargs):
        schema = self.schema()

        order.delete()

        data, errors = schema.dump(order)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)
