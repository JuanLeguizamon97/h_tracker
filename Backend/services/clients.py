# services/clients.py
from typing import Optional, List
from sqlalchemy.orm import Session

from models.clients import Client
from schemas.clients import ClientCreate, ClientUpdate


def create_client(db: Session, client_in: ClientCreate) -> Client:
    """
    Crea un nuevo cliente. Si no se envían los IDs, la BD generará los UUID por defecto.
    """
    data = client_in.model_dump(exclude_unset=True)

    db_client = Client(**data)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


def get_clients(db: Session, active: Optional[bool] = None) -> List[Client]:
    """
    Lista todos los clientes. Si 'active' se envía, filtra por estado.
    """
    query = db.query(Client)
    if active is not None:
        query = query.filter(Client.active == active)
    return query.all()


def get_client(
    db: Session,
    primary_id_client: str,
    second_id_client: str,
) -> Optional[Client]:
    """
    Obtiene un cliente por sus dos claves primarias.
    """
    return (
        db.query(Client)
        .filter(
            Client.primary_id_client == primary_id_client,
            Client.second_id_client == second_id_client,
        )
        .first()
    )


def update_client(
    db: Session,
    primary_id_client: str,
    second_id_client: str,
    client_in: ClientUpdate,
) -> Optional[Client]:
    """
    Actualiza parcialmente un cliente.
    Devuelve el cliente actualizado o None si no existe.
    """
    db_client = get_client(db, primary_id_client, second_id_client)
    if not db_client:
        return None

    data = client_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_client, field, value)

    db.commit()
    db.refresh(db_client)

    return db_client


def delete_client(
    db: Session,
    primary_id_client: str,
    second_id_client: str,
) -> bool:
    """
    Elimina un cliente. Devuelve True si lo eliminó, False si no existía.
    """
    db_client = get_client(db, primary_id_client, second_id_client)
    if not db_client:
        return False

    db.delete(db_client)
    db.commit()
    return True
