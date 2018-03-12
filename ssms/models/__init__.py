import hashlib
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, Sequence, String, func
from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base, declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.mapper import configure_mappers

from ssms import app
from ssms.database import session
from ssms.models.enums import UsersEnum
from ssms.schemas import (
    AdminSchema, ClientSchema, IngredientSchema, OrderProductSchema, OrderSchema, ProductIngredientSchema,
    ProductSchema, UserSchema,
)
from ssms.util import auth, friendly_code


class Base(object):
    created = Column(DateTime)
    updated = Column(DateTime)

    __table__ = None
    id = None
    code = None

    def save(self):
        if not getattr(self, 'id', None):
            self.created = datetime.utcnow()
            session().add(self)
        else:
            cls = self.__class__
            query = session().query(cls)
            query = query.filter(cls.id == self.id)
            query.update({
                column: getattr(self, column)
                for column in self.__table__.columns.keys()
            })
        self.updated = datetime.utcnow()
        session().commit()

        if 'code' in self.__table__.columns.keys():
            if not self.code:
                self.code = friendly_code.encode(int(self.id))
                session().commit()

    def delete(self):
        session().delete(self)
        session().commit()

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    @classmethod
    def get_all(cls):
        return session().query(cls).all()

    @classmethod
    def get_by_id(cls, model_id):
        if cls.id:
            return session().query(cls).filter(cls.id == model_id).first()
        else:
            return None

    @classmethod
    def get_by_code(cls, code):
        if getattr(cls, 'code', None):
            return session().query(cls).filter(cls.code == code).first()
        else:
            return None


BaseModel = declarative_base(cls=Base)


class Ingredient(BaseModel):
    schema = IngredientSchema

    id = Column(Integer, Sequence('ingredient_id_seq'), primary_key=True,
                autoincrement=True)
    name = Column(String(128))
    unit = Column(String(128))
    code = Column(String(256), index=True, unique=True)

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):
        return "<{} (name={}, unit={})>" \
            .format(self.__class__.__name__, self.name, self.unit)


class Product(BaseModel):
    schema = ProductSchema

    id = Column(Integer, Sequence('product_id_seq'), primary_key=True,
                autoincrement=True)
    name = Column(String)
    value = Column(Float)
    discount = Column(Float)
    code = Column(String(256), index=True, unique=True)

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):
        return "<{} (name={}, value={})>" \
            .format(self.__class__.__name__, self.name, self.value)

    @classmethod
    def report_ingredients(cls, products_ids=list(), subquery=False):
        query = session().query(Ingredient,
                                func.sum(ProductIngredient.amount).label(
                                    'total'))
        query = query.select_from(ProductIngredient).join(Ingredient)
        query = query.filter(ProductIngredient.product_id.in_(products_ids))
        query = query.group_by(ProductIngredient.ingredient_id)

        if subquery:
            return query.subquery()
        else:
            return query.all()


class Order(BaseModel):
    schema = OrderSchema

    id = Column(Integer, Sequence('orders_id_seq'), primary_key=True,
                autoincrement=True)
    code = Column(String(256), index=True, unique=True)

    client_id = Column(Integer, ForeignKey('client.id'))

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):
        return "<{}(id={}, code={}, client_id={})>" \
            .format(self.__class__.__name__, self.id, self.code, self.client_id)

    @classmethod
    def report_products(cls, orders_ids=list(), subquery=False):
        query = session().query(Product,
                                func.sum(OrderProduct.amount).label('total'))
        query = query.select_from(OrderProduct).join(Product)
        query = query.filter(OrderProduct.order_id.in_(orders_ids))
        query = query.group_by(Product.id)

        if subquery:
            return query.subquery()
        else:
            return query.all()

    @classmethod
    def report_ingredients(cls, orders_ids=list(), subquery=False):
        stmt = cls.report_products(orders_ids=orders_ids, subquery=True)

        query = session().query(Ingredient, func.sum(
            stmt.c.total * ProductIngredient.amount), )
        query = query.select_from(ProductIngredient).join(Ingredient)
        query = query.join(stmt, ProductIngredient.product_id == stmt.c.id)
        query = query.group_by(Ingredient.id)

        if subquery:
            return query.subquery()
        else:
            return query.all()


class ProductIngredient(BaseModel):
    schema = ProductIngredientSchema

    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'),
                           primary_key=True)
    amount = Column(Float)

    product = relationship('Product',
                           lazy="subquery",
                           cascade='save-update, merge, expunge',
                           backref=backref('ingredients',
                                           lazy="subquery",
                                           cascade="all, delete-orphan",
                                           single_parent=True))
    ingredient = relationship('Ingredient',
                              lazy="subquery",
                              cascade='save-update, merge, expunge',
                              backref=backref('products',
                                              lazy="subquery",
                                              cascade="all, delete-orphan",
                                              single_parent=True))

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    @classmethod
    def get_by_product_id(cls, product_id):
        return list(session().query(cls).filter(cls.product_id == product_id))

    @classmethod
    def get_by_ingredient_id(cls, ingredient_id):
        return list(
            session().query(cls).filter(cls.ingredient_id == ingredient_id))

    @classmethod
    def get_by_product_ingredient(cls, product_id, ingredient_id):
        # return session().query(cls).filter(cls.code == code).first()
        return session().query(cls).filter(cls.product_id == product_id) \
            .filter(cls.ingredient_id == ingredient_id).first()

    def __repr__(self):
        return "<{}(product_id={}, ingredient_id={}, amount={:.2f})>" \
            .format(self.__class__.__name__, self.product_id,
                    self.ingredient_id, self.amount)


class OrderProduct(BaseModel):
    schema = OrderProductSchema

    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    amount = Column(Integer)

    product = relationship('Product',
                           lazy="subquery",
                           cascade='save-update, merge, expunge',
                           backref=backref('orders',
                                           lazy="subquery",
                                           cascade="all, delete-orphan",
                                           single_parent=True))
    order = relationship('Order',
                         lazy="subquery",
                         cascade='save-update, merge, expunge',
                         backref=backref('products',
                                         lazy="subquery",
                                         cascade="all, delete-orphan",
                                         single_parent=True))

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    @classmethod
    def get_by_product_id(cls, product_id):
        return list(session().query(cls).filter(cls.product_id == product_id))

    @classmethod
    def get_by_order_id(cls, order_id):
        return list(session().query(cls).filter(cls.order_id == order_id))

    @classmethod
    def get_by_product_order(cls, product_id, order_id):
        # return session().query(cls).filter(cls.code == code).first()
        return session().query(cls).filter(cls.product_id == product_id) \
            .filter(cls.order_id == order_id).first()

    def __repr__(self):
        return "<{}(order_id={}, product_id={},amount={})>" \
            .format(self.__class__.__name__, self.order_id, self.product_id,
                    self.amount)


class User(AbstractConcreteBase, BaseModel):
    schema = UserSchema

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True,
                autoincrement=True)
    email = Column(String(128), unique=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    password = Column(String(256))
    seed = Column(String(128))
    user_type = Column(Enum(UsersEnum), default=UsersEnum.client)
    code = Column(String(256), index=True, unique=True)

    __mapper_args__ = {
        'confirm_deleted_rows': False,
    }

    def __repr__(self):
        return "<{} (id={}, email={}, first_name={}, last_name={})>" \
            .format(self.__class__.__name__, self.id, self.email,
                    self.first_name, self.last_name)

    @staticmethod
    def hash_password(password, seed):
        if not seed:
            seed = uuid.uuid4().hex
        return hashlib.sha512((password + seed).encode()).hexdigest(), seed

    def set_password(self, password):
        self.password, self.seed = self.hash_password(password, None)

    @classmethod
    def get_by_email(cls, email):
        return session().query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_token(cls, token):
        data = auth.decode(token)
        return cls.get_by_email(data.get('email'))

    def get_token(self):
        from ssms.util.auth import encode
        return encode(dict(code=self.code, email=self.email)).decode()


class Admin(User):
    schema = AdminSchema

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'concrete':             True,
    }

    def save(self, *args, **kwargs):
        self.user_type = UsersEnum.admin
        super().save(*args, **kwargs)


class Client(User):
    schema = ClientSchema

    orders = relationship('Order',
                          backref=backref('client', lazy="subquery"),
                          cascade="all, delete-orphan",
                          lazy="subquery")

    __mapper_args__ = {
        'polymorphic_identity': 'client',
        'concrete':             True
    }

    def save(self, *args, **kwargs):
        self.user_type = UsersEnum.client
        super().save(*args, **kwargs)


BaseModel.metadata.create_all(app.engine)
# maps the abstract user class
configure_mappers()
