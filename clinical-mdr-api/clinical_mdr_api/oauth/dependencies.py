import logging
from collections.abc import Sequence

import pydantic
from authlib.integrations.starlette_client import OAuth
from authlib.jose.errors import JoseError
from fastapi import Depends, Request, Security
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from opencensus.trace import execution_context
from opencensus.trace.tracer import Tracer
from pydantic import ValidationError
from starlette_context import context

from clinical_mdr_api.exceptions import ForbiddenException, NotAuthenticatedException
from clinical_mdr_api.oauth import config
from clinical_mdr_api.oauth.jwk_service import JWKService
from clinical_mdr_api.oauth.models import AccessTokenClaims, UserInfo

log = logging.getLogger(__name__)

oauth = OAuth()
oidc_client = oauth.register(
    "default",
    server_metadata_url=config.OIDC_METADATA_URL,
)

jwks_service = JWKService(
    oidc_client, audience=config.OAUTH_APP_ID, leeway_seconds=config.JWT_LEEWAY_SECONDS
)

oauth_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=config.OAUTH_AUTHORIZATION_URL,
    tokenUrl=config.OAUTH_TOKEN_URL,
    scopes=config.OUR_SCOPES,
)


async def validate_token(
    security_scopes: SecurityScopes,
    request: Request,
    token: str = Depends(oauth_scheme),
) -> AccessTokenClaims:
    """
    Decodes and validates JWT token claims.

    Args:
        security_scopes (SecurityScopes): The security scopes required for the request.
        request (Request): The request object.
        token (str): The JWT access token.

    Returns:
        AccessTokenClaim: The decoded and validated JWT token claims.

    Raises:
        NotAuthenticatedException: If the token is invalid.
        ValidationError: If the JWT claims are invalid.

    """
    try:
        jwt_claims = await jwks_service.validate_jwt(token)
        request.state.id_claims = acc_claims = AccessTokenClaims.parse_obj(jwt_claims)

    except JoseError as exc:
        log.info("%s: %s", exc.error, exc.description)
        raise NotAuthenticatedException(
            f"Token validation error: {exc.description or exc.error}", security_scopes
        ) from exc

    except ValidationError as exc:
        log.info(str(exc))
        raise NotAuthenticatedException(
            "Model validation error", security_scopes
        ) from exc

    _update_context(acc_claims)

    _validate_scopes(security_scopes, acc_claims)

    log.debug("Valid token with claims: %s", acc_claims)

    return acc_claims


def _validate_scopes(
    security_scopes: SecurityScopes, claims: AccessTokenClaims
) -> None:
    """
    Checks if all items of required scopes are within claimed scopes.

    Args:
        security_scopes (SecurityScopes): The security scopes required for the request.
        claims (AccessTokenClaims): The decoded JWT token claims.

    Returns:
        None

    Raises:
        NotAuthenticatedException: If the required scopes are not within the claimed scopes.
    """
    if not security_scopes.scopes:
        return

    if not claims.scp:
        raise NotAuthenticatedException("No scopes claimed", security_scopes)

    for scope in security_scopes.scopes:
        if scope not in claims.scp:
            NotAuthenticatedException(
                f"Scope '{scope}' is not within claimed scopes: {claims.scp}",
                security_scopes,
            )


def _update_context(claims: AccessTokenClaims) -> None:
    """
    Saves some attributes from access token claims to context.

    Args:
        claims (AccessTokenClaims): The decoded JWT token claims.

    Returns:
        None
    """
    # Attributes to current tracing span
    tracer: Tracer = execution_context.get_opencensus_tracer()
    tracer.add_attribute_to_current_span(
        "ai.user.authUserId", claims.preferred_username
    )
    tracer.add_attribute_to_current_span("ai.user.accountId", claims.oid or claims.sub)
    tracer.add_attribute_to_current_span("ai.device.id", claims.azp)

    # Save to context
    context["access_token_claims"] = claims


async def get_authenticated_user_info(
    request: Request,
    token_claims: AccessTokenClaims = Security(validate_token),
) -> UserInfo | None:
    """
    Returns UserInfo object populated from id token claims, or None on validation error

    Args:
        request (Request): The request object.
        token_claims (AccessTokenClaim): The decoded and validated JWT token claims.

    Returns:
        UserInfo | None: The populated UserInfo object, or None if there was a validation error.
    """
    data = token_claims.dict(exclude_unset=True)

    if token_claims.preferred_username:
        data.setdefault("email", token_claims.preferred_username)
        data.setdefault("initials", token_claims.preferred_username.split("@", 1)[0])
        data.setdefault("username", token_claims.preferred_username)
        data.setdefault("name", token_claims.name)

    try:
        request.state.user_info = user_info = UserInfo(**data)

    except pydantic.ValidationError as exc:
        log.debug(
            "Could not create UserInfo object, perhaps missing claims: %s", str(exc)
        )
        user_info = None

    context["user_info"] = user_info
    return user_info


if config.OAUTH_ENABLED and config.OAUTH_RBAC_ENABLED:

    class RequiresAnyRole:
        """
        Dependency checks that required roles are all present in the access token claims.

        Args:
            roles: A sequence of roles required for the request.
        """

        def __init__(self, roles: Sequence[str]):
            self.required_roles = set(roles)

        def __call__(self, claims: AccessTokenClaims = Depends(validate_token)):
            _require_any_role(
                claimed_roles=claims.roles, required_roles=self.required_roles
            )

    def require_any_role(required_roles: Sequence[str]):
        """
        Checks that required roles are all present in the access token claims.

        Args:
            required_roles (Sequence[str]): A sequence of roles required for the request.

        Returns:
            None

        Raises:
            ForbiddenException: If any of the required roles are not present in the access token claims.
        """
        if not isinstance(required_roles, set):
            required_roles = set(required_roles)

        claimed_roles = set(context.get("access_token_claims").roles or [])

        _require_any_role(claimed_roles=claimed_roles, required_roles=required_roles)

else:
    log.warning(
        "WARNING: Role-Based Access Control is disabled. "
        "See OAUTH_ENABLED and OAUTH_RBAC_ENABLED environment variables."
    )

    # pylint: disable=unused-argument
    class RequiresAnyRole:
        def __init__(self, roles):
            # An empty method to keep instantiation compatible with disabled functionality
            pass

        def __call__(self):
            pass

    # pylint: disable=unused-argument
    def require_any_role(required_roles):
        # An empty method to keep call compatibility with disabled functionality
        pass


def _require_any_role(claimed_roles: set[str], required_roles: set[str]):
    """
    Raises ForbiddenException if none of the required roles are claimed.

    Args:
        claimed_roles (set[str]): The set of roles claimed in the JWT access token.
        required_roles (set[str]): The set of roles required for the request.

    Raises:
        ForbiddenException: If none of the required roles are claimed.
    """
    if not (claimed_roles and required_roles & claimed_roles):
        raise ForbiddenException(f"Requires role: {' or '.join(required_roles)}")
