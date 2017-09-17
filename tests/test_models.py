from sqlalchemy.schema import MetaData

import ssms.app
from ssms.models import ProductIngredient, Product, Ingredient, Admin, UsersEnum, Client

import pytest

import logging


@pytest.fixture(scope='module')
def logger():
    _default_logging_format = '[%(asctime)s][%(name)s]: %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        filename='./logging.log',
                        filemode='w',
                        format=_default_logging_format)
    logger = logging.getLogger(__name__)
    yield logger


@pytest.fixture(scope='module')
def db_session():
    metadata = MetaData(ssms.app.engine)
    metadata.reflect()
    session = ssms.app.Session()
    yield session
    metadata.drop_all()


def test_admin_model(db_session, logger):
    users_data = [
        {
            'email': 'fcgomes.92@gmail.com',
            'first_name': 'Fernando',
            'last_name': 'Coelho Gomes',
            'password': 'qwe123',
        },
        {
            'email': 'john@travolta.com',
            'first_name': 'John',
            'last_name': 'Travolta',
            'password': 'qwe123',
        },
        {
            'email': 'bruce@willis.net',
            'first_name': 'Bruce',
            'last_name': 'Willis',
            'password': 'qwe123',
        },
        {
            'email': 'sofia@turner.com',
            'first_name': 'Sofia',
            'last_name': 'Turner',
            'password': 'qwe123',
        }
    ]

    for user_data in users_data:
        user = Admin(**user_data)
        user.set_password(user.password)
        user.save()
        logger.info(user)

    logger.error(Admin.get_all())

    for idx, user in enumerate(list(Admin.get_all())):
        assert users_data[idx].get('email') == user.email
        assert users_data[idx].get('first_name') == user.first_name
        assert users_data[idx].get('last_name') == user.last_name
        assert UsersEnum.admin == user.user_type


def test_admin_model__get_by_email(db_session, logger):
    emails = [
        'fcgomes.92@gmail.com',
        'john@travolta.com',
        'bruce@willis.net',
        'sofia@turner.com',
    ]

    for email in emails:
        admin = Admin.get_by_email(email)

        assert admin is not None
        assert admin.email == email


def test_client_model(db_session, logger):
    users_data = [
        {
            'email': 'fcgomes.92@gmail.com',
            'first_name': 'Fernando',
            'last_name': 'Coelho Gomes',
            'password': 'qwe123',
        },
        {
            'email': 'john@travolta.com',
            'first_name': 'John',
            'last_name': 'Travolta',
            'password': 'qwe123',
        },
        {
            'email': 'bruce@willis.net',
            'first_name': 'Bruce',
            'last_name': 'Willis',
            'password': 'qwe123',
        },
        {
            'email': 'sofia@turner.com',
            'first_name': 'Sofia',
            'last_name': 'Turner',
            'password': 'qwe123',
        }
    ]

    for user_data in users_data:
        user = Client(**user_data)
        user.set_password(user.password)
        user.save()
        logger.info(user)

    logger.error(Client.get_all())

    for idx, user in enumerate(list(Client.get_all())):
        assert users_data[idx].get('email') == user.email
        assert users_data[idx].get('first_name') == user.first_name
        assert users_data[idx].get('last_name') == user.last_name
        assert UsersEnum.client == user.user_type


def test_ingredient_model(db_session, logger):
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
        i.save()

    all_ingredients = Ingredient.get_all()

    logger.info(all_ingredients)

    for idx, ingredient in enumerate(all_ingredients):
        logger.info(ingredient.code)
        assert mock_ingredient_data[idx].get('name') == ingredient.name
        assert mock_ingredient_data[idx].get('unit') == ingredient.unit


def test_product_model(db_session, logger):
    ingredients = Ingredient.get_all()

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
        assert mock_product_data[idx].get('ingredients') == product.ingredients
