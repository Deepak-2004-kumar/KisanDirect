from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import User, Farmer, Buyer, UserRole
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if payload.role not in ("FARMER", "BUYER"):
        raise HTTPException(status_code=400, detail="role must be FARMER or BUYER (admins are seeded separately)")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=UserRole(payload.role),
        preferred_language=payload.preferred_language,
    )
    db.add(user)
    db.flush()  # get user.id before commit

    if payload.role == "FARMER":
        db.add(Farmer(
            user_id=user.id, village=payload.village,
            land_size_acres=payload.land_size_acres,
            latitude=payload.latitude, longitude=payload.longitude,
        ))
    else:
        db.add(Buyer(
            user_id=user.id, business_name=payload.business_name or payload.full_name,
            buyer_type=payload.buyer_type or "RETAILER",
            latitude=payload.latitude, longitude=payload.longitude,
        ))

    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id, full_name=user.full_name)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id, full_name=user.full_name)
