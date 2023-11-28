from pydantic import BaseModel, validator

AUTHORIZATION_ERROR_CODES = {
    "invalid_request",
    "unauthorized_client",
    "access_denied",
    "unsupported_response_type",
    "invalid_scope",
    "server_error",
    "temporarily_unavailable",
    # OpenID Connect Core 1.0
    "login_required",
    "interaction_required",
    # https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#error-codes-for-authorization-endpoint-errors
    "invalid_resource",
}


class JWTTokenClaims(BaseModel):
    """ID Token claims -- as per OpenID Connect 1.0 specification"""

    # RFC-7519 defines them optional, but mandated by OpenID Connect Core 1.0 for id-tokens (except nbf and jti)
    iss: str
    sub: str
    aud: list[str]
    exp: int
    nbf: int | None
    iat: int
    jti: str | None

    # RFC-8693 #4.2 common for both id and access token
    scp: list[str] | None = None

    @validator("aud", "scp", pre=True)
    # pylint:disable=no-self-argument
    def split_str(cls, elm):
        """Splits claim space-separated-string into a list of str elements"""
        if isinstance(elm, str):
            return elm.split()
        return elm


class AccessTokenClaims(JWTTokenClaims):
    """Access token claims"""

    roles: set[str] | None = None

    # OpenID Connect Core 1.0 Standard Claims
    name: str | None = None
    preferred_username: str | None = None
    email: str | None = None
    email_verified: bool | None = None

    # Seen in Active Directory tokens
    username: str | None = None
    oid: str | None = None
    tid: str | None = None

    azp: str | None


class IdTokenClaims(JWTTokenClaims):
    """ID Token claims -- as per OpenID Connect 1.0 specification"""

    # Optional by OpenID Connect Core 1.0
    auth_time: int | None
    nonce: str | None
    acr: str | None
    amr: str | None
    azp: str | None

    # OpenID Connect Core 1.0 Standard Claims
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    middle_name: str | None = None
    nickname: str | None = None
    preferred_username: str | None = None
    profile: str | None = None
    picture: str | None = None
    website: str | None = None
    email: str | None = None
    email_verified: bool | None = None
    gender: str | None = None
    birthdate: str | None = None
    zoneinfo: str | None = None
    locale: str | None = None
    phone_number: str | None = None
    phone_number_verified: str | None = None
    address: str | None = None
    updated_at: str | None = None

    # Seen in Active Directory tokens
    username: str | None = None
    idtyp: str | None = None
    oid: str | None = None
    tid: str | None = None


class UserInfo(BaseModel):
    """Model"""

    sub: str
    name: str
    username: str
    email: str
    initials: str
    roles: set[str]
