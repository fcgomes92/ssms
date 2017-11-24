import mimesis

provider = mimesis.Generic()
provider.add_provider(mimesis.Personal)


def get_random_user_data():
    return {
        'email': provider.personal.email(),
        'first_name': provider.personal.name(),
        'last_name': provider.personal.surname(),
        'password': provider.personal.password(),
    }
