from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.manufacturing import Line, Cell, Model
from app.models.user import User
from app.schemas.manufacturing import (
    LineCreate, LineResponse,
    CellCreate, CellResponse,
    ModelCreate, ModelResponse
)
from app.utils.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(tags=["Manufacturing"])


# ==================== LINES ====================
@router.get("/lines", response_model=List[LineResponse])
async def get_all_lines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all production lines"""
    lines = db.query(Line).offset(skip).limit(limit).all()
    return lines


@router.get("/lines/{line_id}", response_model=LineResponse)
async def get_line(
    line_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get line by ID"""
    line = db.query(Line).filter(Line.line_id == line_id).first()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line not found"
        )
    return line


@router.post("/lines", response_model=LineResponse, status_code=status.HTTP_201_CREATED)
async def create_line(
    line: LineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new production line (Admin only)"""
    # Check if line already exists
    existing_line = db.query(Line).filter(Line.line_id == line.line_id).first()
    if existing_line:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Line ID already exists"
        )

    db_line = Line(**line.model_dump())
    db.add(db_line)
    db.commit()
    db.refresh(db_line)

    return db_line


@router.put("/lines/{line_id}", response_model=LineResponse)
async def update_line(
    line_id: str,
    line_update: LineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update line (Admin only)"""
    db_line = db.query(Line).filter(Line.line_id == line_id).first()
    if not db_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line not found"
        )

    db_line.description_line = line_update.description_line
    db.commit()
    db.refresh(db_line)

    return db_line


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line(
    line_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete line (Admin only)"""
    db_line = db.query(Line).filter(Line.line_id == line_id).first()
    if not db_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Line not found"
        )

    db.delete(db_line)
    db.commit()

    return None


# ==================== CELLS ====================
@router.get("/cells", response_model=List[CellResponse])
async def get_all_cells(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all production cells"""
    cells = db.query(Cell).offset(skip).limit(limit).all()
    return cells


@router.get("/cells/{cell_id}", response_model=CellResponse)
async def get_cell(
    cell_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get cell by ID"""
    cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
    if not cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found"
        )
    return cell


@router.post("/cells", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
async def create_cell(
    cell: CellCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new production cell (Admin only)"""
    # Check if cell already exists
    existing_cell = db.query(Cell).filter(Cell.cell_id == cell.cell_id).first()
    if existing_cell:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cell ID already exists"
        )

    db_cell = Cell(**cell.model_dump())
    db.add(db_cell)
    db.commit()
    db.refresh(db_cell)

    return db_cell


@router.put("/cells/{cell_id}", response_model=CellResponse)
async def update_cell(
    cell_id: str,
    cell_update: CellCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update cell (Admin only)"""
    db_cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
    if not db_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found"
        )

    db_cell.description_cell = cell_update.description_cell
    db.commit()
    db.refresh(db_cell)

    return db_cell


@router.delete("/cells/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cell(
    cell_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete cell (Admin only)"""
    db_cell = db.query(Cell).filter(Cell.cell_id == cell_id).first()
    if not db_cell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cell not found"
        )

    db.delete(db_cell)
    db.commit()

    return None


# ==================== MODELS ====================
@router.get("/models", response_model=List[ModelResponse])
async def get_all_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all product models"""
    models = db.query(Model).offset(skip).limit(limit).all()
    return models


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get model by ID"""
    model = db.query(Model).filter(Model.model_id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    return model


@router.post("/models", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new product model (Admin only)"""
    # Check if model already exists
    existing_model = db.query(Model).filter(Model.model_id == model.model_id).first()
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model ID already exists"
        )

    db_model = Model(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    return db_model


@router.put("/models/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    model_update: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update model (Admin only)"""
    db_model = db.query(Model).filter(Model.model_id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    db_model.description_model = model_update.description_model
    db.commit()
    db.refresh(db_model)

    return db_model


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete model (Admin only)"""
    db_model = db.query(Model).filter(Model.model_id == model_id).first()
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )

    db.delete(db_model)
    db.commit()

    return None
