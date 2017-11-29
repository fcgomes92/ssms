import falcon

from ssms.models import Admin, Ingredient, Product, ProductIngredient, Client, Order, OrderProduct, UsersEnum, User

from tests import util, conftest

import json

from logging import getLogger

logger = getLogger(__name__)


def test_users_auth__on_post(db_session, client, admin, user_client):
    # test auth for admins
    response = client.simulate_post(
        '/v1/users/auth/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK

    response = client.simulate_post(
        '/v1/users/auth/',
        headers={'Authorization': 'Token {}'.format(data)}
    )
    assert response.status == falcon.HTTP_OK

    # a request invalid token should return 401
    response = client.simulate_get(
        '/v1/users',
        headers={'Authorization': 'Token ABCD'}
    )

    assert response.status == falcon.HTTP_401

    # a request with no token should return 403
    response = client.simulate_get(
        '/v1/users',
    )

    assert response.status == falcon.HTTP_403

    response = client.simulate_get(
        '/v1/users',
        headers={'Authorization': 'Token {}'.format(data)}
    )

    assert response.status == falcon.HTTP_OK

    # =====================
    # test auth for clients
    response = client.simulate_post(
        '/v1/users/auth/',
        headers={'Authorization': 'Basic {}'.format(user_client.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK

    response = client.simulate_post(
        '/v1/users/auth/',
        headers={'Authorization': 'Token {}'.format(data)}
    )
    assert response.status == falcon.HTTP_OK

    # a request invalid token should return 401
    response = client.simulate_get(
        '/v1/users',
        headers={'Authorization': 'Token ABCD'}
    )

    assert response.status == falcon.HTTP_401

    # a request with no token should return 403
    response = client.simulate_get(
        '/v1/users',
    )

    assert response.status == falcon.HTTP_403

    response = client.simulate_get(
        '/v1/users',
        headers={'Authorization': 'Token {}'.format(data)}
    )

    assert response.status == falcon.HTTP_OK


def test_admins_list_resource__on_get(db_session, client, admin, user_client):
    response = client.simulate_get(
        '/v1/admins/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)

    for admin_data in data:
        admin = Admin.get_by_id(admin_data.get('id'))
        assert admin_data.get('email') == admin.email
        assert admin_data.get('first_name') == admin.first_name
        assert admin_data.get('last_name') == admin.last_name
        assert admin_data.get('code') == admin.code
        assert admin_data.get('password', None) is None
        assert admin_data.get('user_type') == UsersEnum.admin.value

    # tests a request using a client user
    response = client.simulate_get(
        '/v1/admins/',
        headers={'Authorization': 'Basic {}'.format(user_client.basic_password)}
    )

    assert response.status == falcon.HTTP_403


def test_clients_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/clients/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)

    for client_data in data:
        client = Client.get_by_id(client_data.get('id'))
        assert client_data.get('email') == client.email
        assert client_data.get('first_name') == client.first_name
        assert client_data.get('last_name') == client.last_name
        assert client_data.get('code') == client.code
        assert client_data.get('password', None) is None
        assert client_data.get('user_type') == UsersEnum.client.value


def test_ingredients_list_resource__on_post(db_session, client, admin):
    mock_data = util.get_random_ingredient_data()

    response = client.simulate_post(
        '/v1/ingredients/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert data.get('name') == mock_data.get('name')
    assert data.get('unit') == mock_data.get('unit')


def test_ingredients_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/ingredients/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)

    for ingredient_data in data:
        ingredient = Ingredient.get_by_id(ingredient_data.get('id'))
        assert ingredient_data.get('name') == ingredient.name
        assert ingredient_data.get('unit') == ingredient.unit


def test_ingredients_detail_resource__on_get(db_session, client, admin):
    ingredient = util.create_random_ingredient()

    user_token = admin.get_token()

    response = client.simulate_get(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Token {}'.format(user_token)},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert data.get('name') == ingredient.name
    assert data.get('unit') == ingredient.unit


def test_ingredients_detail_resource__on_delete(db_session, client, admin):
    ingredient = util.create_random_ingredient()

    response = client.simulate_delete(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Ingredient.get_by_id(data.get('id')) is None
    assert ingredient not in db_session


def test_ingredients_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    ingredient = util.create_random_ingredient()

    old_name = ingredient.name

    # the data to be updated
    mock_data = {"name": "onion"}

    # creates the request
    response = client.simulate_put(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('name') != old_name
    assert data.get('unit') == data.get('unit')

    # new mock to be updated
    mock_data = {"unit": "kg", }

    # creates a new request to update only the ingredient unit
    response = client.simulate_put(
        '/v1/ingredients/{ingredient_id}'.format(ingredient_id=ingredient.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    new_data = json.loads(response.content).get('data')

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert new_data.get('unit') == mock_data.get('unit')
    assert new_data.get('name') == ingredient.name
    assert new_data.get('id') == ingredient.id
    assert new_data.get('id') == data.get('id')
    assert new_data.get('id') == ingredient.id
    assert data.get('id') == ingredient.id
    assert new_data.get('code') == data.get('code')
    assert new_data.get('updated') != data.get('updated')
    assert new_data.get('created') == data.get('created')


def test_products_list_resource__on_post(db_session, client, admin):
    mock_data = util.get_random_product_data(4)

    response = client.simulate_post(
        '/v1/products/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')
    data.pop('id')

    assert response.status == falcon.HTTP_OK
    assert data.get('name') == mock_data.get('name')
    assert data.get('value') == mock_data.get('value')
    assert data.get('discount') == mock_data.get('discount')
    assert len(data.get('ingredients')) == 4

    for pi_data in data.get('ingredients'):
        pi = ProductIngredient.get_by_product_ingredient(product_id=pi_data.get('product_id'),
                                                         ingredient_id=pi_data.get('ingredient_id'))
        assert pi_data.get('amount') == pi.amount


def test_products_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/products/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)

    for product_data in data:
        product = Product.get_by_id(product_data.get('id'))
        assert product_data.get('name') == product.name
        assert product_data.get('value') == product.value
        assert product_data.get('discount') == product.discount

        for pi_data in product_data.get('ingredients'):
            pi = ProductIngredient.get_by_product_ingredient(product_id=pi_data.get('product_id'),
                                                             ingredient_id=pi_data.get('ingredient_id'))
            assert pi_data.get('amount') == pi.amount


def test_products_detail_resource__on_get(db_session, client, admin):
    mock_data = util.get_random_product_data_model(4)

    product = Product(**mock_data)
    product.save()

    response = client.simulate_get(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    data.pop('id', None)

    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('value') == mock_data.get('value')
    assert data.get('discount') == mock_data.get('discount')

    for pi_data in data.get('ingredients'):
        pi = ProductIngredient.get_by_product_ingredient(product_id=pi_data.get('product_id'),
                                                         ingredient_id=pi_data.get('ingredient_id'))
        assert pi_data.get('amount') == pi.amount


def test_products_detail_resource__on_delete(db_session, client, admin):
    mock_data = util.get_random_product_data_model(4)

    ingredients_ids = [pi.ingredient_id for pi in mock_data.get('ingredients')]

    product = Product(**mock_data)
    product.save()

    response = client.simulate_delete(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Product.get_by_id(data.get('id')) is None
    assert len(db_session.query(ProductIngredient).filter(Product.id == data.get('id')).all()) == 0
    assert len(ProductIngredient.get_by_product_id(product_id=product.id)) == 0
    assert product not in db_session

    for ingredient_id in ingredients_ids:
        assert Ingredient.get_by_id(ingredient_id) is not None


def test_products_detail_resource__on_put(db_session, client, admin):
    amount_of_ingredients = 4
    # creates the object to be updated
    original_mock_data = util.get_random_product_data_model(amount_of_ingredients)

    # saves the object to be updated instance
    product = Product(**original_mock_data)
    product.save()

    # the data to be updated
    mock_data = {
        "name": "{} {}".format(original_mock_data.get('name'), util.provider.text.word()),
        "value": float(util.provider.numbers.between()),
    }

    # creates the request
    response = client.simulate_put(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') == mock_data.get('name')
    assert data.get('name') != original_mock_data.get('name')
    assert data.get('value') != original_mock_data.get('value')
    assert data.get('value') == mock_data.get('value')
    assert len(data.get('ingredients')) == len(list(product.ingredients))

    # new mock to be updated
    mock_data = {
        "ingredients": [
            dict(ingredient_id=util.create_random_ingredient().id,
                 amount=float(util.provider.numbers.between(maximum=100)))
            for idx in range(amount_of_ingredients + 1)
        ]
    }

    # creates a new request to update only the product unit
    response = client.simulate_put(
        '/v1/products/{product_id}'.format(product_id=product.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the unit changed
    assert response.status == falcon.HTTP_200
    assert data.get('name') == product.name
    assert data.get('value') == product.value
    assert len(data.get('ingredients')) == amount_of_ingredients + 1

    # check if old relations were deleted!
    assert len(ProductIngredient.get_by_product_id(product_id=product.id)) == amount_of_ingredients + 1

    for pi_data in data.get('ingredients'):
        pi = ProductIngredient.get_by_product_ingredient(ingredient_id=pi_data.get('ingredient_id'),
                                                         product_id=pi_data.get('product_id'))
        assert pi_data.get('amount') == pi.amount
        assert pi_data.get('ingredient').get('name') == pi.ingredient.name


def test_products_ingredients_report_resource__on_get(db_session, client, admin):
    # create some products, ingredients and orders
    for idx in range(8):
        util.create_random_ingredient()

    products = [util.create_random_product(3) for idx in range(8)]
    products_ids = list(product.id for product in products)

    # creates the request
    response = client.simulate_get(
        '/v1/products/reports/ingredients',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(products_ids),
    )

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

    assert response.status == falcon.HTTP_200

    data = json.loads(response.content).get('data')

    assert isinstance(data, list)

    for report_data in data:
        test_data = test_report[report_data.get('ingredient_id')]
        assert test_data.get('total') == report_data.get('total')
        assert test_data.get('ingredient').name == report_data.get('ingredient').get('name')
        assert test_data.get('ingredient').unit == report_data.get('ingredient').get('unit')


def test_orders_list_resource__on_post(db_session, client, admin):
    amount_of_users = 1
    amount_of_products = 2

    mock_data = util.get_random_order_data(amount_of_clients=amount_of_users,
                                           amount_of_products=amount_of_products)

    user = User.get_by_id(mock_data.get('client_id'))

    response = client.simulate_post(
        '/v1/orders/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    client_data = data.get('client')

    order = Order.get_by_id(data.get('id'))

    assert response.status == falcon.HTTP_OK
    assert data.get('client_id') == order.client_id
    assert len(data.get('products')) == len(list(order.products))
    assert data.get('code') == order.code
    assert client_data.get('id') == user.id
    assert client_data.get('password') is None
    assert client_data.get('seed') is None


def test_orders_list_resource__on_get(db_session, client, admin):
    response = client.simulate_get(
        '/v1/orders/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)}
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_OK
    assert isinstance(data, list)

    for order_data in data:
        order = Order.get_by_id(order_data.get('id'))
        assert order_data.get('client_id') == order.client_id
        assert len(order_data.get('products')) == len(list(order.products))
        assert order_data.get('code') == order.code


def test_orders_detail_resource__on_get(db_session, client, admin):
    amount_of_users = 1
    amount_of_products = 2

    mock_data = util.get_random_order_data_model(amount_of_products=amount_of_products,
                                                 amount_of_clients=amount_of_users)

    order = Order(**mock_data)
    order.save()

    response = client.simulate_get(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert data.get('client_id') == mock_data.get('client_id')
    assert len(data.get('products')) == amount_of_products
    assert data.get('client_id') == order.client_id
    assert len(data.get('products')) == len(list(order.products))
    assert data.get('code') == order.code


def test_orders_detail_resource__on_put(db_session, client, admin):
    # creates the object to be updated
    amount_of_users = 1
    amount_of_products = 2

    original_mock_data = util.get_random_order_data_model(amount_of_products=amount_of_products,
                                                          amount_of_clients=amount_of_users)

    products = Product.get_all()

    # saves the object to be updated instance
    order = Order(**original_mock_data)
    order.save()

    # the data to be updated
    mock_data = {"products": [
        {"amount": 2, "product_id": products[0].id},
    ]}

    # creates the request
    response = client.simulate_put(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    # assert that only the name changed
    assert response.status == falcon.HTTP_200
    assert len(data.get('products')) == len(mock_data.get('products'))
    assert data.get('products')[0].get('amount') == 2

    # new mock to be updated
    mock_data = {"products": [
        {"amount": 10, "product_id": products[0].id, },
    ]}

    # creates a new request to update only the client unit
    response = client.simulate_put(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert len(data.get('products')) == len(mock_data.get('products'))
    assert data.get('products')[0].get('amount') == 10


def test_orders_detail_resource__on_delete(db_session, client, admin):
    # creates the object to be updated
    amount_of_users = 1
    amount_of_products = 2

    original_mock_data = util.get_random_order_data_model(amount_of_products=amount_of_products,
                                                          amount_of_clients=amount_of_users)

    order = Order(**original_mock_data)
    order.save()

    # creates the request
    response = client.simulate_delete(
        '/v1/orders/{order_id}'.format(order_id=order.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert Order.get_by_id(data.get('id')) is None
    assert len(db_session.query(OrderProduct).filter(Order.id == data.get('id')).all()) == 0
    assert len(Ingredient.get_all()) > 0
    assert order not in db_session


def test_orders_products_report_resource__on_get(db_session, client, admin):
    # create some products, ingredients and orders
    for idx in range(2):
        util.create_random_product(amount_of_ingredients=2)

    orders = [util.create_random_order(amount_of_products=1) for idx in range(2)]

    orders_ids = list(order.id for order in orders)

    # creates the request
    response = client.simulate_get(
        '/v1/orders/reports/products',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(orders_ids),
    )

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

    assert response.status == falcon.HTTP_200

    data = json.loads(response.content).get('data')

    assert isinstance(data, list)

    for report_data in data:
        test_data = test_report[report_data.get('product_id')]
        assert test_data.get('total') == report_data.get('total')
        assert test_data.get('product').name == report_data.get('product').get('name')
        assert test_data.get('product').value == report_data.get('product').get('value')
        assert len(test_data.get('product').ingredients) == len(report_data.get('product').get('ingredients'))


def test_orders_ingredients_report_resource__on_get(db_session, client, admin):
    # create some products, ingredients and orders
    for idx in range(2):
        util.create_random_product(amount_of_ingredients=2)

    orders = [util.create_random_order(amount_of_products=1) for idx in range(2)]

    orders_ids = list(order.id for order in orders)

    # creates the request
    response = client.simulate_get(
        '/v1/orders/reports/ingredients',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(orders_ids),
    )

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

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert isinstance(data, list)

    for report_data in data:
        test_data = test_report[report_data.get('ingredient_id')]
        assert test_data.get('total') == report_data.get('total')
        assert test_data.get('ingredient').name == report_data.get('ingredient').get('name')
        assert test_data.get('ingredient').unit == report_data.get('ingredient').get('unit')


def test_clients_list_resource__on_post(db_session, client, admin):
    mock_data = util.get_random_user_data()

    response = client.simulate_post(
        '/v1/clients/',
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    user_client = User.get_by_id(data.get('id'))

    assert response.status == falcon.HTTP_OK
    assert data.get('email') == user_client.email
    assert data.get('first_name') == user_client.first_name
    assert data.get('last_name') == user_client.last_name
    assert data.get('user_type') == user_client.user_type.value
    assert data.get('code') == user_client.code
    assert data.get('password', None) is None
    assert data.get('seed', None) is None


def test_clients_detail_resource__on_get(db_session, client, admin):
    mock_data = util.get_random_user_data()

    user_client = Client(**mock_data)
    user_client.save()

    response = client.simulate_get(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    data = json.loads(response.content).get('data')

    user_client = User.get_by_id(data.get('id'))

    assert response.status == falcon.HTTP_OK
    assert data.get('email') == user_client.email
    assert data.get('first_name') == user_client.first_name
    assert data.get('last_name') == user_client.last_name
    assert data.get('user_type') == user_client.user_type.value
    assert data.get('code') == user_client.code
    assert data.get('password', None) is None
    assert data.get('seed', None) is None


def test_clients_detail_resource__on_put(db_session, client, admin):
    original_mock_data = util.get_random_user_data()

    # saves the object to be updated instance
    user_client = Client(**original_mock_data)
    user_client.set_password(original_mock_data.get('password'))
    user_client.save()

    mock_data = {"first_name": "{} {}".format(original_mock_data.get('first_name'),
                                              util.provider.personal.name()), }

    response = client.simulate_put(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert data.get('first_name') == mock_data.get('first_name')
    assert data.get('first_name') != original_mock_data.get('first_name')
    assert response.status == falcon.HTTP_OK
    assert data.get('email') == user_client.email
    assert data.get('first_name') == user_client.first_name
    assert data.get('last_name') == user_client.last_name
    assert data.get('user_type') == user_client.user_type.value
    assert data.get('code') == user_client.code
    assert data.get('password', None) is None
    assert data.get('seed', None) is None

    mock_data = {"last_name": "{} {}".format(original_mock_data.get('last_name'),
                                             util.provider.personal.name()), }

    response = client.simulate_put(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
        body=json.dumps(mock_data)
    )

    data = json.loads(response.content).get('data')

    assert response.status == falcon.HTTP_200
    assert data.get('last_name') == mock_data.get('last_name')
    assert data.get('last_name') != original_mock_data.get('last_name')
    assert data.get('email') == user_client.email
    assert data.get('first_name') == user_client.first_name
    assert data.get('last_name') == user_client.last_name
    assert data.get('user_type') == user_client.user_type.value
    assert data.get('code') == user_client.code
    assert data.get('password', None) is None
    assert data.get('seed', None) is None


def test_clients_detail_resource__on_delete(db_session, client, admin):
    # creates the object to be updated
    original_mock_data = util.get_random_user_data()

    # saves the object to be updated instance
    user_client = Client(**original_mock_data)
    user_client.set_password(original_mock_data.get('password'))
    user_client.save()

    user_client_db = Client.get_by_email(user_client.email)

    assert user_client_db is not None

    # creates the request
    response = client.simulate_delete(
        '/v1/clients/{client_id}'.format(client_id=user_client.id),
        headers={'Authorization': 'Basic {}'.format(admin.basic_password)},
    )

    json.loads(response.content).get('data')

    user_client_db = Client.get_by_email(user_client.email)

    assert user_client not in db_session
    assert user_client_db is None
