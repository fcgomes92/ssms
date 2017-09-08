from bson.objectid import ObjectId

import pymongo

import hashlib

import uuid

from ssms.schemas import UserSchema, AdminSchema, ClientSchema
from ssms import app
from ssms.util.decorators import assert_base_model


class BaseModel(object):
    schema = None
    collection = None

    @staticmethod
    def refactor_object_id_to_id(obj):
        obj['id'] = str(obj.pop('_id'))
        return obj

    @assert_base_model
    def save(self):
        data, errors = self.schema().dump(self)

        assert not errors, Exception(errors)

        # updates the already created instance
        if self.id:
            object_id = ObjectId(data.get('id'))
            data.pop('id')
            return app.db[self.collection].update_one({'_id': object_id},
                                                      {"$set": data},
                                                      upsert=False)

        data.pop('id', None)

        # creates a new instance
        self.id = str(app.db[self.collection].insert_one(data).inserted_id)

        # sets a unique index on each unique field
        unique_fields = getattr(self, 'unique', [])
        app.db[self.collection].create_index([(field, pymongo.ASCENDING) for field in unique_fields], unique=True)

        return self

    @classmethod
    @assert_base_model
    def query(cls, query=dict(), unique=False):
        if unique:
            result = app.db[cls.collection].find_one(query)
            result['id'] = str(result.pop('_id'))
            data, error = cls.schema().load(data=result)
            if error:
                raise Exception(error)
            return data
        else:
            result = app.db[cls.collection].find(query)
            result = list(map(cls.refactor_object_id_to_id, result))
            data, error = cls.schema().load(data=result, many=True)
            if error:
                raise Exception(error)
            return data


class Category(BaseModel):
    def __init__(self, name, description, products=list()):
        self.name = name
        self.description = description
        self.products = products


class Product(BaseModel):
    def __init__(self, name, value, discount=0, ingredients=list(), categories=list()):
        self.name = name
        self.value = value
        self.discount = discount
        self.ingredients = ingredients
        self.categories = categories


class ProductCategoryRel(BaseModel):
    def __init__(self, product: Product, category: Category):
        self.product_id = product.id
        self.category_id = category.id


class Ingredient(BaseModel):
    def __init__(self, name, type, default_unit):
        self.name = name
        self.type = type
        self.default_unit = default_unit


class ProductIngredientRel(BaseModel):
    def __init__(self, product, ingredient, amount, unit):
        self.product = product
        self.ingredient = ingredient
        self.amount = amount
        self.unit = unit


class ProductOrderRel(BaseModel):
    pass


class Receipt(BaseModel):
    pass


class User(BaseModel):
    schema = UserSchema
    collection = 'user'
    unique = ('email',)

    def __init__(self, email, first_name, last_name, password=None, seed=None, type='client', id=None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.seed = seed
        self.type = type

    def __str__(self):
        return "{id}: {email} - {fn} {ln}".format(
            id=self.id,
            email=self.email,
            fn=self.first_name,
            ln=self.last_name)

    @staticmethod
    def hash_password(password, seed):
        if not seed:
            seed = uuid.uuid4().hex
        return hashlib.sha512((password + seed).encode()).hexdigest(), seed

    def set_password(self, password):
        self.password, self.seed = self.hash_password(password, None)


class Admin(User):
    schema = AdminSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'admin'


class Client(User):
    schema = ClientSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'client'


class Order(BaseModel):
    def __init__(self, user: User, receipt: Receipt):
        self.user = user
        self.receipt = receipt
