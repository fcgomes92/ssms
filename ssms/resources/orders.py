import json
from logging import getLogger

import falcon

from ssms import hooks
from ssms.models import Order
from ssms.schemas import OrderIngredientsReportSchema, OrderProductSchema, OrderProductsReportSchema, OrderSchema
from ssms.util.response import format_error, format_errors, format_response

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class OrderListResource(object):
    def on_get(self, req, resp, *args, **kwargs):
        schema = OrderSchema()
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
        schema = OrderSchema()
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
    def on_get(self, req, resp, order, *args, **kwargs):
        schema = OrderSchema()
        data, errors = schema.dump(order)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        schema.context['remove_fields'] = ['seed', 'password']

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, order, *args, **kwargs):
        schema = OrderSchema()

        data = json.loads(req.stream.read(req.content_length or 0))

        products = data.pop('products', None)

        order, errors = schema.load(data, partial=True, instance=order)

        if products:
            op_schema = OrderProductSchema()
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
        schema = OrderSchema()

        order.delete()

        schema.context['remove_fields'] = ['seed', 'password']

        data, errors = schema.dump(order)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class OrderProductsReportResource(object):
    def on_get(self, req, resp, *args, **kwargs):
        schema = OrderProductsReportSchema()

        data = json.loads(req.stream.read(req.content_length or 0))

        try:
            report_data = [
                dict(
                    product_id=product.id,
                    product=product,
                    total=float(total),
                ) for product, total in Order.report_products(data)
            ]
            report, errors = schema.dump(report_data, many=True)
        except Exception as e:
            logger.error(e)
            resp.status = falcon.HTTP_500
        else:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(report), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class OrderIngredientsReportResource(object):
    def on_get(self, req, resp, *args, **kwargs):
        oi_schema = OrderIngredientsReportSchema()

        data = json.loads(req.stream.read(req.content_length or 0))

        try:
            report_data = [
                dict(
                    ingredient_id=ingredient.id,
                    ingredient=ingredient,
                    total=float(total),
                ) for ingredient, total in Order.report_ingredients(data)
            ]
            report, errors = oi_schema.dump(report_data, many=True)
        except Exception as e:
            logger.error(e)
            resp.status = falcon.HTTP_500
        else:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(report), ensure_ascii=False)
