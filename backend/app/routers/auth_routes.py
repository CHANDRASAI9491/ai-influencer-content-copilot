from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, CreatorProfile
from ..schemas import UserRegister, UserLogin, UserOut, Token
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..seed_data import ensure_demo_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hash_password(user_in.password),
        display_name=user_in.display_name.strip()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically create default creator profile
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

    token_str = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token_str = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.post("/demo", response_model=Token)
def login_as_demo(db: Session = Depends(get_db)):
    """One-click instant login as demo creator Rahul (Telugu, Fitness, 30 min, Gym)."""
    user = ensure_demo_user(db)
    token_str = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Log out authenticated user session."""
    return {"status": "logged_out", "message": "Logged out successfully", "user_id": current_user.id}
