from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from datetime import date
from enum import Enum
from .. import models, schemas
from ..database import engine, get_db
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/ports",
    tags=['Porty ładowania']
)

class PortStatus(str, Enum):
    WOLNY = 'wolny'
    ZAJETY = 'zajety'
    NIECZYNNY = 'nieczynny'

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingPortOut)
def create_port(
    charging_port: schemas.ChargingPortCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Tworzy nowy port ładowania
    Args:
        charging_port: Dane portu do utworzenia
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Returns:
        schemas.ChargingPortOut: Utworzony port
    """
    new_port = models.ChargingPort(**charging_port.dict())
    db.add(new_port)
    db.commit()
    db.refresh(new_port)
    return new_port

@router.get('/{id}', response_model=schemas.ChargingPortOut)
def get_port(id: int, db: Session = Depends(get_db)):
    """
    Pobiera pojedynczy port ładowania
    Args:
        id: ID portu
        db: Sesja bazy danych
    Returns:
        schemas.ChargingPortOut: Znaleziony port
    Raises:
        HTTPException: Gdy port nie zostanie znaleziony
    """
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    if not port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Nie znaleziono portu o ID: {id}"
        )
    return port

@router.get('/', response_model=List[schemas.ChargingPortOut])
def get_all_ports(db: Session = Depends(get_db)):
    """
    Pobiera wszystkie porty ładowania
    Args:
        db: Sesja bazy danych
    Returns:
        List[schemas.ChargingPortOut]: Lista wszystkich portów
    """
    ports = db.query(models.ChargingPort).all()
    for port in ports:
        if port.last_service_date is None:
            port.last_service_date = date.today()
    return ports

@router.patch("/{id}/status", response_model=schemas.ChargingPortOut)
def update_port_status(
    id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Aktualizuje status portu ładowania
    Args:
        id: ID portu
        status_update: Nowy status
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Returns:
        schemas.ChargingPortOut: Zaktualizowany port
    Raises:
        HTTPException: Gdy port nie zostanie znaleziony lub status jest nieprawidłowy
    """
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    if not port:
        raise HTTPException(
            status_code=404, 
            detail="Nie znaleziono portu"
        )
    
    new_status = status_update.get('status')
    if new_status not in [status.value for status in PortStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy status. Dozwolone wartości: {', '.join([status.value for status in PortStatus])}"
        )

    port.status = new_status
    db.commit()
    db.refresh(port)
    return port

@router.put("/{id}", response_model=schemas.ChargingPortOut)
def update_port(
    id: int,
    port_update: schemas.ChargingPortUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Aktualizuje dane portu ładowania
    Args:
        id: ID portu
        port_update: Nowe dane portu
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Returns:
        schemas.ChargingPortOut: Zaktualizowany port
    """
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    
    if not port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nie znaleziono portu o ID: {id}"
        )
    
    if port_update.status and port_update.status not in [status.value for status in PortStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy status. Dozwolone wartości: {', '.join([status.value for status in PortStatus])}"
        )
    
    for key, value in port_update.dict(exclude_unset=True).items():
        setattr(port, key, value)
    
    try:
        db.commit()
        db.refresh(port)
        return port
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd aktualizacji portu: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_port(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Usuwa port ładowania
    Args:
        id: ID portu
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Raises:
        HTTPException: Gdy port nie zostanie znaleziony lub ma aktywne sesje
    """
    port_query = db.query(models.ChargingPort).filter(models.ChargingPort.id == id)
    port = port_query.first()

    if not port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nie znaleziono portu o ID: {id}"
        )
    
    active_sessions = db.query(models.ChargingSession).filter(
        models.ChargingSession.port_id == id,
        models.ChargingSession.end_time.is_(None)
    ).first()

    if active_sessions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można usunąć portu z aktywnymi sesjami ładowania"
        )

    try:
        port_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd usuwania portu: {str(e)}"
        )