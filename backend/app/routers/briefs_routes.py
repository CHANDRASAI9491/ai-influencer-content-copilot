from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, ContentIdea, ContentBrief
from ..schemas import BriefGenerateRequest, BriefOut, BriefUpdate, BriefStatusUpdate
from ..auth import get_current_user
from ..services.ai_service import AIService

router = APIRouter(prefix="/briefs", tags=["Content Briefs"])

@router.post("/generate", response_model=BriefOut, status_code=status.HTTP_201_CREATED)
def generate_content_brief(
    request: BriefGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a complete, structured content brief from an existing idea.
    Includes Two Alternative Hooks (Direct vs Curiosity), Segmented Script,
    Shot List, Caption, CTA, On-screen text, Practical Requirements,
    Assumptions, and Originality notes.
    """
    idea = db.query(ContentIdea).filter(
        ContentIdea.id == request.idea_id,
        ContentIdea.user_id == current_user.id
    ).first()
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content idea not found or access denied."
        )

    brief = AIService.generate_brief(
        db=db,
        user=current_user,
        idea=idea,
        creator_notes=request.creator_notes
    )
    return BriefOut.model_validate(brief)

@router.get("", response_model=List[BriefOut])
def list_user_briefs(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all briefs owned by the current user with optional status filter."""
    query = db.query(ContentBrief).filter(ContentBrief.user_id == current_user.id)
    if status_filter:
        query = query.filter(ContentBrief.status == status_filter)
    briefs = query.order_by(ContentBrief.updated_at.desc()).all()
    return [BriefOut.model_validate(b) for b in briefs]

@router.get("/{brief_id}", response_model=BriefOut)
def get_brief_detail(
    brief_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single brief with strict ownership check."""
    brief = db.query(ContentBrief).filter(
        ContentBrief.id == brief_id,
        ContentBrief.user_id == current_user.id
    ).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content brief not found or access denied."
        )
    return BriefOut.model_validate(brief)

@router.put("/{brief_id}", response_model=BriefOut)
def update_brief(
    brief_id: int,
    brief_update: BriefUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update/edit brief fields (title, hooks, script, shots, caption, CTA, requirements, etc.).
    Protects against silent version overwrite if client version mismatches.
    """
    brief = db.query(ContentBrief).filter(
        ContentBrief.id == brief_id,
        ContentBrief.user_id == current_user.id
    ).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content brief not found or access denied."
        )

    # Version check if client provided version
    if brief_update.version is not None and brief_update.version < brief.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Conflict: Brief has been modified (current version: {brief.version}, submitted version: {brief_update.version}). Please refresh."
        )

    update_dict = brief_update.model_dump(exclude_unset=True)
    # Serialize nested pydantic objects to dicts if present
    for field in ["hooks", "script", "shots"]:
        if field in update_dict and update_dict[field] is not None:
            update_dict[field] = [
                item.model_dump() if hasattr(item, "model_dump") else item 
                for item in update_dict[field]
            ]

    for key, val in update_dict.items():
        if key != "version" and val is not None:
            setattr(brief, key, val)

    # Increment version
    brief.version += 1
    db.commit()
    db.refresh(brief)
    return BriefOut.model_validate(brief)

@router.patch("/{brief_id}/status", response_model=BriefOut)
@router.put("/{brief_id}/status", response_model=BriefOut)
def update_brief_status(
    brief_id: int,
    status_update: BriefStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update brief workflow status: planned -> filmed -> published -> archived."""
    allowed = ["planned", "filmed", "published", "archived"]
    if status_update.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_update.status}'. Allowed: {', '.join(allowed)}"
        )

    brief = db.query(ContentBrief).filter(
        ContentBrief.id == brief_id,
        ContentBrief.user_id == current_user.id
    ).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content brief not found or access denied."
        )

    brief.status = status_update.status
    db.commit()
    db.refresh(brief)
    return BriefOut.model_validate(brief)

@router.post("/{brief_id}/regenerate-hooks", response_model=BriefOut)
def regenerate_hooks_for_brief(
    brief_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate fresh alternative hooks for this brief."""
    brief = db.query(ContentBrief).filter(
        ContentBrief.id == brief_id,
        ContentBrief.user_id == current_user.id
    ).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content brief not found or access denied."
        )

    profile = current_user.profile
    lang = ", ".join(profile.languages) if profile and profile.languages else "Telugu"
    audience = profile.target_audience if profile and profile.target_audience else "College students and beginners"

    new_hooks = AIService.regenerate_hooks(
        user=current_user,
        topic=brief.title,
        audience=audience,
        language=lang
    )
    brief.hooks = new_hooks
    brief.version += 1
    db.commit()
    db.refresh(brief)
    return BriefOut.model_validate(brief)

@router.delete("/{brief_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brief(
    brief_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete brief with strict ownership check."""
    brief = db.query(ContentBrief).filter(
        ContentBrief.id == brief_id,
        ContentBrief.user_id == current_user.id
    ).first()
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content brief not found or access denied."
        )
    db.delete(brief)
    db.commit()
    return None
