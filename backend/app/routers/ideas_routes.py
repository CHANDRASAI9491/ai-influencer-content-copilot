from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, ContentIdea
from ..schemas import IdeaGenerateRequest, IdeaOut
from ..auth import get_current_user
from ..services.ai_service import AIService

router = APIRouter(prefix="/ideas", tags=["Content Ideas"])

@router.post("/generate", response_model=List[IdeaOut])
def generate_content_ideas(
    request: IdeaGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate 5 personalized, shootable content ideas tailored to creator niche,
    language, goals, available time, and gear constraints.
    """
    ideas = AIService.generate_ideas(db=db, user=current_user, request=request)
    return [IdeaOut.model_validate(idea) for idea in ideas]

@router.get("", response_model=List[IdeaOut])
def list_user_ideas(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List ideas belonging to the authenticated creator."""
    query = db.query(ContentIdea).filter(ContentIdea.user_id == current_user.id)
    if status_filter:
        query = query.filter(ContentIdea.status == status_filter)
    ideas = query.order_by(ContentIdea.created_at.desc()).all()
    return [IdeaOut.model_validate(idea) for idea in ideas]

@router.get("/{idea_id}", response_model=IdeaOut)
def get_idea_detail(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single idea details with strict ownership verification."""
    idea = db.query(ContentIdea).filter(
        ContentIdea.id == idea_id,
        ContentIdea.user_id == current_user.id
    ).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content idea not found or access denied."
        )
    return IdeaOut.model_validate(idea)

@router.patch("/{idea_id}/select", response_model=IdeaOut)
@router.post("/{idea_id}/select", response_model=IdeaOut)
def select_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Select idea to proceed with brief creation."""
    idea = db.query(ContentIdea).filter(
        ContentIdea.id == idea_id,
        ContentIdea.user_id == current_user.id
    ).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content idea not found or access denied."
        )
    idea.status = "selected"
    db.commit()
    db.refresh(idea)
    return IdeaOut.model_validate(idea)

@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an idea with strict ownership verification."""
    idea = db.query(ContentIdea).filter(
        ContentIdea.id == idea_id,
        ContentIdea.user_id == current_user.id
    ).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content idea not found or access denied."
        )
    db.delete(idea)
    db.commit()
    return None
