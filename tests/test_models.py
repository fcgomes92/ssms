import ssms
from ssms.models import User


def test_user_model():
    user_data = [
        {
            'email': 'fcgomes.92@gmail.com',
            'first_name': 'Fernando',
            'last_name': 'Coelho Gomes'
        },
        {
            'email': 'john@travolta.com',
            'first_name': 'John',
            'last_name': 'Travolta'
        },
        {
            'email': 'bruce@willis.net',
            'first_name': 'Bruce',
            'last_name': 'Willis'
        },
        {
            'email': 'sofia@turner.com',
            'first_name': 'Sofia',
            'last_name': 'Turner'
        }
    ]

    for user in user_data:
        schema = User.schema()
        user, errors = schema.load(user)
        dumped_data, errors = schema.dump(user)
        user.save()

    for idx, user in enumerate(list(User.query({}))):
        assert user_data[idx].get('email') == user.email
        assert user_data[idx].get('first_name') == user.first_name
        assert user_data[idx].get('last_name') == user.last_name
