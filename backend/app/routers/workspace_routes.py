from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, ContentIdea, ContentBrief
from ..schemas import BriefOut, IdeaOut
from ..auth import get_current_user

router = APIRouter(prefix="/workspace", tags=["Creator Workspace"])

@router.get("/summary")
def get_workspace_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns counts and summary breakdown across workspace stages:
    - ideas (suggested / selected ideas)
    - planned (briefs in planned stage)
    - filmed (briefs self-reported filmed)
    - published (briefs self-reported published)
    - archived (briefs archived)
    """
    ideas_count = db.query(ContentIdea).filter(
        ContentIdea.user_id == current_user.id
    ).count()

    planned_count = db.query(ContentBrief).filter(
        ContentBrief.user_id == current_user.id,
        ContentBrief.status == "planned"
    ).count()

    filmed_count = db.query(ContentBrief).filter(
        ContentBrief.user_id == current_user.id,
        ContentBrief.status == "filmed"
    ).count()

    published_count = db.query(ContentBrief).filter(
        ContentBrief.user_id == current_user.id,
        ContentBrief.status == "published"
    ).count()

    archived_count = db.query(ContentBrief).filter(
        ContentBrief.user_id == current_user.id,
        ContentBrief.status == "archived"
    ).count()

    return {
        "ideas": ideas_count,
        "planned": planned_count,
        "filmed": filmed_count,
        "published": published_count,
        "archived": archived_count,
        "disclaimer": "Publication status is self-reported by the creator and is not verified via Instagram API."
    }

@router.get("")
def get_workspace_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns full workspace items partitioned by status column:
    - planned: List[BriefOut]
    - filmed: List[BriefOut]
    - published: List[BriefOut]
    - archived: List[BriefOut]
    - ideas: List[IdeaOut]
    """
    briefs = (
        db.query(ContentBrief)
        .filter(ContentBrief.user_id == current_user.id)
        .order_by(ContentBrief.updated_at.desc())
        .all()
    )
    ideas = (
        db.query(ContentIdea)
        .filter(ContentIdea.user_id == current_user.id)
        .order_by(ContentIdea.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "planned": [BriefOut.model_validate(b) for b in briefs if b.status == "planned"],
        "filmed": [BriefOut.model_validate(b) for b in briefs if b.status == "filmed"],
        "published": [BriefOut.model_validate(b) for b in briefs if b.status == "published"],
        "archived": [BriefOut.model_validate(b) for b in briefs if b.status == "archived"],
        "ideas": [IdeaOut.model_validate(i) for i in ideas]
    }
