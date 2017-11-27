from ssms.models import ProductIngredient, OrderProduct, Ingredient, Client, Product, Admin, Order

import random

import mimesis

provider = mimesis.Generic()
provider.add_provider(mimesis.Personal)
provider.add_provider(mimesis.Food)
provider.add_provider(mimesis.Numbers)
provider.add_provider(mimesis.Text)


def get_random_ingredients(amount):
    ingredients = Ingredient.get_all()
    return random.sample(ingredients, amount)


def get_random_ingredient():
    ingredients = Ingredient.get_all()
    return random.choice(ingredients)


def get_random_products(amount):
    products = Product.get_all()
    return random.sample(products, amount)


def get_random_product():
    products = Product.get_all()
    return random.choice(products)


def get_random_order():
    orders = Order.get_all()
    return random.choice(orders)


def get_random_client():
    clients = Client.get_all()
    return random.choice(clients)


def get_random_admin():
    admins = Admin.get_all()
    return random.choice(admins)


def get_random_user_data():
    return {
        'email': provider.personal.email(),
        'first_name': provider.personal.name(),
        'last_name': provider.personal.surname(),
        'password': provider.personal.password(),
    }


def get_random_ingredient_data():
    return {
        "name": provider.food.fruit(),
        "unit": 'g',
    }


def get_random_product_data_model(amount_of_ingredients):
    for idx in range(amount_of_ingredients):
        create_random_ingredient()

    return {
        "name": provider.food.dish(),
        "value": provider.numbers.between(1.0, 30.0),
        "discount": 0.0,
        "ingredients": [
            ProductIngredient(**dict(
                amount=float(provider.numbers.between(maximum=100)),
                ingredient_id=ingredient.id))
            for ingredient in get_random_ingredients(amount_of_ingredients)
        ],
    }


def get_random_product_data(amount_of_ingredients=4):
    for idx in range(amount_of_ingredients):
        create_random_ingredient()

    return {
        "name": provider.food.dish(),
        "value": provider.numbers.between(1.0, 30.0),
        "discount": 0.0,
        "ingredients": [
            dict(amount=provider.numbers.between(), ingredient_id=ingredient.id)
            for ingredient in get_random_ingredients(amount_of_ingredients)
        ],
    }


def get_random_order_data_model(amount_of_products=4, amount_of_clients=1):
    for idx in range(amount_of_clients):
        create_random_client()

    for idx in range(amount_of_products):
        create_random_product()

    return {
        "client_id": get_random_client().id,
        "products": [
            OrderProduct(**dict(amount=provider.numbers.between(), product_id=product.id)) for product in
            get_random_products(amount_of_products)
        ]
    }


def get_random_order_data(amount_of_products=4, amount_of_clients=1):
    for idx in range(amount_of_clients):
        create_random_client()

    for idx in range(amount_of_products):
        create_random_product()

    return {
        "client_id": get_random_client().id,
        "products": [
            dict(amount=provider.numbers.between(), product_id=product.id) for product in get_random_products(2)
        ]
    }


def create_random_ingredient():
    data = get_random_ingredient_data()
    ingredient = Ingredient(**data)
    ingredient.save()
    return ingredient


def create_random_product(amount_of_ingredients=8):
    data = get_random_product_data_model(amount_of_ingredients)
    product = Product(**data)
    product.save()

    return product


def create_random_client():
    data = get_random_user_data()
    client = Client(**data)
    client.save()
    return client


def create_random_order(amount_of_products=4, amount_of_clients=1):
    data = get_random_order_data_model(amount_of_products, amount_of_clients)
    order = Order(**data)
    order.save()

    return order
