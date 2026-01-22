from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rupmes.controllers.items_controller import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)
from rupmes.controllers.routings_controller import (
    create_routing,
    delete_routing,
    get_routing,
    list_routings,
    update_routing,
)
from rupmes.controllers.status_controller import create_status, delete_status, get_status, list_statuses
from rupmes.controllers.users_controller import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)
from rupmes.core.db import get_engine
from rupmes.core.db import get_session as _get_session
from rupmes.models import TbItems, TbRoutings, TbStatus, TbUsers
from rupmes.views.schemas import (
    ItemCreate,
    ItemRead,
    ItemUpdate,
    RoutingCreate,
    RoutingRead,
    RoutingUpdate,
    StatusCreate,
    StatusRead,
    StatusUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
)


app = FastAPI(title="RupMes Trazability API")


def get_db():
    engine = get_engine()
    session = _get_session(engine)
    try:
        yield session
    finally:
        session.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/statuses", response_model=list[StatusRead])
def statuses(db: Session = Depends(get_db)):
    rows = list_statuses(db)
    return [StatusRead(status_id=row.status_id, description_status=row.description_status) for row in rows]

@app.get("/statuses/{status_id}", response_model=StatusRead)
def get_status_endpoint(status_id: str, db: Session = Depends(get_db)):
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.post("/statuses", response_model=StatusRead, status_code=status.HTTP_201_CREATED)
def create_status(payload: StatusCreate, db: Session = Depends(get_db)):
    status_row = TbStatus(status_id=payload.status_id, description_status=payload.description_status)
    try:
        row = create_status(db, status_row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Status already exists")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.patch("/statuses/{status_id}", response_model=StatusRead)
def update_status(status_id: str, payload: StatusUpdate, db: Session = Depends(get_db)):
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    if payload.description_status is not None:
        row.description_status = payload.description_status
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_endpoint(status_id: str, db: Session = Depends(get_db)):
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    delete_status(db, row)
    return None


@app.get("/items", response_model=list[ItemRead])
def items(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = list_items(db, limit=limit, offset=offset)
    return [
        ItemRead(
            item_id=row.item_id,
            model_id=row.model_id,
            line_id=row.line_id,
            location_id=row.location_id,
            cell_id=row.cell_id,
            id_user=row.id_user,
            status_id=row.status_id,
            create_date=row.create_date,
            last_test_date=row.last_test_date,
            value1_int=row.value1_int,
            value2_int=row.value2_int,
            value3_int=row.value3_int,
            value4_int=row.value4_int,
            value5_int=row.value5_int,
            value1_str=row.value1_str,
            value2_str=row.value2_str,
            value3_str=row.value3_str,
            value4_str=row.value4_str,
            value5_str=row.value5_str,
        )
        for row in rows
    ]


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item_endpoint(payload: ItemCreate, db: Session = Depends(get_db)):
    item = TbItems(
        item_id=payload.item_id,
        model_id=payload.model_id,
        line_id=payload.line_id,
        location_id=payload.location_id,
        cell_id=payload.cell_id,
        id_user=payload.id_user,
        status_id=payload.status_id,
        value1_int=payload.value1_int,
        value2_int=payload.value2_int,
        value3_int=payload.value3_int,
        value4_int=payload.value4_int,
        value5_int=payload.value5_int,
        value1_str=payload.value1_str,
        value2_str=payload.value2_str,
        value3_str=payload.value3_str,
        value4_str=payload.value4_str,
        value5_str=payload.value5_str,
    )
    try:
        row = create_item(db, item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists or FK invalid")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )

@app.get("/items/{item_id}", response_model=ItemRead)
def get_item_endpoint(item_id: str, db: Session = Depends(get_db)):
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )


@app.patch("/items/{item_id}", response_model=ItemRead)
def update_item_endpoint(item_id: str, payload: ItemUpdate, db: Session = Depends(get_db)):
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    try:
        row = update_item(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(item_id: str, db: Session = Depends(get_db)):
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    delete_item(db, row)
    return None

@app.get("/users", response_model=list[UserRead])
def users(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = list_users(db, limit=limit, offset=offset)
    return [
        UserRead(
            id_user=row.id_user,
            name_user=row.name_user,
            mail_user=row.mail_user,
            id_group=row.id_group,
            status_user=row.status_user,
            create_date=row.create_date,
        )
        for row in rows
    ]


@app.get("/users/{id_user}", response_model=UserRead)
def get_user_endpoint(id_user: str, db: Session = Depends(get_db)):
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        create_date=row.create_date,
    )


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)):
    user = TbUsers(
        id_user=payload.id_user,
        name_user=payload.name_user,
        mail_user=payload.mail_user,
        id_group=payload.id_group,
        status_user=payload.status_user,
        pass_hash="",
    )
    try:
        row = create_user(db, user, payload.password)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists or FK invalid")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        create_date=row.create_date,
    )

@app.patch("/users/{id_user}", response_model=UserRead)
def update_user_endpoint(id_user: str, payload: UserUpdate, db: Session = Depends(get_db)):
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updates = payload.model_dump(exclude_unset=True)
    password = updates.pop("password", None)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        row = update_user(db, row, password)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        create_date=row.create_date,
    )


@app.delete("/users/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(id_user: str, db: Session = Depends(get_db)):
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, row)
    return None

@app.get("/routings", response_model=list[RoutingRead])
def routings(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = list_routings(db, limit=limit, offset=offset)
    return [
        RoutingRead(
            routing_id=row.routing_id,
            description_routing=row.description_routing,
            create_date=row.create_date,
        )
        for row in rows
    ]


@app.get("/routings/{routing_id}", response_model=RoutingRead)
def get_routing_endpoint(routing_id: str, db: Session = Depends(get_db)):
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.post("/routings", response_model=RoutingRead, status_code=status.HTTP_201_CREATED)
def create_routing_endpoint(payload: RoutingCreate, db: Session = Depends(get_db)):
    routing = TbRoutings(
        routing_id=payload.routing_id,
        description_routing=payload.description_routing,
    )
    try:
        row = create_routing(db, routing)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Routing already exists")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.patch("/routings/{routing_id}", response_model=RoutingRead)
def update_routing_endpoint(routing_id: str, payload: RoutingUpdate, db: Session = Depends(get_db)):
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        row = update_routing(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.delete("/routings/{routing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routing_endpoint(routing_id: str, db: Session = Depends(get_db)):
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    delete_routing(db, row)
    return None
