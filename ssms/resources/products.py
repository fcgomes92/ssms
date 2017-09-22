import falcon

from ssms.models import Product
from ssms.util.response import format_errors, format_error, format_response

import json

from logging import getLogger

logger = getLogger(__name__)


def get_product(req, resp, resource, params):
    product_id = params.get('product_id', None)
    if not product_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    product = Product.get_by_id(product_id)

    if not product:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['product'] = product


@falcon.before(get_product)
class ProductDetailResource(object):
    schema = Product.schema

    def on_get(self, res, resp, product, *args, **kwargs):
        schema = self.schema()
        data, errors = schema.dump(product)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, product, *args, **kwargs):
        schema = self.schema()
        data = json.loads(req.stream.read(req.content_length or 0))

        product, errors = schema.dump(product)
        product.update(data)

        product, errors = schema.load(product)

        if errors:
            logger.error(errors)
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

    def on_delete(self, req, resp, product, *args, **kwargs):
        schema = self.schema()

        product.delete()

        data, errors = schema.dump(product)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)


class ProductListResource(object):
    schema = Product.schema

    def on_get(self, req, resp, *args, **kwargs):
        schema = self.schema()
        products = Product.get_all()

        data, errors = schema.dump(products, many=True)

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
