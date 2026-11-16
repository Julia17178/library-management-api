"""Unit tests for Bearer authentication and role authorization dependencies."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_current_user, require_admin
from app.auth.users import AuthenticatedUser, Role, get_demo_token_for_role
from app.core.config import Settings, StorageBackend


def test_get_current_user_accepts_member_token() -> None:
    settings = Settings(STORAGE_BACKEND=StorageBackend.IN_MEMORY)
    token = get_demo_token_for_role(Role.MEMBER, settings)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user = get_current_user(credentials=credentials, settings=settings)

    assert user == AuthenticatedUser(username="member", role=Role.MEMBER)


def test_get_current_user_accepts_admin_token() -> None:
    settings = Settings(STORAGE_BACKEND=StorageBackend.IN_MEMORY)
    token = get_demo_token_for_role(Role.ADMIN, settings)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user = get_current_user(credentials=credentials, settings=settings)

    assert user == AuthenticatedUser(username="admin", role=Role.ADMIN)


def test_get_current_user_rejects_missing_or_invalid_token() -> None:
    settings = Settings(STORAGE_BACKEND=StorageBackend.IN_MEMORY)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None, settings=settings)
    assert exc_info.value.status_code == 401

    bad_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-token")
    with pytest.raises(HTTPException) as bad_exc_info:
        get_current_user(credentials=bad_creds, settings=settings)
    assert bad_exc_info.value.status_code == 401


def test_require_admin_allows_admin_and_blocks_member() -> None:
    admin = AuthenticatedUser(username="admin", role=Role.ADMIN)
    member = AuthenticatedUser(username="member", role=Role.MEMBER)

    assert require_admin(admin) == admin

    with pytest.raises(HTTPException) as exc_info:
        require_admin(member)
    assert exc_info.value.status_code == 403
