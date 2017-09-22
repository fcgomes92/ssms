from sqlalchemy.schema import MetaData

import falcon
from falcon import testing

import pytest

import ssms.app
from ssms.models import Admin, Ingredient, Product, ProductIngredient, Client, Order, OrderProduct

import json

from logging import getLogger

logger = getLogger(__name__)


@pytest.fixture
def client():
    api = ssms.app.create_app()
    return testing.TestClient(api)


@pytest.fixture(scope='module')
def db_session():
    metadata = MetaData(ssms.app.engine)
    metadata.reflect()
    session = ssms.app.Session()
    yield session
    metadata.drop_all()


@pytest.fixture(scope='module')
def admin():
    admin = Admin(
        **dict(
            email='admin@test.com',
            first_name='Admin',
            last_name='Admin'
        )
    )
    admin.set_password('admin')
    admin.save()
    yield admin


def test_admins_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/admins/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_ingredients_list_resource__on_post(db_session, client, admin):
    mock_data = {
        "name": 'apple',
        "unit": 'g',
    }

    response = client.simulate_post(
        '/v1/ingredients/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id')
    data.pop("code")
    data.pop('created', None)
    data.pop('updated', None)

    assert response.status == falcon.HTTP_OK
    assert data == mock_data


def test_ingredients_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/ingredients/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_ingredients_detail_resource__on_get(db_session, client, admin):
    mock_data = {
        "name": 'apple',
        "unit": 'g',
    }

    ingredient = Ingredient(**mock_data)
    ingredient.save()

    response = client.simulate_get(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    data.pop('id', None)
    data.pop('code', None)
    data.pop('created', None)
    data.pop('updated', None)

    assert response.status == falcon.HTTP_200
    assert data == mock_data


def test_ingredients_detail_resource__on_delete(db_session, client, admin):
    mock_data = {
        "name": 'apple to delete',
        "unit": 'g',
    }

    ingredient = Ingredient(**mock_data)
    ingredient.save()

    response = client.simulate_delete(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Ingredient.get_by_id(data.get('id')) is None
    assert ingredient not in db_session


def test_ingredients_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    original_mock_data = {
        "name": 'apple',
        "unit": 'g',
    }

    # saves the object to be updated instance
    ingredient = Ingredient(**original_mock_data)
    ingredient.save()

    # the data to be updated
    mock_data = {"name": "onion", }

    # creates the request
    response = client.simulate_put(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('name') != original_mock_data.get('name')
    assert data.get('unit') == data.get('unit')

    # redefines the new ingredient
    ingredient, errors = Ingredient.schema().load(data=data)

    # new mock to be updated
    mock_data = {"unit": "kg", }

    # creates a new request to update only the ingredient unit
    response = client.simulate_put(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id', None)

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert data.get('unit') == mock_data.get('unit')


def test_products_list_resource__on_post(db_session, client, admin):
    mock_data = {
        "name": "Cake 1",
        "value": 10.0,
        "discount": 0,
        "ingredients": [
            {"amount": 100, "ingredient_id": 1},
            {"amount": 100, "ingredient_id": 2},
        ]
    }

    response = client.simulate_post(
        '/v1/products/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id')

    assert response.status == falcon.HTTP_OK
    assert data.get('name') == mock_data.get('name')
    assert data.get('value') == mock_data.get('value')
    assert data.get('discount') == mock_data.get('discount')
    assert len(data.get('ingredients')) == 2

    for pi in data.get('ingredients'):
        assert pi.get('amount') == 100


def test_products_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/products/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_products_detail_resource__on_get(db_session, client, admin):
    mock_data = {
        "name": "Cake 2",
        "value": 10.0,
        "discount": 0,
        "ingredients": [
            ProductIngredient(**{"amount": 100, "ingredient_id": 1}),
            ProductIngredient(**{"amount": 100, "ingredient_id": 2}),
        ]
    }

    product = Product(**mock_data)
    product.save()

    response = client.simulate_get(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    data.pop('id', None)

    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('value') == mock_data.get('value')
    assert data.get('discount') == mock_data.get('discount')
    assert len(data.get('ingredients')) == 2

    for pi in data.get('ingredients'):
        assert pi.get('amount') == 100


def test_products_detail_resource__on_delete(db_session, client):
    mock_data = {
        "name": "Delete Cake",
        "value": 10.0,
        "discount": 0,
        "ingredients": [
            ProductIngredient(**{"amount": 100, "ingredient_id": 1}),
            ProductIngredient(**{"amount": 100, "ingredient_id": 2}),
        ]
    }

    product = Product(**mock_data)
    product.save()

    response = client.simulate_delete(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Product.get_by_id(data.get('id')) is None
    assert len(db_session.query(ProductIngredient).filter(Product.id == data.get('id')).all()) == 0
    assert len(Ingredient.get_all()) > 0
    assert product not in db_session


def test_products_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    original_mock_data = {
        "name": "Cake 3",
        "value": 10.0,
        "discount": 0,
        "ingredients": [
            ProductIngredient(**{"amount": 100, "ingredient_id": 1}),
            ProductIngredient(**{"amount": 100, "ingredient_id": 2}),
        ]
    }

    # saves the object to be updated instance
    product = Product(**original_mock_data)
    product.save()

    # the data to be updated
    mock_data = {"name": "onion", }

    # creates the request
    response = client.simulate_put(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('name') != original_mock_data.get('name')

    # redefines the new product
    product, errors = Product.schema().load(data=data)

    # new mock to be updated
    mock_data = {"value": 20.0, }

    # creates a new request to update only the product unit
    response = client.simulate_put(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id', None)

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') != original_mock_data.get('name')
    assert data.get('value') != original_mock_data.get('value')
    assert data.get('value') == mock_data.get('value')
    assert len(data.get('ingredients')) == 2

    for pi in data.get('ingredients'):
        assert pi.get('amount') == 100


def test_clients_list_resource__on_post(db_session, client, admin):
    mock_data = {
        "email": "client_post@test.com",
        "first_name": "Client Post",
        "last_name": "Client Post",
        "password": "qwe123"
    }

    response = client.simulate_post(
        '/v1/clients/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id', None)
    data.pop("code", None)
    data.pop('created', None)
    data.pop('updated', None)

    assert response.status == falcon.HTTP_OK
    # assert data == mock_data


def test_clients_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/clients/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_clients_detail_resource__on_get(db_session, client, admin):
    mock_data = {
        "email": "client_get@test.com",
        "first_name": "Client Get",
        "last_name": "Client Get",
        "password": "qwe123"
    }

    user_client = Client(**mock_data)
    user_client.save()

    response = client.simulate_get(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    data.pop('id', None)
    data.pop('code', None)
    data.pop('created', None)
    data.pop('updated', None)

    assert response.status == falcon.HTTP_200
    # assert data == mock_data


def test_clients_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    original_mock_data = {
        "email": "client_put@test.com",
        "first_name": "Client Put",
        "last_name": "Client Put",
        "password": "qwe123"
    }

    # saves the object to be updated instance
    user_client = Client(**original_mock_data)
    user_client.set_password(original_mock_data.get('password'))
    user_client.save()

    # the data to be updated
    mock_data = {"first_name": "Client Put Updated", }

    # creates the request
    response = client.simulate_put(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert data.get('first_name') == mock_data.get('first_name')
    assert data.get('first_name') != original_mock_data.get('first_name')

    # new mock to be updated
    mock_data = {"last_name": "Client Put Updated", }

    # creates a new request to update only the client unit
    response = client.simulate_put(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id', None)

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert data.get('last_name') == mock_data.get('last_name')
    assert data.get('last_name') != original_mock_data.get('last_name')


def test_clients_detail_resource__on_delete(db_session, client, admin):
    # creates the object to be updated
    original_mock_data = {
        "email": "client_delete@test.com",
        "first_name": "Client Delete",
        "last_name": "Client Delete",
        "password": "qwe123"
    }

    # saves the object to be updated instance
    user_client = Client(**original_mock_data)
    user_client.set_password(original_mock_data.get('password'))
    user_client.save()

    user_client_db = db_session.query(Client).filter(Client.email == original_mock_data.get('email')).first()

    assert user_client_db is not None

    # creates the request
    response = client.simulate_delete(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    logger.info(data)

    user_client_db = db_session.query(Client).filter(Client.email == original_mock_data.get('email')).first()

    assert user_client_db is None


def test_orders_list_resource__on_post(db_session, client):
    user = Client.get_all()[0]
    products = Product.get_all()

    mock_data = {
        "client_id": user.id,
        "products": [
            {"amount": 2, "product_id": products[0].id, },
            {"amount": 2, "product_id": products[1].id, },
        ]
    }

    response = client.simulate_post(
        '/v1/orders/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    logger.debug(data)

    data.pop('id', None)
    data.pop("code", None)
    data.pop('created', None)
    data.pop('updated', None)

    assert response.status == falcon.HTTP_OK
    assert len(Order.get_all()) == 1
    assert data.get('client').get('id') == user.id


def test_orders_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/orders/',
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)


def test_orders_detail_resource__on_get(db_session, client, admin):
    user = Client.get_all()[0]
    products = Product.get_all()

    mock_data = {
        "client_id": user.id,
        "products": [
            OrderProduct(**{"amount": 2, "product_id": products[0].id, }),
            OrderProduct(**{"amount": 2, "product_id": products[1].id, }),
        ]
    }

    order = Order(**mock_data)
    order.save()

    response = client.simulate_get(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert data.get('client_id') == mock_data.get('client_id')
    assert len(data.get('products')) == 2


def test_orders_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    user = Client.get_all()[0]
    products = Product.get_all()

    original_mock_data = {
        "client_id": user.id,
        "products": [
            OrderProduct(**{"amount": 2, "product_id": products[0].id, }),
            OrderProduct(**{"amount": 2, "product_id": products[1].id, }),
        ]
    }
    # saves the object to be updated instance
    order = Order(**original_mock_data)
    order.save()

    # the data to be updated
    mock_data = {"products": [
        {"amount": 1, "product_id": products[0].id, },
    ]}

    # creates the request
    response = client.simulate_put(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert len(data.get('products')) == 1
    assert data.get('products')[0].get('amount') == 1

    # new mock to be updated
    mock_data = {"products": [
        {"amount": 10, "product_id": products[0].id, },
    ]}

    # creates a new request to update only the client unit
    response = client.simulate_put(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert len(data.get('products')) == 1
    assert data.get('products')[0].get('amount') == 10


def test_orders_detail_resource__on_delete(db_session, client, admin):
    # creates the object to be updated
    user = Client.get_all()[0]
    products = Product.get_all()

    original_mock_data = {
        "client_id": user.id,
        "products": [
            OrderProduct(**{"amount": 2, "product_id": products[0].id, }),
            OrderProduct(**{"amount": 2, "product_id": products[1].id, }),
        ]
    }

    order = Order(**original_mock_data)
    order.save()

    # creates the request
    response = client.simulate_delete(
        '/v1/orders/{client_id}'.format(client_id=order.id),
        headers={'Authorization': 'Basic YWRtaW5AdGVzdC5jb206YWRtaW4='},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Order.get_by_id(data.get('id')) is None
    assert len(db_session.query(OrderProduct).filter(Order.id == data.get('id')).all()) == 0
    assert len(Ingredient.get_all()) > 0
    assert order not in db_session
