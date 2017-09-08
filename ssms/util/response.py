format_response = lambda response: {
    "data": response,
}

format_error = lambda code, message, extra: dict(
    code=code,
    message=message,
    **extra
)

format_errors = lambda errors: dict(
    error=True,
    errors=[error for error in errors]
)
