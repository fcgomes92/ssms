from marshmallow import Schema, fields, post_load, post_dump


class UserSchema(Schema):
    id = fields.String(allow_none=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    seed = fields.String(allow_none=True)
    first_name = fields.String(required=True)
    type = fields.String(allow_none=True)
    last_name = fields.String(required=True)

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
        return Admin(**data)


class ClientSchema(UserSchema):
    @post_load
    def make_user(self, data):
        from ssms.models import Client
        return Client(**data)


class IngredientSchema(Schema):
    id = fields.String(allow_none=True)
    name = fields.String(required=True)
    unit = fields.String(required=True)

    @post_load
    def make_ingredient(self, data):
        from ssms.models import Ingredient
        return Ingredient(**data)
