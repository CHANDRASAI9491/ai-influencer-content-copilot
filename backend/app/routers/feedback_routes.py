from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Feedback, ContentIdea, ContentBrief
from ..schemas import FeedbackCreate, FeedbackOut
from ..auth import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback System"])

@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit creator feedback for an idea or brief.
    Stores ratings (useful / not_useful) and reasons (Too generic, Equipment missing, etc.)
    to inform future generation context.
    """
    # Verify ownership of idea/brief if provided
    if feedback_in.idea_id:
        idea = db.query(ContentIdea).filter(
            ContentIdea.id == feedback_in.idea_id,
            ContentIdea.user_id == current_user.id
        ).first()
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated idea not found or access denied."
            )

    if feedback_in.brief_id:
        brief = db.query(ContentBrief).filter(
            ContentBrief.id == feedback_in.brief_id,
            ContentBrief.user_id == current_user.id
        ).first()
        if not brief:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated brief not found or access denied."
            )

    fb_record = Feedback(
        user_id=current_user.id,
        idea_id=feedback_in.idea_id,
        brief_id=feedback_in.brief_id,
        rating=feedback_in.rating,
        reason=feedback_in.reason,
        details=feedback_in.details
    )
    db.add(fb_record)
    db.commit()
    db.refresh(fb_record)
    return FeedbackOut.model_validate(fb_record)

@router.get("", response_model=List[FeedbackOut])
def get_user_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List recent feedback submitted by current user."""
    items = (
        db.query(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .order_by(Feedback.created_at.desc())
        .limit(50)
        .all()
    )
    return [FeedbackOut.model_validate(item) for item in items]
