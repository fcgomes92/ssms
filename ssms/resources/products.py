import json
from logging import getLogger

import falcon

from ssms import hooks
from ssms.models import Product
from ssms.schemas import ProductIngredientSchema, ProductIngredientsReportSchema, ProductSchema
from ssms.util.response import format_error, format_errors, format_response

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class ProductListResource(object):
    def on_get(self, req, resp, *args, **kwargs):
        schema = ProductSchema()
        products = Product.get_all()

        data, errors = schema.dump(products, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp, *args, **kwargs):
        schema = ProductSchema()
        data = json.loads(req.stream.read(req.content_length or 0))

        data.pop('type', None)

        product, errors = schema.load(data)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            product.save()

            data, errors = schema.dump(product)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
@falcon.before(hooks.get_product)
class ProductDetailResource(object):
    def on_get(self, res, resp, product, *args, **kwargs):
        schema = ProductSchema()
        data, errors = schema.dump(product)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, product, *args, **kwargs):
        schema = ProductSchema()
        data = json.loads(req.stream.read(req.content_length or 0))

        ingredients = data.pop('ingredients', None)

        product, errors = schema.load(data, partial=True, instance=product)

        pi_errors = None
        pi = None
        if ingredients:
            pi_schema = ProductIngredientSchema()
            pi, pi_errors = pi_schema.load(ingredients, many=True, partial=True)

        if errors:
            logger.error(errors)
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        elif pi_errors:
            logger.error(pi_errors)
            pi_errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in pi_errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(pi_errors), ensure_ascii=False)
        else:
            if pi:
                product.ingredients = pi

            product.save()

            data, errors = schema.dump(product)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)

    def on_delete(self, req, resp, product, *args, **kwargs):
        schema = ProductSchema()

        product.delete()

        data, errors = schema.dump(product)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class ProductIngredientsReportResource(object):
    def on_get(self, req, resp, *args, **kwargs):
        schema = ProductIngredientsReportSchema()

        data = json.loads(req.stream.read(req.content_length or 0))

        try:
            report_data = [
                dict(
                    ingredient_id=ingredient.id,
                    ingredient=ingredient,
                    total=float(total),
                ) for ingredient, total in Product.report_ingredients(data)
            ]
            report, errors = schema.dump(report_data, many=True)
        except Exception as e:
            logger.error(e)
            resp.status = falcon.HTTP_500
        else:
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(report), ensure_ascii=False)
