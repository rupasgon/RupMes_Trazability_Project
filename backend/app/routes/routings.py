from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.manufacturing import Routing
from app.models.relationships import CellLine, RoutingCell, RoutingModel
from app.models.user import User
from app.schemas.manufacturing import (
    RoutingCreate, RoutingResponse,
    CellLineCreate, RoutingCellCreate, RoutingModelCreate
)
from app.utils.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/routings", tags=["Routings"])


# ==================== ROUTINGS ====================
@router.get("/", response_model=List[RoutingResponse])
async def get_all_routings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all routings"""
    routings = db.query(Routing).offset(skip).limit(limit).all()
    return routings


@router.get("/{routing_id}", response_model=RoutingResponse)
async def get_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get routing by ID"""
    routing = db.query(Routing).filter(Routing.routing_id == routing_id).first()
    if not routing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routing not found"
        )
    return routing


@router.post("/", response_model=RoutingResponse, status_code=status.HTTP_201_CREATED)
async def create_routing(
    routing: RoutingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new routing (Admin only)"""
    # Check if routing already exists
    existing_routing = db.query(Routing).filter(Routing.routing_id == routing.routing_id).first()
    if existing_routing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Routing ID already exists"
        )

    db_routing = Routing(**routing.model_dump())
    db.add(db_routing)
    db.commit()
    db.refresh(db_routing)

    return db_routing


@router.put("/{routing_id}", response_model=RoutingResponse)
async def update_routing(
    routing_id: str,
    routing_update: RoutingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update routing (Admin only)"""
    db_routing = db.query(Routing).filter(Routing.routing_id == routing_id).first()
    if not db_routing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routing not found"
        )

    db_routing.description_routing = routing_update.description_routing
    db.commit()
    db.refresh(db_routing)

    return db_routing


@router.delete("/{routing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete routing (Admin only)"""
    db_routing = db.query(Routing).filter(Routing.routing_id == routing_id).first()
    if not db_routing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Routing not found"
        )

    db.delete(db_routing)
    db.commit()

    return None


# ==================== CELL-LINE RELATIONSHIPS ====================
@router.post("/cell-line", status_code=status.HTTP_201_CREATED)
async def create_cell_line_relationship(
    relationship: CellLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create cell-line relationship (Admin only)"""
    db_relationship = CellLine(**relationship.model_dump())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)

    return {"message": "Cell-Line relationship created successfully"}


@router.get("/cell-line/{line_id}")
async def get_cells_by_line(
    line_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all cells for a specific line"""
    relationships = db.query(CellLine).filter(CellLine.line_id == line_id).all()
    return [{"cell_id": rel.cell_id, "line_id": rel.line_id} for rel in relationships]


# ==================== ROUTING-CELL RELATIONSHIPS ====================
@router.post("/routing-cell", status_code=status.HTTP_201_CREATED)
async def create_routing_cell_relationship(
    relationship: RoutingCellCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create routing-cell relationship with location (Admin only)"""
    db_relationship = RoutingCell(**relationship.model_dump())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)

    return {"message": "Routing-Cell relationship created successfully"}


@router.get("/routing-cell/{routing_id}")
async def get_cells_by_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all cells for a specific routing with locations"""
    relationships = db.query(RoutingCell).filter(
        RoutingCell.routing_id == routing_id
    ).order_by(RoutingCell.id_location).all()

    return [{
        "routing_id": rel.routing_id,
        "cell_id": rel.cell_id,
        "id_location": rel.id_location
    } for rel in relationships]


# ==================== ROUTING-MODEL RELATIONSHIPS ====================
@router.post("/routing-model", status_code=status.HTTP_201_CREATED)
async def create_routing_model_relationship(
    relationship: RoutingModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create routing-model relationship (Admin only)"""
    db_relationship = RoutingModel(**relationship.model_dump())
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)

    return {"message": "Routing-Model relationship created successfully"}


@router.get("/routing-model/{model_id}")
async def get_routings_by_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all routings for a specific model"""
    relationships = db.query(RoutingModel).filter(
        RoutingModel.model_id == model_id
    ).all()

    return [{
        "routing_id": rel.routing_id,
        "model_id": rel.model_id,
        "location_id": rel.location_id
    } for rel in relationships]


@router.get("/model-routing/{routing_id}")
async def get_models_by_routing(
    routing_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all models for a specific routing"""
    relationships = db.query(RoutingModel).filter(
        RoutingModel.routing_id == routing_id
    ).all()

    return [{
        "routing_id": rel.routing_id,
        "model_id": rel.model_id,
        "location_id": rel.location_id
    } for rel in relationships]
