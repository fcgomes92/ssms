from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', echo=False)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import subqueryload, aliased
from sqlalchemy import func

Base = declarative_base()

from sqlalchemy import Column, Integer, String, Sequence, Float, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)


class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, Sequence('ingredient_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String)
    unit = Column(String)

    def __repr__(self):
        return "<Ingredient(name='%s', unit='%s')>" % (
            self.name, self.unit)


class ProductIngredient(Base):
    __tablename__ = 'product_ingredient'

    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), primary_key=True)
    amount = Column(Float)

    product = relationship('Product', back_populates='ingredients')
    ingredient = relationship('Ingredient', )


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, Sequence('product_id_seq'), primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(Float)
    discount = Column(Float)
    ingredients = relationship('ProductIngredient', back_populates='product')

    def __repr__(self):
        return "<Product(name='%s', value='%s')>" % (
            self.name, self.value)


class OrderProduct(Base):
    __tablename__ = 'order_product'

    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    amount = Column(Integer)

    product = relationship('Product')
    order = relationship('Order', back_populates='products')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, Sequence('orders_id_seq'), primary_key=True, autoincrement=True)
    ref = Column(String(256))
    # user = relationship('User')
    products = relationship('OrderProduct', back_populates='order')


Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

session = Session()

u = User(name='Fernando', email='fcgomes.92@gmail.com', password='qwe123')

session.add(u)

session.commit()

mock_ingredient_data = [
    {
        "name": "Fernamento",
        "unit": "g",
    },
    {
        "name": "Farinha de Rosca",
        "unit": "g",
    },
    {
        "name": "Farinha branca",
        "unit": "g",
    }
]

for im in mock_ingredient_data:
    i = Ingredient(**im)
    session.add(i)

session.commit()

ingredients_query = session.query(Ingredient).all()
ingredients = []
for i in ingredients_query:
    ingredients.append(i)

mock_product_data = [
    {
        "name": "Bolo 1",
        "value": 10.0,
        "discount": 0.0,
        "ingredients": [
            ProductIngredient(**dict(amount=100, ingredient=ingredients[0])),
            ProductIngredient(**dict(amount=100, ingredient=ingredients[1])),
        ]
    },
    {
        "name": "Bolo 2",
        "value": 20.0,
        "discount": 0.0,
        "ingredients": [
            ProductIngredient(**dict(amount=100, ingredient_id=ingredients[1].id)),
            ProductIngredient(**dict(amount=100, ingredient_id=ingredients[2].id)),
        ]
    },
]

for pm in mock_product_data:
    p = Product(**pm)
    session.add(p)

session.commit()

mock_orders_data = [
    {
        "ref": "ORD001",
        "products": [
            OrderProduct(**dict(product_id=1, amount=2)),
            OrderProduct(**dict(product_id=2, amount=2)),
        ]
    },
    {
        "ref": "ORD002",
        "products": [
            OrderProduct(**dict(product_id=2, amount=2))
        ]
    },
]

for om in mock_orders_data:
    o = Order(**om)
    session.add(o)

session.commit()

pts = session.query(Product).options(subqueryload(Product.ingredients)).filter(Product.id == 1)

# query for product ingredient report
# qry = session.query(Ingredient, func.sum(ProductIngredient.amount).label('total')) \
#     .select_from(ProductIngredient).join(Ingredient) \
#     .filter(ProductIngredient.product_id.in_([1, ])) \
#     .group_by(ProductIngredient.ingredient_id)

# query for order ingredient report
stmt = session.query(Product, func.sum(OrderProduct.amount).label('total')) \
    .select_from(OrderProduct).join(Product) \
    .filter(OrderProduct.order_id.in_([1, 2])) \
    .group_by(Product.id)

stmt = stmt.subquery()

qry = session.query(Ingredient, func.sum(stmt.c.total * ProductIngredient.amount).label('total'), stmt.c.total) \
    .select_from(ProductIngredient).join(Ingredient) \
    .join(stmt, ProductIngredient.product_id == stmt.c.id) \
    .group_by(ProductIngredient.ingredient_id)

print("You'll need:")
for ingredient, total, ptotal in qry:
    unit = ingredient.unit
    print("\t* {:.2f} {} of {}".format(total, unit, ingredient.name))

    # for p in pts:
    #     for pi in p.ingredients:
    #         print(pi.ingredient)
    #         print(pi.amount)

    # for p in session.query(Product).options(subqueryload(Product.ingredients)).all():
    #     for pi in p.ingredients:
    #         print(pi.ingredient)
    #         print(pi.amount)
