from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from datetime import date
from enum import Enum
from .. import models, schemas
from ..database import engine, get_db
from ..routers.auth import get_current_user  # Add this import

router = APIRouter(
    prefix="/ports",
    tags=['Charging Ports']
)

class PortStatus(str, Enum):
    WOLNY = 'wolny'
    ZAJETY = 'zajety'
    NIECZYNNY = 'nieczynny'

# Stwórz port
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingPortOut)
def create_port(
    charging_port: schemas.ChargingPortCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Add this line
):
    new_port = models.ChargingPort(**charging_port.dict())
    db.add(new_port)
    db.commit()
    db.refresh(new_port)
    return new_port

# Wypisz jeden port
@router.get('/{id}', response_model=schemas.ChargingPortOut)
def get_port(id: int, db: Session = Depends(get_db)):
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    if not port:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Charging port with id: {id} does not exist")
    print(f"Charging port {port.id} is connected to station {port.station_id}")
    return port

# Wypisz wszystkie porty
@router.get('/', response_model=List[schemas.ChargingPortOut])
def get_all_ports(db: Session = Depends(get_db)):
    # Remove authentication requirement for GET /ports
    ports = db.query(models.ChargingPort).all()
    
    # Set default last_service_date if None
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
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
    
    new_status = status_update.get('status')
    if new_status not in [status.value for status in PortStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join([status.value for status in PortStatus])}"
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
    # Find the port
    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == id).first()
    
    # Check if port exists
    if not port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Port with id: {id} does not exist"
        )
    
    # Validate status if it's being updated
    if port_update.status and port_update.status not in [status.value for status in PortStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join([status.value for status in PortStatus])}"
        )
    
    # Update port attributes
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
            detail=f"Failed to update port: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_port(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Find the port
    port_query = db.query(models.ChargingPort).filter(models.ChargingPort.id == id)
    port = port_query.first()

    # Check if port exists
    if not port:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Port with id: {id} does not exist"
        )
    
    # Check for active sessions
    active_sessions = db.query(models.ChargingSession).filter(
        models.ChargingSession.port_id == id,
        models.ChargingSession.end_time.is_(None)
    ).first()

    if active_sessions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete port with active charging sessions"
        )

    try:
        # Delete the port
        port_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete port: {str(e)}"
        )