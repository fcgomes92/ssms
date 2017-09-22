def format_response(response):
    return {
        "data": response,
    }


def format_error(code, message, extra):
    return dict(
        code=code,
        message=message,
        **extra
    )


def format_errors(errors):
    return dict(
        error=True,
        errors=[error for error in errors]
    )
