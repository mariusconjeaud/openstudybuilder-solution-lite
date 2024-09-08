from starlette_context import context

from consumer_api.auth.models import Auth, User


def auth() -> Auth:
    """Retrieves authentication-related information from the request context as Auth object."""

    return context.get("auth")


def user() -> User:
    """Retrieves user information as User object, member of the Auth object in the request context."""

    return auth().user
