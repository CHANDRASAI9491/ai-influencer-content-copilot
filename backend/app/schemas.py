from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)
    display_name: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str
    status: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# --- Creator Profile Schemas ---
class ProfileBase(BaseModel):
    creator_type: str = "Aspiring Influencer"
    niches: List[str] = Field(default_factory=list)
    secondary_niches: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=lambda: ["English"])
    target_audience: str = "College students and beginners"
    broad_location: Optional[str] = ""
    goals: List[str] = Field(default_factory=list)
    formats: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=lambda: ["Smartphone"])
    filming_time: str = "30 minutes"
    environment: str = "Home"
    experience_level: str = "Beginner"
    preferred_duration: str = "30-60 seconds"
    tone: str = "Practical & Energetic"
    topics_liked: List[str] = Field(default_factory=list)
    topics_avoided: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=lambda: ["Instagram Reels", "YouTube Shorts"])
    posting_frequency: str = "3-4 reels / week"

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    creator_type: Optional[str] = None
    niches: Optional[List[str]] = None
    secondary_niches: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    target_audience: Optional[str] = None
    broad_location: Optional[str] = None
    goals: Optional[List[str]] = None
    formats: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    filming_time: Optional[str] = None
    environment: Optional[str] = None
    experience_level: Optional[str] = None
    preferred_duration: Optional[str] = None
    tone: Optional[str] = None
    topics_liked: Optional[List[str]] = None
    topics_avoided: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    posting_frequency: Optional[str] = None

class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# --- AI Content Idea Schemas ---
class IdeaGenerateRequest(BaseModel):
    goal: Optional[str] = None
    available_time: Optional[str] = None
    equipment: Optional[List[str]] = None
    environment: Optional[str] = None
    format_preference: Optional[str] = None
    additional_notes: Optional[str] = None

class IdeaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str
    format: str
    difficulty: str
    estimated_time: str
    why_it_fits: str
    status: str
    meta_info: Optional[Dict[str, Any]] = None
    created_at: datetime

# --- AI Content Brief Schemas ---
class HookItem(BaseModel):
    type: str # "direct" or "curiosity"
    text: str

class ScriptItem(BaseModel):
    section: str # e.g. "0–3 sec", "3–10 sec"
    title: Optional[str] = ""
    content: str

class ShotItem(BaseModel):
    order: int
    timestamp: Optional[str] = ""
    framing: str
    action: Optional[str] = ""
    dialogue: Optional[str] = ""
    description: Optional[str] = ""
    visual_text: Optional[str] = ""
    b_roll: Optional[str] = ""
    audio: Optional[str] = ""
    transition: Optional[str] = ""

class BriefGenerateRequest(BaseModel):
    idea_id: int
    creator_notes: Optional[str] = None

class BriefUpdate(BaseModel):
    title: Optional[str] = None
    content_objective: Optional[str] = None
    selected_hook_type: Optional[str] = None
    recommended_hook: Optional[str] = None
    hooks: Optional[List[HookItem]] = None
    script: Optional[List[ScriptItem]] = None
    shots: Optional[List[ShotItem]] = None
    caption: Optional[str] = None
    cta: Optional[str] = None
    hashtags: Optional[List[str]] = None
    on_screen_text: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    editing_notes: Optional[List[str]] = None
    b_roll_requirements: Optional[List[str]] = None
    audio_requirements: Optional[List[str]] = None
    assumptions: Optional[List[str]] = None
    originality_notes: Optional[List[str]] = None
    platform_notes: Optional[List[str]] = None
    status: Optional[str] = None
    version: Optional[int] = None

class BriefStatusUpdate(BaseModel):
    status: str # "planned", "filmed", "published", "archived"

class BriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    idea_id: Optional[int] = None
    title: str
    content_objective: Optional[str] = "High engagement education"
    selected_hook_type: str = "direct"
    recommended_hook: Optional[str] = "direct"
    hooks: List[Dict[str, Any]]
    script: List[Dict[str, Any]]
    shots: List[Dict[str, Any]]
    caption: str
    cta: str
    hashtags: Optional[List[str]] = None
    on_screen_text: List[str]
    requirements: List[str]
    editing_notes: Optional[List[str]] = None
    b_roll_requirements: Optional[List[str]] = None
    audio_requirements: Optional[List[str]] = None
    assumptions: List[str]
    originality_notes: List[str]
    platform_notes: Optional[List[str]] = None
    status: str
    version: int
    meta_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

# --- Feedback Schemas ---
class FeedbackCreate(BaseModel):
    idea_id: Optional[int] = None
    brief_id: Optional[int] = None
    rating: str = Field(..., pattern="^(useful|not_useful)$")
    reason: Optional[str] = None
    details: Optional[str] = None

class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    idea_id: Optional[int] = None
    brief_id: Optional[int] = None
    rating: str
    reason: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

# --- Structured AI Validation Schemas ---
class StructuredIdeaItem(BaseModel):
    title: str
    description: str
    format: str
    difficulty: str
    estimated_time: str
    why_it_fits: str
    concept: Optional[str] = None
    target_audience: Optional[str] = None
    hook_preview: Optional[str] = None
    suggested_angle: Optional[str] = None
    cta: Optional[str] = None
    required_equipment: List[str] = Field(default_factory=list)
    shooting_environment: str = ""
    originality_considerations: str = ""
    assumptions: Optional[str] = None

class StructuredIdeasResponse(BaseModel):
    ideas: List[StructuredIdeaItem]

class StructuredBriefResponse(BaseModel):
    title: str
    format: str
    target_audience: str
    why_it_fits: str
    estimated_duration: str
    difficulty: str
    content_objective: Optional[str] = "High engagement education"
    recommended_hook: Optional[str] = "direct"
    hooks: List[HookItem]
    script: List[ScriptItem]
    shots: List[ShotItem]
    caption: str
    cta: str
    hashtags: List[str] = Field(default_factory=list)
    on_screen_text: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    editing_notes: List[str] = Field(default_factory=list)
    b_roll_requirements: List[str] = Field(default_factory=list)
    audio_requirements: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    originality_notes: List[str] = Field(default_factory=list)
    platform_notes: List[str] = Field(default_factory=list)
