import falcon

from ssms import hooks
from ssms.models import Order, OrderProduct
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

        schema.context['remove_fields'] = ['seed', 'password']

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
            schema.context['remove_fields'] = ['seed', 'password']

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

        schema.context['remove_fields'] = ['seed', 'password']

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, order, *args, **kwargs):
        schema = self.schema()

        data = json.loads(req.stream.read(req.content_length or 0))

        products = data.pop('products', None)

        order, errors = schema.load(data, partial=True, instance=order)

        if products:
            op_schema = OrderProduct.schema()
            op, op_errors = op_schema.load(products, many=True, partial=True)
        else:
            op_errors = None
            op = None

        if errors:
            logger.error(errors)
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        elif op_errors:
            logger.error(op_errors)
            op_errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in op_errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(op_errors), ensure_ascii=False)
        else:
            if op:
                order.products = op

            schema.context['remove_fields'] = ['seed', 'password']

            order.save()

            data, errors = schema.dump(order)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)

    def on_delete(self, req, resp, order, *args, **kwargs):
        schema = self.schema()

        order.delete()

        schema.context['remove_fields'] = ['seed', 'password']

        data, errors = schema.dump(order)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)
