# routers/weeks.py
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import db_session
from middlewares.jwt_bearer import JWTBearer

from services.weeks import (
    create_week,
    get_weeks,
    get_week as get_week_service,
    update_week as update_week_service,
    delete_week as delete_week_service,
)
from schemas.weeks import WeekCreate, WeekUpdate, WeekOut


weeks_router = APIRouter(
    prefix="/weeks",
    tags=["weeks"],
    dependencies=[Depends(JWTBearer())],  # protege todos los endpoints
)


@weeks_router.post(
    "/",
    response_model=WeekOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_week(
    week_in: WeekCreate,
    db: Session = Depends(db_session),
):
    try:
        return create_week(db, week_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@weeks_router.get(
    "/",
    response_model=List[WeekOut],
    status_code=status.HTTP_200_OK,
)
def list_weeks(
    year_number: Optional[int] = None,
    week_number: Optional[int] = None,
    is_split_month: Optional[bool] = None,
    db: Session = Depends(db_session),
):
    """
    Lista semanas. Filtros opcionales:
    - ?year_number=2025
    - ?week_number=40
    - ?is_split_month=true/false
    """
    return get_weeks(
        db,
        year_number=year_number,
        week_number=week_number,
        is_split_month=is_split_month,
    )


@weeks_router.get(
    "/{week_start}",
    response_model=WeekOut,
    status_code=status.HTTP_200_OK,
)
def get_week_detail(
    week_start: date,
    db: Session = Depends(db_session),
):
    week = get_week_service(db, week_start)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )
    return week


@weeks_router.put(
    "/{week_start}",
    response_model=WeekOut,
    status_code=status.HTTP_200_OK,
)
def update_week_detail(
    week_start: date,
    week_in: WeekUpdate,
    db: Session = Depends(db_session),
):
    week = update_week_service(db, week_start, week_in)
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )
    return week


@weeks_router.delete(
    "/{week_start}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_week_detail(
    week_start: date,
    db: Session = Depends(db_session),
):
    deleted = delete_week_service(db, week_start)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )
    return
