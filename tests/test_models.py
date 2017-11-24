from ssms.models import ProductIngredient, Product, Ingredient, Admin, UsersEnum, Client, Order, OrderProduct

from tests import util, conftest


def test_admin_model(db_session, logger):
    users_data = [
        util.get_random_user_data() for idx in range(8)
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
    users_data = [
        util.get_random_user_data() for idx in range(8)
    ]

    for user_data in users_data:
        user = Admin(**user_data)
        user.set_password(user.password)
        user.save()
        logger.info(user)

    for user_data in users_data:
        admin = Admin.get_by_email(user_data.get('email'))

        assert admin is not None
        assert admin.email == user_data.get('email')


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


def test_order_model(db_session, logger):
    products = Product.get_all()
    clients = Client.get_all()

    mock_order_data = [
        {
            "client_id": clients[0].id,
            "products": [
                OrderProduct(**dict(amount=2, product_id=products[0].id)),
                OrderProduct(**dict(amount=2, product_id=products[1].id)),
            ]
        },
        {
            "client_id": clients[0].id,
            "products": [
                OrderProduct(**dict(amount=5, product_id=products[0].id)),
                OrderProduct(**dict(amount=5, product_id=products[1].id)),
            ]
        }
    ]

    for order_data in mock_order_data:
        o = Order(**order_data)
        o.save()

    all_orders = Order.get_all()

    logger.info(all_orders)

    for idx, order in enumerate(all_orders):
        assert len(order.products) == 2
        assert mock_order_data[idx].get('client_id') == order.client_id


def test_cient_model_delete(db_session, logger):
    clients = Client.get_all()


def test_admin_model_delete(db_session, logger):
    admins = Admin.get_all()


def test_ingredient_model_delete(db_session, logger):
    ingredients = Ingredient.get_all()


def test_product_model_delete(db_session, logger):
    products = Product.get_all()


def test_order_model_delete(db_session, logger):
    orders = Order.get_all()

    for order in orders:
        order.delete()

    assert len(Order.get_all()) == 0
