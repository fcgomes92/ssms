import argparse

parser = argparse.ArgumentParser("Create an Admin User")
parser.add_argument('-e', '--email', metavar='email', type=str, default='admin@admin.com')
parser.add_argument('-p', '--password', metavar='password', type=str, default='123456')


def main(email, password):
    from ssms.models import Admin

    first_name = last_name = email.split('@')[0]

    admin = Admin(**dict(
        email=email,
        first_name=first_name,
        last_name=last_name,
    ))
    admin.set_password(password)

    print('=' * 80)
    print(f"Creating user {admin}")
    print('=' * 80)

    admin.save()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.email, args.password)
