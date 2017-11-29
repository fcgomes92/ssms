from marshmallow import Schema as BaseSchema, fields, post_load, post_dump
from marshmallow_enum import EnumField

from sqlalchemy import inspect

from ssms.models.enums import UsersEnum


class Schema(BaseSchema):
    created = fields.DateTime(dump_only=True, allow_none=True, format='iso')
    updated = fields.DateTime(dump_only=True, allow_none=True, format='iso')

    def load(self, data, instance=None, **kwargs):
        result, errors = super(Schema, self).load(data, **kwargs)

        if errors:
            return None, errors

        if instance:
            mapper = inspect(instance)
            for field in mapper.attrs:
                updated_value = getattr(result, field.key, None)
                if updated_value:
                    setattr(instance, field.key, updated_value)

            return instance, errors

        return result, errors


class UserSchema(Schema):
    id = fields.Integer(allow_none=True, dump_only=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    seed = fields.String(allow_none=True)
    first_name = fields.String(required=True)
    user_type = EnumField(UsersEnum, by_value=True, allow_none=True)
    last_name = fields.String(required=True)
    code = fields.String(dump_only=True, allow_none=True)

    @post_load
    def make_user(self, data):
        from ssms.models import User
        return User(**data)

    @post_dump
    def remove_fields(self, data):
        for field in self.context.get('remove_fields', []):
            data.pop(field, None)


class AdminSchema(UserSchema):
    @post_load
    def make_user(self, data):
        from ssms.models import Admin
        data['user_type'] = 'admin'
        return Admin(**data)


class ClientSchema(UserSchema):
    @post_load
    def make_user(self, data):
        from ssms.models import Client
        data['user_type'] = 'client'
        return Client(**data)


class IngredientSchema(Schema):
    id = fields.Integer(allow_none=True, dump_only=True)
    name = fields.String(required=True)
    unit = fields.String(required=True)
    code = fields.String(dump_only=True, allow_none=True)

    @post_load
    def make_ingredient(self, data):
        from ssms.models import Ingredient
        return Ingredient(**data)


class ProductIngredientSchema(Schema):
    ingredient_id = fields.Integer()
    product_id = fields.Integer()
    ingredient = fields.Nested(IngredientSchema, allow_none=True)
    amount = fields.Float(default=0)

    @post_load
    def make_pi(self, data):
        from ssms.models import ProductIngredient
        return ProductIngredient(**data)


class ProductSchema(Schema):
    id = fields.Integer(allow_none=True, dump_only=True)
    name = fields.String(required=True)
    value = fields.Float(required=True)
    discount = fields.Float()
    ingredients = fields.Nested(ProductIngredientSchema, default=[], many=True)
    code = fields.String(dump_only=True, allow_none=True)

    @post_load
    def make_product(self, data):
        from ssms.models import Product
        return Product(**data)


class OrderProductSchema(Schema):
    product_id = fields.Integer(allow_none=True)
    order_id = fields.Integer(allow_none=True)
    product = fields.Nested(ProductSchema, allow_none=True)
    amount = fields.Float(default=0)

    @post_load
    def make_order_product(self, data):
        from ssms.models import OrderProduct
        return OrderProduct(**data)


class OrderSchema(Schema):
    id = fields.Integer(allow_none=True, dump_only=True)
    client_id = fields.Integer()
    client = fields.Nested(ClientSchema, dump_only=True, allow_none=True)
    products = fields.Nested(OrderProductSchema, default=[], many=True)
    code = fields.String(dump_only=True, allow_none=True)

    @post_load
    def make_order(self, data):
        from ssms.models import Order
        return Order(**data)


class OrderProductsReportSchema(BaseSchema):
    product_id = fields.Integer()
    product = fields.Nested(ProductSchema)
    total = fields.Float()


class OrderIngredientsReportSchema(BaseSchema):
    ingredient_id = fields.Integer()
    ingredient = fields.Nested(IngredientSchema)
    total = fields.Float()


class ProductIngredientsReportSchema(BaseSchema):
    ingredient_id = fields.Integer()
    ingredient = fields.Nested(IngredientSchema)
    total = fields.Float()
