import pytest
from fastapi import HTTPException

from src.core.security import create_access_token, hash_password, require_role, verify_password
from src.models.entities import Role, User


@pytest.mark.parametrize(
    "password",
    [
        "password123",
        "Admin123!",
        "qwertyui",
        "long-enough-pass",
        "seller-demo-1",
        "buyer-demo-2",
        "moderator-pass",
        "admin-pass-123",
        "upload-feature-pass",
        "chat-feature-pass",
        "catalog-feature-pass",
        "moderation-feature-pass",
        "listing-feature-pass",
        "category-feature-pass",
        "workspace-pass-01",
        "workspace-pass-02",
        "workspace-pass-03",
        "workspace-pass-04",
        "workspace-pass-05",
        "workspace-pass-06",
    ],
)
def test_hash_and_verify_password_roundtrip(password):
    hashed = hash_password(password)
    assert "$" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password(f"{password}-wrong", hashed) is False


@pytest.mark.parametrize(
    "password",
    [
        "same-password",
        "Admin123!",
        "repeatable-pass",
        "moderator-secret",
        "buyer-secret",
        "seller-secret",
        "catalog-secret",
        "detail-page-secret",
        "upload-secret",
        "message-secret",
    ],
)
def test_hash_password_uses_random_salt(password):
    first = hash_password(password)
    second = hash_password(password)
    assert first != second
    assert verify_password(password, first)
    assert verify_password(password, second)


@pytest.mark.parametrize(
    "subject",
    [
        "admin@example.com",
        "moderator@example.com",
        "seller@example.com",
        "buyer@example.com",
        "blocked@example.com",
        "owner@example.com",
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "demo@example.com",
    ],
)
def test_create_access_token_returns_non_empty_string(subject):
    token = create_access_token(subject)
    assert isinstance(token, str)
    assert len(token) > 20


@pytest.mark.parametrize(
    ("allowed_roles", "user_role", "should_pass"),
    [
        ((Role.ADMIN,), Role.ADMIN, True),
        ((Role.ADMIN,), Role.MODERATOR, False),
        ((Role.ADMIN,), Role.USER, False),
        ((Role.MODERATOR,), Role.MODERATOR, True),
        ((Role.MODERATOR,), Role.ADMIN, False),
        ((Role.USER,), Role.USER, True),
        ((Role.ADMIN, Role.MODERATOR), Role.ADMIN, True),
        ((Role.ADMIN, Role.MODERATOR), Role.MODERATOR, True),
        ((Role.ADMIN, Role.MODERATOR), Role.USER, False),
        ((Role.USER, Role.MODERATOR), Role.MODERATOR, True),
        ((Role.USER, Role.MODERATOR), Role.USER, True),
        ((Role.USER, Role.MODERATOR), Role.ADMIN, False),
        ((Role.ADMIN, Role.USER), Role.USER, True),
        ((Role.ADMIN, Role.USER), Role.MODERATOR, False),
        ((Role.ADMIN, Role.USER), Role.ADMIN, True),
        ((Role.ADMIN, Role.MODERATOR, Role.USER), Role.USER, True),
    ],
)
def test_require_role_matrix(allowed_roles, user_role, should_pass):
    dependency = require_role(*allowed_roles)
    current_user = User(
        email="role@test.com",
        full_name="Role User",
        password_hash="hashed",
        role=user_role,
    )
    if should_pass:
        assert dependency(current_user) is current_user
    else:
        with pytest.raises(HTTPException) as exc_info:
            dependency(current_user)
        assert exc_info.value.status_code == 403
