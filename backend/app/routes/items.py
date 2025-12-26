from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.item import Item, ItemStatus, ItemHistory
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemStatusResponse, ItemHistoryResponse
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/items", tags=["Items & Traceability"])


@router.get("/", response_model=List[ItemResponse])
async def get_all_items(
    skip: int = 0,
    limit: int = 100,
    status_id: Optional[str] = None,
    model_id: Optional[str] = None,
    line_id: Optional[str] = None,
    cell_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all items with optional filters

    - **status_id**: Filter by status
    - **model_id**: Filter by model
    - **line_id**: Filter by line
    - **cell_id**: Filter by cell
    """
    query = db.query(Item)

    if status_id:
        query = query.filter(Item.status_id == status_id)
    if model_id:
        query = query.filter(Item.model_id == model_id)
    if line_id:
        query = query.filter(Item.line_id == line_id)
    if cell_id:
        query = query.filter(Item.cell_id == cell_id)

    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get item by ID"""
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item


@router.get("/{item_id}/history", response_model=List[ItemHistoryResponse])
async def get_item_history(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get complete history of an item"""
    history = db.query(ItemHistory).filter(ItemHistory.item_id == item_id).order_by(ItemHistory.create_date.desc()).all()
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found for this item"
        )
    return history


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new item"""
    # Check if item already exists
    existing_item = db.query(Item).filter(Item.item_id == item.item_id).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID already exists"
        )

    # Create new item
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Create history entry
    history_entry = ItemHistory(**item.model_dump())
    db.add(history_entry)
    db.commit()

    return db_item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update item and create history entry"""
    db_item = db.query(Item).filter(Item.item_id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Save current state to history before updating
    history_data = {
        "item_id": db_item.item_id,
        "model_id": db_item.model_id,
        "line_id": db_item.line_id,
        "location_id": db_item.location_id,
        "cell_id": db_item.cell_id,
        "id_user": db_item.id_user,
        "create_date": db_item.create_date,
        "last_test_date": db_item.last_test_date,
        "status_id": db_item.status_id,
        "value1_int": db_item.value1_int,
        "value2_int": db_item.value2_int,
        "value3_int": db_item.value3_int,
        "value4_int": db_item.value4_int,
        "value5_int": db_item.value5_int,
        "value1_str": db_item.value1_str,
        "value2_str": db_item.value2_str,
        "value3_str": db_item.value3_str,
        "value4_str": db_item.value4_str,
        "value5_str": db_item.value5_str,
    }
    history_entry = ItemHistory(**history_data)
    db.add(history_entry)

    # Update item
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    # Update last_test_date
    db_item.last_test_date = datetime.utcnow()

    db.commit()
    db.refresh(db_item)

    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete item (creates final history entry)"""
    db_item = db.query(Item).filter(Item.item_id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Save final state to history
    history_data = {
        "item_id": db_item.item_id,
        "model_id": db_item.model_id,
        "line_id": db_item.line_id,
        "location_id": db_item.location_id,
        "cell_id": db_item.cell_id,
        "id_user": db_item.id_user,
        "create_date": db_item.create_date,
        "last_test_date": db_item.last_test_date,
        "status_id": db_item.status_id,
        "value1_int": db_item.value1_int,
        "value2_int": db_item.value2_int,
        "value3_int": db_item.value3_int,
        "value4_int": db_item.value4_int,
        "value5_int": db_item.value5_int,
        "value1_str": db_item.value1_str,
        "value2_str": db_item.value2_str,
        "value3_str": db_item.value3_str,
        "value4_str": db_item.value4_str,
        "value5_str": db_item.value5_str,
    }
    history_entry = ItemHistory(**history_data)
    db.add(history_entry)

    db.delete(db_item)
    db.commit()

    return None


# Item Status endpoints
@router.get("/status/all", response_model=List[ItemStatusResponse])
async def get_all_item_statuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all item statuses"""
    statuses = db.query(ItemStatus).all()
    return statuses


# Statistics endpoints
@router.get("/stats/by-status", response_model=dict)
async def get_items_by_status_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get item count grouped by status"""
    stats = db.query(
        Item.status_id,
        func.count(Item.id_row).label("count")
    ).group_by(Item.status_id).all()

    return {stat.status_id: stat.count for stat in stats}


@router.get("/stats/by-model", response_model=dict)
async def get_items_by_model_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get item count grouped by model"""
    stats = db.query(
        Item.model_id,
        func.count(Item.id_row).label("count")
    ).group_by(Item.model_id).all()

    return {stat.model_id: stat.count for stat in stats}
