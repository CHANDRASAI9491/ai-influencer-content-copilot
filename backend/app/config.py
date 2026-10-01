import os
import sys
import secrets
import logging
from pathlib import Path
from typing import Optional, Set
from pydantic_settings import BaseSettings
from pydantic import model_validator

from dotenv import load_dotenv

logger = logging.getLogger("copilot.config")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_ENV_FILE = ROOT_DIR / ".env"

if ROOT_ENV_FILE.exists():
    load_dotenv(ROOT_ENV_FILE)

# List of revoked, compromised, or insecure placeholder secrets.
# Any attempt to use these will be rejected and rotated immediately.
REVOKED_SECRETS: Set[str] = {
    "copilot-super-secret-creator-token-key-2026",
    "your_secure_jwt_secret",
    "secret",
    "changeme",
    "password",
    "default",
    "12345678",
    "supersecret"
}

def get_or_create_dev_secret() -> str:
    """
    Generate or read a secure, cryptographically random secret for development.
    The secret is cached in a gitignored .dev_secret file so sessions persist
    across fast code reloads during local development.
    """
    dev_secret_file = BASE_DIR / ".dev_secret"
    try:
        if dev_secret_file.exists():
            val = dev_secret_file.read_text(encoding="utf-8").strip()
            if val and val not in REVOKED_SECRETS and len(val) >= 32:
                return val
    except Exception as e:
        logger.debug(f"Could not read .dev_secret file: {e}")

    # Generate fresh cryptographically secure random key
    new_secret = secrets.token_urlsafe(48)
    try:
        dev_secret_file.write_text(new_secret, encoding="utf-8")
    except Exception as e:
        logger.debug(f"Could not persist .dev_secret file: {e}")

    logger.warning(
        "Notice: No SECRET_KEY provided in environment. "
        "Generated a cryptographically secure random development key."
    )
    return new_secret


class Settings(BaseSettings):
    PROJECT_NAME: str = "Influencer Help — AI Content Copilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Environment mode: 'development', 'test', 'staging', 'production'
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()

    # Database: defaults to SQLite for immediate local zero-config run, or PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/copilot.db")

    # Authentication & Security
    # NOTE: Never hardcode a production secret. In production, this MUST come from the environment.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI Providers
    # options: "auto", "gemini", "openai", "creative_engine"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_FALLBACK_ON_ERROR: bool = os.getenv("AI_FALLBACK_ON_ERROR", "true").lower() in ("true", "1", "yes")

    # Rate Limiting & Safety
    MAX_IDEAS_PER_REQUEST: int = 5
    RATE_LIMIT_REQUESTS_PER_MIN: int = 60

    model_config = {
        "env_file": str(ROOT_ENV_FILE) if ROOT_ENV_FILE.exists() else ".env",
        "extra": "ignore"
    }

    @model_validator(mode="after")
    def validate_and_resolve_security_config(self) -> "Settings":
        env = self.ENVIRONMENT.lower().strip()
        is_production = env in ("production", "prod", "staging")
        secret = self.SECRET_KEY.strip() if self.SECRET_KEY else ""

        if is_production:
            # 1. In production, SECRET_KEY is strictly required from environment
            if not secret:
                raise ValueError(
                    f"FATAL SECURITY CONFIGURATION: Environment '{self.ENVIRONMENT}' requires "
                    "a SECRET_KEY to be set explicitly in environment variables."
                )

            # 2. Reject revoked or default secrets in production
            if secret in REVOKED_SECRETS:
                raise ValueError(
                    "FATAL SECURITY CONFIGURATION: The configured SECRET_KEY has been revoked "
                    "or is a known insecure placeholder. You must generate a fresh, unique secret."
                )

            # 3. Minimum length requirement for cryptographic security
            if len(secret) < 32:
                raise ValueError(
                    f"FATAL SECURITY CONFIGURATION: The production SECRET_KEY is too short ({len(secret)} chars). "
                    "It must be at least 32 characters long."
                )
        else:
            # Development / Test mode:
            # If empty or revoked, automatically generate a cryptographically strong random secret
            if not secret or secret in REVOKED_SECRETS:
                self.SECRET_KEY = get_or_create_dev_secret()

        return self


settings = Settings()
