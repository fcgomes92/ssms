from sqlalchemy.ext.declarative import declarative_base, declared_attr, AbstractConcreteBase
from sqlalchemy.orm import subqueryload, relationship
from sqlalchemy import Column, Integer, String, Sequence, Float, ForeignKey, func, Enum, update

import enum

import hashlib

import uuid

from ssms import app
from ssms.schemas import (UserSchema, AdminSchema, ClientSchema, IngredientSchema, ProductSchema,
                          ProductIngredientSchema)


class Base(object):
    session = app.Session()

    def save(self):
        if not self.id:
            self.session.add(self)
        else:
            cls = self.__class__
            self.session.query(cls) \
                .filter(cls.id == self.id) \
                .update(
                {
                    column: getattr(self, column)
                    for column in self.__table__.columns.keys()
                }
            )
        self.session.commit()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def get_all(cls):
        return cls.session.query(cls).all()

    @classmethod
    def get_by_id(cls, id):
        if cls.id:
            return cls.session.query(cls).filter(cls.id == id).first()
        else:
            return None


BaseModel = declarative_base(cls=Base)


class Ingredient(BaseModel):
    schema = IngredientSchema
    collection = 'ingredient'

    id = Column(Integer, Sequence('ingredient_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String(128))
    unit = Column(String(128))

    def __repr__(self):
        return "<{} (name={}, unit={})>" \
            .format(self.__class__.__name__, self.name, self.unit)


class ProductIngredient(BaseModel):
    schema = ProductIngredientSchema

    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True)
    amount = Column(Float)

    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', )

    def __repr__(self):
        return "<{}(product_id={}, ingredient_id={}, amount={:.2f})>" \
            .format(self.__class__.__name__, self.product_id, self.ingredient_id, self.amount)


class Product(BaseModel):
    schema = ProductSchema
    collection = 'product'

    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(Float)
    discount = Column(Float)
    ingredients = relationship('ProductIngredient', back_populates='product')

    def __repr__(self):
        return "<{} (name={}, value={})>" \
            .format(self.__class__.__name__, self.name, self.value)


class OrderProduct(Base):
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    amount = Column(Integer)

    product = relationship('Product')
    order = relationship('Order', back_populates='products')

    def __repr__(self):
        return "<{}(order_id={}, product_id={},amount={})>" \
            .format(self.__class__.__name__, self.product_id, self.order_id, self.amount)


class Order(Base):
    id = Column(Integer, Sequence('orders_id_seq'), primary_key=True, autoincrement=True)
    ref = Column(String(256))
    # user = relationship('User')
    products = relationship('OrderProduct', back_populates='order')

    def __repr__(self):
        return "<{}(id={}, ref={})>" \
            .format(self.__class__.__name__, self.id, self.ref)


class UsersEnum(enum.Enum):
    admin = 0
    client = 1


class User(AbstractConcreteBase, BaseModel):
    schema = UserSchema
    collection = 'user'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, autoincrement=True)
    email = Column(String(128), unique=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    password = Column(String(256))
    seed = Column(String(128))
    user_type = Column(Enum(UsersEnum), default=UsersEnum.client)

    def __repr__(self):
        return "<{} (id={}, email={}, first_name={}, last_name={})>" \
            .format(self.__class__.__name__, self.id, self.email, self.first_name, self.last_name)

    @staticmethod
    def hash_password(password, seed):
        if not seed:
            seed = uuid.uuid4().hex
        return hashlib.sha512((password + seed).encode()).hexdigest(), seed

    def set_password(self, password):
        self.password, self.seed = self.hash_password(password, None)

    @classmethod
    def get_by_email(cls, email):
        return cls.session.query(cls).filter(cls.email == email).first()


class Admin(User):
    schema = AdminSchema

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'concrete': True
    }

    def save(self, *args, **kwargs):
        self.user_type = UsersEnum.admin
        super().save(*args, **kwargs)


class Client(User):
    schema = ClientSchema

    __mapper_args__ = {
        'polymorphic_identity': 'client',
        'concrete': True
    }

    def save(self, *args, **kwargs):
        self.user_type = UsersEnum.client
        super().save(*args, **kwargs)


BaseModel.metadata.create_all(app.engine)
