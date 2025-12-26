from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, Group, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserResponse, GroupResponse, UserStatusResponse
from app.utils.dependencies import get_current_active_user, get_current_admin_user
from app.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information"""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID"""
    # Users can only see their own info unless they're admin
    if current_user.id_user != user_id and current_user.id_group != "ADM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user = db.query(User).filter(User.id_user == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new user (Admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.id_user == user.id_user).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID already registered"
        )

    # Verify group exists
    group = db.query(Group).filter(Group.id_group == user.id_group).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group ID"
        )

    # Verify status exists
    status_obj = db.query(UserStatus).filter(UserStatus.status_user == user.status_user).first()
    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    # Hash password
    hashed_password = get_password_hash(user.pass_user)

    # Create new user
    db_user = User(
        id_user=user.id_user,
        name_user=user.name_user,
        mail_user=user.mail_user,
        id_group=user.id_group,
        status_user=user.status_user,
        pass_user=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update user (Admin only)"""
    db_user = db.query(User).filter(User.id_user == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)

    # Hash password if provided
    if "pass_user" in update_data:
        update_data["pass_user"] = get_password_hash(update_data["pass_user"])

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete user (Admin only)"""
    db_user = db.query(User).filter(User.id_user == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting admin user
    if db_user.id_user == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default admin user"
        )

    db.delete(db_user)
    db.commit()

    return None


# Group endpoints
@router.get("/groups/all", response_model=List[GroupResponse])
async def get_all_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user groups"""
    groups = db.query(Group).all()
    return groups


# Status endpoints
@router.get("/status/all", response_model=List[UserStatusResponse])
async def get_all_user_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all user statuses"""
    statuses = db.query(UserStatus).all()
    return statuses
