# routers/clients.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.clients import (
    create_client,
    get_clients,
    get_client as get_client_service,
    update_client as update_client_service,
    delete_client as delete_client_service,
)
from schemas.clients import ClientCreate, ClientUpdate, ClientOut


clients_router = APIRouter(
    prefix="/clients",
    tags=["clients"],  # Protege todos los endpoints con JWT
)


@clients_router.post(
    "/",
    response_model=ClientOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_client(db, client_in)
    except Exception as e:
        # Puedes afinar este comportamiento para errores específicos (IntegrityError, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@clients_router.get(
    "/",
    response_model=List[ClientOut],
    status_code=status.HTTP_200_OK,
)
def list_clients(
    active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Lista clientes. Si 'active' se envía (?active=true/false), filtra por estado.
    """
    clients = get_clients(db, active=active)
    return clients


@clients_router.get(
    "/{primary_id_client}/{second_id_client}",
    response_model=ClientOut,
    status_code=status.HTTP_200_OK,
)
def get_client_detail(
    primary_id_client: str,
    second_id_client: str,
    db: Session = Depends(get_db),
):
    client = get_client_service(db, primary_id_client, second_id_client)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@clients_router.put(
    "/{primary_id_client}/{second_id_client}",
    response_model=ClientOut,
    status_code=status.HTTP_200_OK,
)
def update_client_detail(
    primary_id_client: str,
    second_id_client: str,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
):
    client = update_client_service(
        db,
        primary_id_client=primary_id_client,
        second_id_client=second_id_client,
        client_in=client_in,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return client


@clients_router.delete(
    "/{primary_id_client}/{second_id_client}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_client_detail(
    primary_id_client: str,
    second_id_client: str,
    db: Session = Depends(get_db),
):
    deleted = delete_client_service(db, primary_id_client, second_id_client)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    # 204: sin body de respuesta
    return
