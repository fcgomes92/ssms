from collections import Counter

from ssms.models import Product, Ingredient, Admin, UsersEnum, Client, Order

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

    logger.info(Admin.get_all())

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

    logger.error(Client.get_all())

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

    logger.info(all_ingredients)

    for idx, ingredient in enumerate(all_ingredients):
        assert mock_ingredient_data[idx].get('name') == ingredient.name
        assert mock_ingredient_data[idx].get('unit') == ingredient.unit


def test_product_model(db_session, conf_logger):
    mock_product_data = [
        util.get_random_product_data() for idx in range(8)
    ]

    for product_data in mock_product_data:
        p = Product(**product_data)
        p.save()

    all_products = Product.get_all()

    logger.info(all_products)

    for idx, product in enumerate(all_products):
        assert len(product.ingredients) == 2
        assert mock_product_data[idx].get('name') == product.name
        assert mock_product_data[idx].get('value') == product.value
        assert mock_product_data[idx].get('discount') == product.discount
        assert Counter(mock_product_data[idx].get('ingredients')) == Counter(product.ingredients)


def test_order_model(db_session, conf_logger):
    mock_order_data = [
        util.get_random_order_data() for idx in range(8)
    ]

    for order_data in mock_order_data:
        o = Order(**order_data)
        o.save()

    all_orders = Order.get_all()

    logger.info(all_orders)

    for idx, order in enumerate(all_orders):
        assert len(order.products) == 2
        assert mock_order_data[idx].get('client_id') == order.client_id
        assert Counter(mock_order_data[idx].get('products')) == Counter(order.products)


def test_cient_model_delete(db_session, conf_logger):
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

    logger.info("DELETED INGREDIENT: {}".format(ingredient))

    ingredient.delete()

    assert ingredient in ingredients
    assert ingredient not in Ingredient.get_all()
    assert Ingredient.get_by_id(ingredient.id) is None
    assert Ingredient.get_by_code(ingredient.code) is None


def test_product_model_delete(db_session, conf_logger):
    products = Product.get_all()
    product = util.get_random_product()

    logger.info("DELETED PRODUCT: {}".format(product))

    product.delete()

    assert product in products
    assert product not in Product.get_all()
    assert Product.get_by_id(product.id) is None
    assert Product.get_by_code(product.code) is None


def test_order_model_delete(db_session, conf_logger):
    orders = Order.get_all()
    order = util.get_random_order()

    logger.info("DELETED ORDER: {}".format(order))

    order.delete()

    assert order in orders
    assert order not in Order.get_all()
    assert Order.get_by_id(order.id) is None
    assert Order.get_by_code(order.code) is None
