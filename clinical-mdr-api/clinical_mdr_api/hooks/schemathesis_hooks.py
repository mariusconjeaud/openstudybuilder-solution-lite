import schemathesis


def is_in_range(val):
    """Temporarily filter out all characters outside of 0x30...0xFFFF range"""
    val = str(val)
    return all(0x30 <= ord(char) <= 0xFFFF for char in val)


def is_desired_header(headers):
    if headers:
        for name, value in headers.items():
            if not is_in_range(name) or not is_in_range(value):
                return False
    return True


def is_desired_query_param(query_params):
    if query_params:
        for key, value in query_params.items():
            if not is_in_range(key) or not is_in_range(value):
                return False
    return True


@schemathesis.hooks.register
def before_generate_headers(_context, strategy):
    return strategy.filter(is_desired_header)


@schemathesis.hooks.register
def before_generate_query(_context, strategy):
    return strategy.filter(is_desired_query_param)
