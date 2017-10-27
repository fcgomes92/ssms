import jwt

from datetime import datetime, timedelta


def encode(data):
    from ssms.app import JWT_ALGORITHM, JWT_SECRET_KEY
    payload = dict(
        data=data,
        exp=datetime.utcnow() + timedelta(hours=24),
    )
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode(data):
    from ssms.app import JWT_ALGORITHM, JWT_SECRET_KEY
    payload = jwt.decode(data, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM, ])
    return payload.get('data', None)
