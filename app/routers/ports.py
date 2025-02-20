from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/ports",
    tags=['Charging Ports']
)

# Stwórz port
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingPortOut)
def create_port(charging_port: schemas.ChargingPortCreate, db: Session = Depends(get_db)):
    new_port = models.ChargingPort(**charging_port.dict())
    db.add(new_port)
    db.commit()
    db.refresh(new_port)
    print(f"Charging port {new_port.id} is connected to station {new_port.station_id}")
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
    ports = db.query(models.ChargingPort).all()
    for port in ports:
        print(f"Charging port {port.id} is connected to station {port.station_id}")
    return ports