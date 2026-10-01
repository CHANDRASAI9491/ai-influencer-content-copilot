import pytest
import os
import secrets
from pathlib import Path
from pydantic import ValidationError

from app.config import Settings, REVOKED_SECRETS, get_or_create_dev_secret

def test_production_requires_secret_key():
    """Requirement 2: Require SECRET_KEY from the environment for non-development environments."""
    with pytest.raises((ValueError, ValidationError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="",
            _env_file=None
        )
    assert "requires a SECRET_KEY to be set explicitly" in str(exc_info.value)


def test_production_rejects_revoked_or_default_secret():
    """Requirement 1 & 7: Remove hardcoded default and reject revoked secrets in production."""
    for bad_secret in REVOKED_SECRETS:
        with pytest.raises((ValueError, ValidationError)) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY=bad_secret,
                _env_file=None
            )
        assert "revoked" in str(exc_info.value).lower() or "insecure" in str(exc_info.value).lower()


def test_production_enforces_minimum_secret_length():
    """Requirement 2: Enforce cryptographically strong secret length in production."""
    with pytest.raises((ValueError, ValidationError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short-secret-key-12345",
            _env_file=None
        )
    assert "too short" in str(exc_info.value).lower()


def test_production_accepts_strong_secret():
    """Production succeeds when a valid strong secret is supplied."""
    strong_key = secrets.token_urlsafe(32)
    s = Settings(
        ENVIRONMENT="production",
        SECRET_KEY=strong_key,
        _env_file=None
    )
    assert s.SECRET_KEY == strong_key
    assert len(s.SECRET_KEY) >= 32


def test_development_generates_secure_random_secret_if_omitted():
    """Requirement 3: Generate a secure random development secret if omitted."""
    s = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="",
        _env_file=None
    )
    assert s.SECRET_KEY != ""
    assert s.SECRET_KEY not in REVOKED_SECRETS
    assert len(s.SECRET_KEY) >= 32


def test_development_rotates_if_revoked_key_used():
    """Requirement 7: Rotate any secret that may already have been exposed."""
    s = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="copilot-super-secret-creator-token-key-2026",
        _env_file=None
    )
    # The revoked key must NOT be used
    assert s.SECRET_KEY != "copilot-super-secret-creator-token-key-2026"
    assert len(s.SECRET_KEY) >= 32


def test_gitignore_protects_env_and_db_files():
    """Requirement 4 & 5: Ensure .gitignore protects .env and database files."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    gitignore_file = root_dir / ".gitignore"
    assert gitignore_file.exists(), ".gitignore must exist in workspace root"

    content = gitignore_file.read_text(encoding="utf-8")
    
    # Check .env protections
    assert ".env" in content
    assert ".dev_secret" in content
    
    # Check database protections
    assert "*.db" in content or "copilot.db" in content
    assert "*.sqlite" in content
