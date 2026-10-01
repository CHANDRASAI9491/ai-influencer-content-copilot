import logging
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..config import settings
from ..models import User, CreatorProfile, ContentIdea, ContentBrief, Feedback
from ..schemas import (
    IdeaGenerateRequest, StructuredIdeasResponse, StructuredBriefResponse,
    StructuredIdeaItem, HookItem, ScriptItem, ShotItem
)
from .prompt_templates import (
    IDEA_GENERATION_PROMPT_V1, BRIEF_GENERATION_PROMPT_V1,
    HOOK_GENERATION_PROMPT_V1, CAPTION_GENERATION_PROMPT_V1
)
from .llm_providers import get_llm_provider, IntelligentCreativeEngine

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def sanitize_input(text: Optional[str]) -> str:
        """Sanitize user text input to treat as data, not instructions."""
        if not text:
            return ""
        # Strip potential prompt injection markers and dangerous characters
        sanitized = text.replace("```", "").replace("<|im_start|>", "").replace("<|im_end|>", "")
        return sanitized.strip()[:1000]

    @staticmethod
    def validate_safety_claims(data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safety validation: Reject or neutralize unsupported claims
        (e.g., 'guaranteed viral', 'guaranteed views', 'verified trend').
        """
        def clean_val(val: Any) -> Any:
            if isinstance(val, str):
                forbidden_replacements = [
                    ("will go viral", "is designed for high engagement"),
                    ("guaranteed viral", "optimized for viewer retention"),
                    ("guaranteed views", "estimated reach potential"),
                    ("guaranteed followers", "designed to attract followers"),
                    ("definitely trending", "AI-suggested content topic"),
                    ("verified trend", "AI-modeled content suggestion"),
                    ("100% viral", "crafted for audience relevance")
                ]
                cleaned = val
                for bad, repl in forbidden_replacements:
                    cleaned = cleaned.replace(bad, repl).replace(bad.capitalize(), repl.capitalize())
                return cleaned
            elif isinstance(val, list):
                return [clean_val(item) for item in val]
            elif isinstance(val, dict):
                return {k: clean_val(v) for k, v in val.items()}
            return val

        return clean_val(data_dict)

    @classmethod
    def generate_ideas(
        cls,
        db: Session,
        user: User,
        request: IdeaGenerateRequest
    ) -> List[ContentIdea]:
        """
        Pipeline:
        1. Load Creator Profile
        2. Merge Request Constraints
        3. Load Feedback signals (what did the user previously like or dislike?)
        4. Build Versioned Prompt
        5. Invoke LLM Provider
        6. Validate against StructuredIdeasResponse Schema
        7. Safety & Evidence Validation
        8. Persist and return ContentIdea records
        """
        profile = user.profile
        if not profile:
            # Create a sensible default profile if missing
            profile = CreatorProfile(
                user_id=user.id,
                creator_type="Aspiring Influencer",
                niches=["General"],
                languages=["English"],
                target_audience="General audience",
                goals=["Grow audience"],
                formats=["Educational"],
                equipment=["Smartphone"],
                filming_time="30 minutes",
                environment="Home"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # Merge preferences
        filming_time = cls.sanitize_input(request.available_time) or profile.filming_time or "30 minutes"
        equipment = request.equipment if request.equipment is not None else profile.equipment
        if not equipment:
            equipment = ["Smartphone"]
        environment = cls.sanitize_input(request.environment) or profile.environment or "Home"
        goal = cls.sanitize_input(request.goal) or (profile.goals[0] if profile.goals else "Grow audience")
        additional_notes = cls.sanitize_input(request.additional_notes)

        # Incorporate prior user feedback into context to avoid disliked patterns
        negative_feedback = (
            db.query(Feedback.reason)
            .filter(Feedback.user_id == user.id, Feedback.rating == "not_useful")
            .limit(5)
            .all()
        )
        feedback_context = ""
        if negative_feedback:
            reasons = [r[0] for r in negative_feedback if r[0]]
            if reasons:
                feedback_context = f"Avoid patterns creator previously marked not useful: {', '.join(set(reasons))}."

        # Compile versioned prompt
        prompt = IDEA_GENERATION_PROMPT_V1.format(
            creator_type=profile.creator_type,
            niches=", ".join(profile.niches) if profile.niches else "General",
            secondary_niches=", ".join(profile.secondary_niches) if profile.secondary_niches else "None",
            target_audience=profile.target_audience,
            languages=", ".join(profile.languages) if profile.languages else "English",
            broad_location=profile.broad_location or "Not specified",
            goals=goal,
            formats=", ".join(profile.formats) if profile.formats else "Educational Reel",
            equipment=", ".join(equipment),
            filming_time=filming_time,
            environment=environment,
            additional_notes=f"{additional_notes} {feedback_context}".strip()
        )

        provider = get_llm_provider(allow_fallback=settings.AI_FALLBACK_ON_ERROR)
        logger.info(f"Generating ideas for user {user.id} using provider: {provider.name}")

        try:
            raw_json = provider.generate_json(prompt)
            provider_name = provider.name
            provider_model = provider.model
            is_fallback = provider.is_fallback
            fallback_reason = provider.fallback_reason
            attempted_provider = provider.attempted_provider
        except Exception as e:
            logger.error(f"Provider '{provider.name}' failed: {e}")
            if not settings.AI_FALLBACK_ON_ERROR:
                err_str = str(e).lower()
                if isinstance(e, TimeoutError) or "timeout" in err_str or "timed out" in err_str:
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail=f"AI service provider ({provider.name}) timed out: {e}"
                    )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI service provider ({provider.name}) failed: {e}"
                )
            
            # Resilient fallback with full audit trail
            fallback_engine = IntelligentCreativeEngine(
                is_fallback=True,
                fallback_reason=f"{type(e).__name__}: {str(e)}",
                attempted_provider=provider.name
            )
            raw_json = fallback_engine.generate_json(prompt)
            provider_name = fallback_engine.name
            provider_model = fallback_engine.model
            is_fallback = True
            fallback_reason = fallback_engine.fallback_reason
            attempted_provider = provider.name

        # Validate with Pydantic
        try:
            validated = StructuredIdeasResponse.model_validate(raw_json)
        except Exception as val_err:
            logger.error(f"Malformed AI ideas output: {val_err}. Raw was: {raw_json}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned an invalid structured format. Please retry."
            )

        # Safety & evidence validation
        safe_data = cls.validate_safety_claims(validated.model_dump())
        validated_ideas = safe_data.get("ideas", [])

        # Persist generated ideas in database
        saved_records = []
        for item in validated_ideas[:5]:
            idea_record = ContentIdea(
                user_id=user.id,
                title=item["title"],
                description=item["description"],
                format=item["format"],
                difficulty=item["difficulty"],
                estimated_time=item["estimated_time"],
                why_it_fits=item["why_it_fits"],
                status="suggested",
                meta_info={
                    "required_equipment": item.get("required_equipment", []),
                    "shooting_environment": item.get("shooting_environment", environment),
                    "originality_considerations": item.get("originality_considerations", ""),
                    "is_ai_generated": True,
                    "provider": provider_name,
                    "model": provider_model,
                    "is_fallback": is_fallback,
                    "fallback_reason": fallback_reason,
                    "attempted_provider": attempted_provider
                }
            )
            db.add(idea_record)
            saved_records.append(idea_record)

        db.commit()
        for rec in saved_records:
            db.refresh(rec)

        return saved_records

    @classmethod
    def generate_brief(
        cls,
        db: Session,
        user: User,
        idea: ContentIdea,
        creator_notes: Optional[str] = None
    ) -> ContentBrief:
        """
        Generate complete structured Content Brief from an Idea.
        Output contains Title, Two Hooks (Direct & Curiosity), Segmented Script,
        Shot List, Caption, CTA, On-screen text, Practical requirements,
        Assumptions, and Originality guidance.
        """
        profile = user.profile
        creator_notes_clean = cls.sanitize_input(creator_notes)

        equipment_str = ", ".join(profile.equipment) if profile and profile.equipment else "Smartphone"
        filming_time_str = profile.filming_time if profile and profile.filming_time else "30 minutes"
        env_str = profile.environment if profile and profile.environment else "Gym"
        lang_str = ", ".join(profile.languages) if profile and profile.languages else "Telugu"
        audience_str = profile.target_audience if profile and profile.target_audience else "College students and beginners"

        prompt = BRIEF_GENERATION_PROMPT_V1.format(
            creator_type=profile.creator_type if profile else "Creator",
            niches=", ".join(profile.niches) if profile and profile.niches else "Fitness",
            languages=lang_str,
            target_audience=audience_str,
            equipment=equipment_str,
            filming_time=filming_time_str,
            environment=env_str,
            idea_title=idea.title,
            idea_description=idea.description,
            idea_format=idea.format,
            creator_notes=creator_notes_clean or "None"
        )

        provider = get_llm_provider(allow_fallback=settings.AI_FALLBACK_ON_ERROR)
        logger.info(f"Generating content brief for idea {idea.id} with provider: {provider.name}")

        try:
            raw_json = provider.generate_json(prompt)
            provider_name = provider.name
            provider_model = provider.model
            is_fallback = provider.is_fallback
            fallback_reason = provider.fallback_reason
            attempted_provider = provider.attempted_provider
        except Exception as e:
            logger.error(f"Provider '{provider.name}' failed for brief: {e}")
            if not settings.AI_FALLBACK_ON_ERROR:
                err_str = str(e).lower()
                if isinstance(e, TimeoutError) or "timeout" in err_str or "timed out" in err_str:
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail=f"AI service provider ({provider.name}) timed out: {e}"
                    )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI service provider ({provider.name}) failed: {e}"
                )
            
            fallback_engine = IntelligentCreativeEngine(
                is_fallback=True,
                fallback_reason=f"{type(e).__name__}: {str(e)}",
                attempted_provider=provider.name
            )
            raw_json = fallback_engine.generate_json(prompt)
            provider_name = fallback_engine.name
            provider_model = fallback_engine.model
            is_fallback = True
            fallback_reason = fallback_engine.fallback_reason
            attempted_provider = provider.name

        # Validate with Pydantic
        try:
            validated = StructuredBriefResponse.model_validate(raw_json)
        except Exception as val_err:
            logger.error(f"Malformed AI brief output: {val_err}. Raw was: {raw_json}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned an invalid brief format. Please retry."
            )

        safe_data = cls.validate_safety_claims(validated.model_dump())

        # Check if an existing brief already exists for this idea to increment version
        existing_brief = db.query(ContentBrief).filter(
            ContentBrief.idea_id == idea.id,
            ContentBrief.user_id == user.id
        ).first()

        version = (existing_brief.version + 1) if existing_brief else 1

        brief = ContentBrief(
            user_id=user.id,
            idea_id=idea.id,
            title=safe_data["title"],
            content_objective=safe_data.get("content_objective", "High engagement education"),
            selected_hook_type="direct",
            recommended_hook=safe_data.get("recommended_hook", "direct"),
            hooks=safe_data["hooks"],
            script=safe_data["script"],
            shots=safe_data["shots"],
            caption=safe_data["caption"],
            cta=safe_data["cta"],
            hashtags=safe_data.get("hashtags", []),
            on_screen_text=safe_data.get("on_screen_text", []),
            requirements=safe_data.get("requirements", []),
            editing_notes=safe_data.get("editing_notes", []),
            b_roll_requirements=safe_data.get("b_roll_requirements", []),
            audio_requirements=safe_data.get("audio_requirements", []),
            assumptions=safe_data.get("assumptions", []),
            originality_notes=safe_data.get("originality_notes", []),
            platform_notes=safe_data.get("platform_notes", []),
            status="planned",
            version=version,
            meta_info={
                "is_ai_generated": True,
                "provider": provider_name,
                "model": provider_model,
                "is_fallback": is_fallback,
                "fallback_reason": fallback_reason,
                "attempted_provider": attempted_provider
            }
        )

        db.add(brief)
        # Update idea status
        idea.status = "brief_created"
        db.commit()
        db.refresh(brief)

        return brief

    @classmethod
    def regenerate_hooks(cls, user: User, topic: str, audience: str, language: str) -> List[Dict[str, str]]:
        """Regenerate two fresh alternative hooks for a brief."""
        prompt = HOOK_GENERATION_PROMPT_V1.format(
            topic=cls.sanitize_input(topic),
            audience=cls.sanitize_input(audience),
            language=cls.sanitize_input(language)
        )
        provider = get_llm_provider()
        try:
            data = provider.generate_json(prompt)
            hooks = data.get("hooks", [])
            if len(hooks) >= 2:
                return hooks[:2]
        except Exception as e:
            logger.warning(f"Hook regeneration error: {e}")

        # Fallback
        return [
            {"type": "direct", "text": f"Stop making this rookie mistake in {topic} right now!"},
            {"type": "curiosity", "text": f"Why does nobody tell beginners this about {topic}?"}
        ]
