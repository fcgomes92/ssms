_base_error = '{} needs to define a {}!'


def assert_base_model(f):
    def wrapper(*args, **kwargs):
        # gets the instance or the class reference
        instance = args[0]

        # since no static method is allowed here,
        # the first arg will always be the desired instance
        new_args = args[1:]

        # verification code for the base model
        collection = getattr(instance, 'collection', None)
        schema = getattr(instance, 'schema', None)

        assert collection is not None, Exception(
            _base_error.format(instance.__class__.__name__, 'collection'))
        assert schema is not None, Exception(
            _base_error.format(instance.__class__.__name__, 'schema'))
        return f(instance, *new_args, **kwargs)
    return wrapper
