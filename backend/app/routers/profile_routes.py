from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, CreatorProfile
from ..schemas import ProfileOut, ProfileUpdate
from ..auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Creator Profile"])

@router.get("", response_model=ProfileOut)
def get_creator_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = CreatorProfile(
            user_id=current_user.id,
            creator_type="Aspiring Influencer",
            niches=["Fitness"],
            secondary_niches=["Nutrition"],
            languages=["Telugu", "English"],
            target_audience="College students and beginners",
            broad_location="Hyderabad",
            goals=["Grow audience"],
            formats=["Educational", "Tutorial"],
            equipment=["Smartphone"],
            filming_time="30 minutes",
            environment="Gym"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return ProfileOut.model_validate(profile)

@router.put("", response_model=ProfileOut)
def update_creator_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = CreatorProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return ProfileOut.model_validate(profile)

@router.post("/reset-demo", response_model=ProfileOut)
def reset_to_rahul_demo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset creator profile to the exact specification of Rahul (Demo Creator)."""
    profile = current_user.profile
    if not profile:
        profile = CreatorProfile(user_id=current_user.id)
        db.add(profile)

    profile.creator_type = "Aspiring Influencer"
    profile.niches = ["Fitness"]
    profile.secondary_niches = ["Nutrition", "Motivation"]
    profile.languages = ["Telugu", "English"]
    profile.target_audience = "College students and beginners"
    profile.broad_location = "Hyderabad"
    profile.goals = ["Grow audience", "Educate"]
    profile.formats = ["Educational", "Tutorial", "POV"]
    profile.equipment = ["Smartphone"]
    profile.filming_time = "30 minutes"
    profile.environment = "Gym"

    db.commit()
    db.refresh(profile)
    return ProfileOut.model_validate(profile)
