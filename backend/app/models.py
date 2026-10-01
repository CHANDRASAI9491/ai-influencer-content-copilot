from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    profile = relationship("CreatorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ideas = relationship("ContentIdea", back_populates="user", cascade="all, delete-orphan")
    briefs = relationship("ContentBrief", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    creator_type = Column(String(100), default="Aspiring Influencer")
    niches = Column(JSON, default=list)            # e.g. ["Fitness"]
    secondary_niches = Column(JSON, default=list)  # e.g. ["Nutrition", "Motivation"]
    languages = Column(JSON, default=list)         # e.g. ["Telugu", "English"]
    target_audience = Column(String(255), default="College students and beginners")
    broad_location = Column(String(255), default="")
    goals = Column(JSON, default=list)             # e.g. ["Grow audience", "Educate"]
    formats = Column(JSON, default=list)           # e.g. ["Educational", "Tutorial"]
    equipment = Column(JSON, default=list)         # e.g. ["Smartphone"]
    filming_time = Column(String(100), default="30 minutes")
    environment = Column(String(100), default="Gym")
    experience_level = Column(String(100), default="Beginner")
    preferred_duration = Column(String(100), default="30-60 seconds")
    tone = Column(String(100), default="Practical & Energetic")
    topics_liked = Column(JSON, default=list)
    topics_avoided = Column(JSON, default=list)
    platforms = Column(JSON, default=list)
    posting_frequency = Column(String(100), default="3-4 reels / week")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="profile")


class ContentIdea(Base):
    __tablename__ = "content_ideas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Easy")
    estimated_time = Column(String(100), default="30 minutes")
    why_it_fits = Column(Text, nullable=False)
    status = Column(String(50), default="suggested") # suggested, selected, brief_created, discarded
    meta_info = Column(JSON, default=dict) # equipment, environment, originality considerations
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="ideas")
    brief = relationship("ContentBrief", back_populates="idea", uselist=False)
    feedbacks = relationship("Feedback", back_populates="idea")


class ContentBrief(Base):
    __tablename__ = "content_briefs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    idea_id = Column(Integer, ForeignKey("content_ideas.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content_objective = Column(String(255), default="High engagement education")
    selected_hook_type = Column(String(50), default="direct") # "direct" or "curiosity"
    recommended_hook = Column(String(50), default="direct")
    hooks = Column(JSON, default=list)         # [{"type": "direct", "text": ""}, {"type": "curiosity", "text": ""}]
    script = Column(JSON, default=list)        # [{"section": "0–3 sec", "title": "Hook", "content": ""}]
    shots = Column(JSON, default=list)         # [{"order": 1, "description": "", "framing": "", "visual_text": ""}]
    caption = Column(Text, default="")
    cta = Column(String(255), default="")
    hashtags = Column(JSON, default=list)
    on_screen_text = Column(JSON, default=list)
    requirements = Column(JSON, default=list)   # ["Smartphone", "Gym location", "No extra crew"]
    editing_notes = Column(JSON, default=list)
    b_roll_requirements = Column(JSON, default=list)
    audio_requirements = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)    # ["Assumes beginner gym equipment access"]
    originality_notes = Column(JSON, default=list)
    platform_notes = Column(JSON, default=list)
    status = Column(String(50), default="planned") # planned, filmed, published, archived
    version = Column(Integer, default=1)
    meta_info = Column(JSON, default=dict) # provider, is_fallback, model
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="briefs")
    idea = relationship("ContentIdea", back_populates="brief")
    feedbacks = relationship("Feedback", back_populates="brief")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    idea_id = Column(Integer, ForeignKey("content_ideas.id", ondelete="SET NULL"), nullable=True, index=True)
    brief_id = Column(Integer, ForeignKey("content_briefs.id", ondelete="SET NULL"), nullable=True, index=True)
    rating = Column(String(50), nullable=False) # "useful", "not_useful"
    reason = Column(String(255), nullable=True) # "Too generic", "Not relevant", etc.
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="feedbacks")
    idea = relationship("ContentIdea", back_populates="feedbacks")
    brief = relationship("ContentBrief", back_populates="feedbacks")
