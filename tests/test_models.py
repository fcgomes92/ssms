from collections import Counter

from ssms.models import Product, Ingredient, Admin, UsersEnum, Client, Order, ProductIngredient

from tests import util, conftest

import logging

logger = logging.getLogger(__name__)


def test_admin_model(db_session, conf_logger):
    users_data = [
        util.get_random_user_data() for idx in range(8)
    ]

    for user_data in users_data:
        user = Admin(**user_data)
        user.set_password(user.password)
        user.save()

    for idx, user in enumerate(list(Admin.get_all())):
        assert users_data[idx].get('email') == user.email
        assert users_data[idx].get('first_name') == user.first_name
        assert users_data[idx].get('last_name') == user.last_name
        assert UsersEnum.admin == user.user_type


def test_admin_model__get_by_email(db_session, conf_logger):
    users_data = [
        util.get_random_user_data() for idx in range(8)
    ]

    for user_data in users_data:
        user = Admin(**user_data)
        user.set_password(user.password)
        user.save()

    for user_data in users_data:
        admin = Admin.get_by_email(user_data.get('email'))
        assert admin is not None
        assert admin.email == user_data.get('email')


def test_client_model(db_session, conf_logger):
    users_data = [
        util.get_random_user_data() for idx in range(8)
    ]

    for user_data in users_data:
        user = Client(**user_data)
        user.set_password(user.password)
        user.save()

    for idx, user in enumerate(list(Client.get_all())):
        assert users_data[idx].get('email') == user.email
        assert users_data[idx].get('first_name') == user.first_name
        assert users_data[idx].get('last_name') == user.last_name
        assert UsersEnum.client == user.user_type


def test_ingredient_model(db_session, conf_logger):
    mock_ingredient_data = [
        util.get_random_ingredient_data() for idx in range(8)
    ]

    for im in mock_ingredient_data:
        i = Ingredient(**im)
        i.save()

    all_ingredients = Ingredient.get_all()

    for idx, ingredient in enumerate(all_ingredients):
        assert mock_ingredient_data[idx].get('name') == ingredient.name
        assert mock_ingredient_data[idx].get('unit') == ingredient.unit


def test_product_model(db_session, conf_logger):
    amount_of_ingredients = 4
    mock_product_data = [
        util.get_random_product_data_model(amount_of_ingredients) for idx in range(8)
    ]

    for pd in mock_product_data:
        p = Product(**pd)
        p.save()

    all_products = Product.get_all()

    for idx, product in enumerate(all_products):
        assert len(product.ingredients) == amount_of_ingredients
        assert mock_product_data[idx].get('name') == product.name
        assert mock_product_data[idx].get('value') == product.value
        assert mock_product_data[idx].get('discount') == product.discount
        assert Counter(mock_product_data[idx].get('ingredients')) == Counter(product.ingredients)


def test_order_model(db_session, conf_logger):
    amount_of_products = 2
    mock_order_data = [
        util.get_random_order_data_model(2) for idx in range(8)
    ]

    for order_data in mock_order_data:
        o = Order(**order_data)
        o.save()

    all_orders = Order.get_all()

    for idx, order in enumerate(all_orders):
        assert len(order.products) == amount_of_products
        assert mock_order_data[idx].get('client_id') == order.client_id
        assert Counter(mock_order_data[idx].get('products')) == Counter(order.products)


def test_client_model_delete(db_session, conf_logger):
    clients = Client.get_all()
    client = util.get_random_client()
    client.delete()

    assert client in clients
    assert client not in Client.get_all()
    assert Client.get_by_email(client.email) is None


def test_admin_model_delete(db_session, conf_logger):
    admins = Admin.get_all()
    admin = util.get_random_admin()
    admin.delete()

    assert admin in admins
    assert admin not in Admin.get_all()
    assert Admin.get_by_email(admin.email) is None


def test_ingredient_model_delete(db_session, conf_logger):
    ingredients = Ingredient.get_all()
    ingredient = util.get_random_ingredient()

    ingredient.delete()

    assert ingredient in ingredients
    assert ingredient not in Ingredient.get_all()
    assert Ingredient.get_by_id(ingredient.id) is None
    assert Ingredient.get_by_code(ingredient.code) is None


def test_product_model_delete(db_session, conf_logger):
    products = Product.get_all()
    product = util.get_random_product()

    product.delete()

    assert product in products
    assert product not in Product.get_all()
    assert Product.get_by_id(product.id) is None
    assert Product.get_by_code(product.code) is None


def test_product_ingredients_report(db_session, conf_logger):
    """
    Test the products ingredients report query
    Given a list of products ids, the query should return a list of ingredients used by each product and the total
    amount of ingredients used to produce the given products list.
    """
    # create some products and ingredients
    for idx in range(8):
        util.create_random_ingredient()

    products = [util.create_random_product(3) for idx in range(8)]
    products_ids = list(product.id for product in products)

    # repose model:
    # [(ingredient, total)...]
    products_ingredients_report = Product.report_ingredients(products_ids)

    test_report = {}

    for product in products:
        for pi in product.ingredients:
            if test_report.get(pi.ingredient_id, None):
                test_report[pi.ingredient_id]['total'] += pi.amount
            else:
                test_report[pi.ingredient_id] = dict(
                    total=pi.amount,
                    ingredient=pi.ingredient
                )

    for ingredient, total in products_ingredients_report:
        test_data = test_report[ingredient.id]
        assert test_data.get('total') == total
        assert test_data.get('ingredient') == ingredient


def test_order_model_delete(db_session, conf_logger):
    orders = Order.get_all()
    order = util.get_random_order()

    order.delete()

    assert order in orders
    assert order not in Order.get_all()
    assert Order.get_by_id(order.id) is None
    assert Order.get_by_code(order.code) is None


def test_order_products_report(db_session, conf_logger):
    """
    Test the order products report query
    Given a list of orders ids, the query should return a list of products used by each order and the total
    amount of products used to produce the given order list.
    """
    # create some products, ingredients and orders
    for idx in range(8):
        util.create_random_ingredient()

    for idx in range(8):
        util.create_random_product(3)

    orders = [util.create_random_order() for idx in range(8)]

    orders_ids = list(order.id for order in orders)

    # repose model:
    # [(product, total)...]
    order_products_report = Order.report_products(orders_ids=orders_ids)

    test_report = {}

    for order in orders:
        for op in order.products:
            if test_report.get(op.product_id, None):
                test_report[op.product_id]['total'] += op.amount
            else:
                test_report[op.product_id] = dict(
                    total=op.amount,
                    product=op.product
                )

    for product, total in order_products_report:
        test_data = test_report[product.id]
        assert test_data.get('total') == total
        assert test_data.get('product') == product


def test_order_ingredients_report(db_session, conf_logger):
    """
    Test the products ingredients report query
    Given a list of products ids, the query should return a list of ingredients used by each product and the total
    amount of ingredients used to produce the given products list.
    """
    # create some products, ingredients and orders
    for idx in range(2):
        util.create_random_product(amount_of_ingredients=2)

    orders = [util.create_random_order(amount_of_products=1) for idx in range(2)]

    orders_ids = list(order.id for order in orders)

    # repose model:
    # [(ingredient, total)...]
    order_ingredients_report = Order.report_ingredients(orders_ids=orders_ids)

    test_report = {}

    for order in orders:
        for op in order.products:
            for pi in op.product.ingredients:
                if test_report.get(pi.ingredient_id, None):
                    test_report[pi.ingredient_id]['total'] += pi.amount * op.amount
                else:
                    test_report[pi.ingredient_id] = dict(
                        total=pi.amount * op.amount,
                        ingredient=pi.ingredient
                    )

    for ingredient, total in order_ingredients_report:
        test_data = test_report[ingredient.id]
        assert test_data.get('total') == total
        assert test_data.get('ingredient') == ingredient
