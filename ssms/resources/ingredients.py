import falcon

from ssms.models import Ingredient
from ssms.util.response import format_errors, format_error, format_response

import json

from logging import getLogger

logger = getLogger(__name__)


def get_ingredient(req, resp, resource, params):
    ingredient_id = params.get('ingredient_id', None)
    if not ingredient_id:
        raise falcon.HTTPError(falcon.HTTP_400)

    ingredient = Ingredient.get_by_id(ingredient_id)

    if not ingredient:
        raise falcon.HTTPError(falcon.HTTP_404)

    params['ingredient'] = ingredient


@falcon.before(get_ingredient)
class IngredientDetailResorce(object):
    schema = Ingredient.schema()

    def on_get(self, res, resp, ingredient, *args, **kwargs):
        data, errors = self.schema.dump(ingredient)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_put(self, req, resp, ingredient, *args, **kwargs):
        data = json.loads(req.stream.read(req.content_length or 0))

        ingredient, errors = self.schema.dump(ingredient)
        ingredient.update(data)

        ingredient, errors = self.schema.load(ingredient)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            ingredient.save()

            data, errors = self.schema.dump(ingredient)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)


class IngredientListResource(object):
    schema = Ingredient.schema()

    def on_get(self, req, resp, *args, **kwargs):
        ingredients = Ingredient.get_all()

        data, errors = self.schema.dump(ingredients, many=True)

        if errors:
            logger.error(errors)
            raise falcon.HTTPInternalServerError()

        data = format_response(data)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(data, ensure_ascii=False)

    def on_post(self, req, resp, *args, **kwargs):
        data = json.loads(req.stream.read(req.content_length or 0))

        data.pop('type', None)

        ingredient, errors = self.schema.load(data)

        if errors:
            errors = [
                format_error('missing-field', ' '.join(value), dict(field=key))
                for key, value in errors.items()
            ]
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(format_errors(errors), ensure_ascii=False)
        else:
            ingredient.save()

            data, errors = self.schema.dump(ingredient)

            resp.status = falcon.HTTP_200
            resp.body = json.dumps(format_response(data), ensure_ascii=False)
