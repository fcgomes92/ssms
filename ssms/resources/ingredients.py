import json
from logging import getLogger

import falcon

from ssms import hooks
from ssms.models import Ingredient
from ssms.schemas import IngredientSchema
from ssms.util.response import format_error, format_errors, format_response

logger = getLogger(__name__)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
class IngredientListResource(object):

    def on_get(self, req, resp, *args, **kwargs):
        schema = IngredientSchema()
        ingredients = Ingredient.get_all()

        data, errors = schema.dump(ingredients, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp, *args, **kwargs):
        schema = IngredientSchema()
        data = json.loads(req.stream.read(req.content_length or 0))

        data.pop('type', None)

        ingredient, errors = schema.load(data)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            ingredient.save()

            data, errors = schema.dump(ingredient)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


@falcon.before(hooks.require_auth)
@falcon.before(hooks.require_admin)
@falcon.before(hooks.get_ingredient)
class IngredientDetailResource(object):
    def on_get(self, res, resp, ingredient, *args, **kwargs):
        schema = IngredientSchema()
        data, errors = schema.dump(ingredient)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, ingredient, *args, **kwargs):
        schema = IngredientSchema()

        data = json.loads(req.stream.read(req.content_length or 0))

        ingredient, errors = schema.load(data, partial=True, instance=ingredient)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            ingredient.save()

            data, errors = schema.dump(ingredient)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)

    def on_delete(self, req, resp, ingredient, *args, **kwargs):
        schema = IngredientSchema()

        ingredient.delete()

        data, errors = schema.dump(ingredient)

        resp.status = falcon.HTTP_200

        resp.body = json.dumps(format_response(data), ensure_ascii=False)
