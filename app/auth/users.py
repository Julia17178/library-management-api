"""Predefined demonstration users and roles for Assignment 3."""

from dataclasses import dataclass
from enum import Enum

from app.core.config import Settings


class Role(str, Enum):
    """Roles supported by the course-demo permission policy."""

    MEMBER = "member"
    ADMIN = "admin"


@dataclass(frozen=True)
class AuthenticatedUser:
    """Represent the identity and role established by a valid Bearer token."""

    username: str
    role: Role


def get_demo_token_for_role(role: Role, settings: Settings) -> str:
    """Return the validated course-demo token configured for one role."""
    if role is Role.MEMBER:
        return settings.DEMO_MEMBER_TOKEN
    return settings.DEMO_ADMIN_TOKEN


def get_user_for_token(token: str, settings: Settings) -> AuthenticatedUser | None:
    """Map one configured demo token to its predefined user and role."""
    member_token = get_demo_token_for_role(Role.MEMBER, settings)
    admin_token = get_demo_token_for_role(Role.ADMIN, settings)

    if member_token and token == member_token:
        return AuthenticatedUser(username="member", role=Role.MEMBER)
    if admin_token and token == admin_token:
        return AuthenticatedUser(username="admin", role=Role.ADMIN)
    return None
