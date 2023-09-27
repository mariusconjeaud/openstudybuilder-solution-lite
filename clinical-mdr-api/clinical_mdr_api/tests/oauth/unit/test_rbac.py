import random

import pytest

import clinical_mdr_api.oauth.dependencies as oauth_dependencies
from clinical_mdr_api.exceptions import ForbiddenException
from clinical_mdr_api.oauth.models import AccessTokenClaims
from clinical_mdr_api.tests.oauth.markers import if_oauth_enabled
from clinical_mdr_api.tests.oauth.unit.test_jwk_service import mk_claims

# Skipp all tests in this module if OAuth is not enabled
pytestmark = if_oauth_enabled

KNOWN_ROLES = {
    "Admin.Read",
    "Admin.Write",
    "Library.Read",
    "Library.Write",
    "Study.Read",
    "Study.Write",
}

IRRELEVANT_ROLES = ["Some, Fake", "Testing", ""]


def test_require_any_role(monkeypatch):
    context = {}
    monkeypatch.setattr(oauth_dependencies, "context", context)

    for required_role in KNOWN_ROLES:
        claims = context["access_token_claims"] = AccessTokenClaims(**mk_claims())

        # Throws exception if required role is not claimed
        claims.roles = list(KNOWN_ROLES - {required_role})
        with pytest.raises(ForbiddenException):
            oauth_dependencies.require_any_role([required_role])

        claims.roles = [random.choice(claims.roles)]
        with pytest.raises(ForbiddenException):
            oauth_dependencies.require_any_role([required_role])

        # Throws exception if multiple roles are not claimed
        required_roles = [required_role, random.choice(claims.roles)]
        claims.roles = list(KNOWN_ROLES - set(required_roles))
        with pytest.raises(ForbiddenException):
            oauth_dependencies.require_any_role(required_roles)

        # Passes with required roles claimed
        claims.roles = list(required_roles)
        oauth_dependencies.require_any_role(required_roles)

        random.shuffle(claims.roles)
        oauth_dependencies.require_any_role(required_roles)

        claims.roles += [random.choice(tuple(KNOWN_ROLES - set(claims.roles)))]
        oauth_dependencies.require_any_role(required_roles)

        claims.roles = [
            random.choice(tuple(KNOWN_ROLES - set(claims.roles)))
        ] + claims.roles
        oauth_dependencies.require_any_role(required_roles)
