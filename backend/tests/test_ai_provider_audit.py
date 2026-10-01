import pytest
import os
from unittest.mock import patch
from fastapi import status
from app.config import settings
from app.services.llm_providers import (
    get_llm_provider,
    GeminiProvider,
    IntelligentCreativeEngine,
    OpenAIProvider
)
from app.services.ai_service import AIService
from app.models import User, CreatorProfile, ContentIdea, ContentBrief


def create_test_user_and_profile(db_session, email="creator_audit@test.com"):
    user = User(email=email, hashed_password="hashed_pw_test", display_name="Audit Creator")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CreatorProfile(
        user_id=user.id,
        creator_type="Full-Time Creator",
        niches=["Fitness", "Health"],
        languages=["Telugu", "English"],
        target_audience="College students and beginners",
        goals=["Grow audience", "Monetize"],
        formats=["Educational Reel"],
        equipment=["Smartphone"],
        filming_time="30 minutes",
        environment="Gym"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user


class TestAIProviderSelectionAndExecution:
    """
    Test suite for AI Provider selection logic, provider reporting,
    and resilience/fallback behavior.
    """

    def test_provider_selection_creative_engine(self, monkeypatch):
        """Test AI_PROVIDER=creative_engine selects IntelligentCreativeEngine without fallback."""
        monkeypatch.setattr(settings, "AI_PROVIDER", "creative_engine")
        provider = get_llm_provider()

        assert isinstance(provider, IntelligentCreativeEngine)
        assert provider.name == "Local Creative Engine (Realistic Copilot)"
        assert provider.model == "creative-engine-v1"
        assert provider.is_fallback is False
        assert provider.fallback_reason is None
        assert provider.attempted_provider is None

    def test_provider_selection_auto_no_keys(self, monkeypatch):
        """Test AI_PROVIDER=auto with no keys configured defaults cleanly to IntelligentCreativeEngine."""
        monkeypatch.setattr(settings, "AI_PROVIDER", "auto")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
        monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

        provider = get_llm_provider()
        assert isinstance(provider, IntelligentCreativeEngine)
        assert provider.is_fallback is False
        assert provider.name == "Local Creative Engine (Realistic Copilot)"

    def test_provider_selection_gemini_missing_key_fallback_enabled(self, monkeypatch):
        """Test AI_PROVIDER=gemini with missing key reports fallback when fallback is enabled."""
        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", True)

        provider = get_llm_provider(allow_fallback=True)
        assert isinstance(provider, IntelligentCreativeEngine)
        assert provider.is_fallback is True
        assert "Missing GEMINI_API_KEY" in provider.fallback_reason
        assert provider.attempted_provider == "Google Gemini (Gemini 2.5 Flash)"
        assert "Fallback: Google Gemini" in provider.name

    def test_provider_selection_gemini_missing_key_fallback_disabled(self, monkeypatch):
        """Test AI_PROVIDER=gemini with missing key raises ValueError when fallback is disabled."""
        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", False)

        with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
            get_llm_provider(allow_fallback=False)

    def test_provider_selection_gemini_with_key_instantiates_gemini_provider(self, monkeypatch):
        """Test AI_PROVIDER=gemini with API key instantiates GeminiProvider targeting gemini-2.5-flash."""
        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "test_key_abc_123")

        provider = get_llm_provider()
        assert isinstance(provider, GeminiProvider)
        assert provider.name == "Google Gemini (Gemini 2.5 Flash)"
        assert provider.model == "gemini-2.5-flash"
        assert provider.is_fallback is False

    def test_gemini_invalid_key_live_call_fails_and_reports_real_error(self, monkeypatch):
        """
        Test that passing an invalid Gemini API key to GeminiProvider makes an actual
        call to Gemini API, receives a real ClientError (400 INVALID_ARGUMENT),
        and does NOT fake or simulate a response.
        """
        from google.genai.errors import ClientError

        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "AIzaSy_INVALID_KEY_AUDIT_TEST")

        provider = GeminiProvider(api_key="AIzaSy_INVALID_KEY_AUDIT_TEST")
        assert provider.name == "Google Gemini (Gemini 2.5 Flash)"
        assert provider.model == "gemini-2.5-flash"

        # Attempt actual generation: must fail with ClientError from Google's servers
        with pytest.raises(ClientError) as exc_info:
            provider.generate_json("Test prompt")

        error_message = str(exc_info.value)
        assert "API_KEY_INVALID" in error_message or "400" in error_message

    def test_ai_service_gemini_invalid_key_fallback_behavior(self, db_session, monkeypatch):
        """
        Test AIService.generate_ideas when Gemini has an invalid key and AI_FALLBACK_ON_ERROR=True:
        Verifies that ideas are generated via fallback, but meta_info explicitly flags
        is_fallback=True, attempted_provider='Google Gemini (Gemini 2.5 Flash)',
        and includes the real API_KEY_INVALID error in fallback_reason.
        """
        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "AIzaSy_INVALID_KEY_AUDIT_TEST")
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", True)

        user = create_test_user_and_profile(db_session, "invalid_key_fallback@test.com")
        from app.schemas import IdeaGenerateRequest
        req = IdeaGenerateRequest(available_time="30 minutes", equipment=["Smartphone"])

        ideas = AIService.generate_ideas(db=db_session, user=user, request=req)
        assert len(ideas) == 5

        # Check metadata
        for idea in ideas:
            meta = idea.meta_info
            assert meta["is_fallback"] is True
            assert meta["attempted_provider"] == "Google Gemini (Gemini 2.5 Flash)"
            assert "ClientError" in meta["fallback_reason"] or "400" in meta["fallback_reason"]
            assert "Local Creative Engine (Fallback:" in meta["provider"]

    def test_ai_service_gemini_invalid_key_strict_error_no_fallback(self, db_session, monkeypatch):
        """
        Test AIService.generate_ideas when Gemini has an invalid key and AI_FALLBACK_ON_ERROR=False:
        Verifies that AIService does NOT fake a response and instead raises HTTP 502 Bad Gateway.
        """
        from fastapi import HTTPException

        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "AIzaSy_INVALID_KEY_AUDIT_TEST")
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", False)

        user = create_test_user_and_profile(db_session, "invalid_key_strict@test.com")
        from app.schemas import IdeaGenerateRequest
        req = IdeaGenerateRequest(available_time="30 minutes", equipment=["Smartphone"])

        with pytest.raises(HTTPException) as exc_info:
            AIService.generate_ideas(db=db_session, user=user, request=req)

        assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
        assert "Google Gemini (Gemini 2.5 Flash)" in exc_info.value.detail

    def test_ai_service_gemini_timeout_handling(self, db_session, monkeypatch):
        """
        Test AIService behavior when Gemini times out:
        1. When AI_FALLBACK_ON_ERROR=False -> raises HTTP 504 Gateway Timeout.
        2. When AI_FALLBACK_ON_ERROR=True -> falls back and records TimeoutError in meta_info.
        """
        from fastapi import HTTPException

        monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
        monkeypatch.setattr(settings, "GEMINI_API_KEY", "mock_key")

        # Mock generate_json on GeminiProvider to simulate TimeoutError
        def mock_timeout(self, prompt):
            raise TimeoutError("Request timed out after 30s waiting for Gemini API")

        monkeypatch.setattr(GeminiProvider, "generate_json", mock_timeout)

        user = create_test_user_and_profile(db_session, "timeout_test@test.com")
        from app.schemas import IdeaGenerateRequest
        req = IdeaGenerateRequest(available_time="30 minutes")

        # Case 1: Strict failure
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", False)
        with pytest.raises(HTTPException) as exc_info:
            AIService.generate_ideas(db=db_session, user=user, request=req)
        assert exc_info.value.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert "timed out" in exc_info.value.detail.lower()

        # Case 2: Graceful fallback
        monkeypatch.setattr(settings, "AI_FALLBACK_ON_ERROR", True)
        ideas = AIService.generate_ideas(db=db_session, user=user, request=req)
        assert len(ideas) == 5
        assert ideas[0].meta_info["is_fallback"] is True
        assert "TimeoutError" in ideas[0].meta_info["fallback_reason"]
        assert ideas[0].meta_info["attempted_provider"] == "Google Gemini (Gemini 2.5 Flash)"

    def test_complete_flow_creative_engine_persistence(self, db_session, monkeypatch):
        """
        Test the complete flow for AI_PROVIDER=creative_engine:
        Ideas generation -> Brief generation -> Verify database records & metadata.
        """
        monkeypatch.setattr(settings, "AI_PROVIDER", "creative_engine")

        user = create_test_user_and_profile(db_session, "flow_test@test.com")
        from app.schemas import IdeaGenerateRequest
        req = IdeaGenerateRequest(available_time="30 minutes", equipment=["Smartphone"])

        # 1. Generate Ideas
        ideas = AIService.generate_ideas(db=db_session, user=user, request=req)
        assert len(ideas) == 5

        for idea in ideas:
            assert idea.user_id == user.id
            assert idea.meta_info["provider"] == "Local Creative Engine (Realistic Copilot)"
            assert idea.meta_info["model"] == "creative-engine-v1"
            assert idea.meta_info["is_fallback"] is False
            assert idea.meta_info["fallback_reason"] is None
            assert idea.meta_info["attempted_provider"] is None

        # 2. Generate Brief from Idea #1
        first_idea = ideas[0]
        brief = AIService.generate_brief(
            db=db_session,
            user=user,
            idea=first_idea,
            creator_notes="Emphasize Telugu hooks for college beginners"
        )

        assert brief.user_id == user.id
        assert brief.idea_id == first_idea.id
        assert brief.meta_info["provider"] == "Local Creative Engine (Realistic Copilot)"
        assert brief.meta_info["model"] == "creative-engine-v1"
        assert brief.meta_info["is_fallback"] is False
        assert brief.meta_info["fallback_reason"] is None
        assert len(brief.hooks) == 2
        assert len(brief.script) >= 4
        assert len(brief.shots) >= 4

        # 3. Check DB query persistence
        persisted_brief = db_session.query(ContentBrief).filter(ContentBrief.id == brief.id).first()
        assert persisted_brief is not None
        assert persisted_brief.meta_info["provider"] == "Local Creative Engine (Realistic Copilot)"
        assert persisted_brief.meta_info["is_fallback"] is False
