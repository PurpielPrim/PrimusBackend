from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/stations",
    tags=['Charging Stations']
)

# Stwórz stację
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingStationCreate)
def create_station(charging_station: schemas.ChargingStationCreate, db: Session = Depends(get_db)):

    new_station = models.ChargingStation(**charging_station.dict())

    db.add(new_station)
    db.commit()
    db.refresh(new_station)

    return new_station

# Wypisz jedną stację
@router.get('/{id}', response_model=schemas.ChargingStationOut)
def get_station(id: str, db: Session = Depends(get_db)):
    
    station = db.query(models.ChargingStation).filter(models.ChargingStation.id == id).first()

    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f"Station with id: {id} does not exist")
    
    return station

# Wypisz wszystkie stacje
@router.get('/', response_model=List[schemas.ChargingStationOut])
def get_all_stations(db: Session = Depends(get_db)):
    
    station = db.query(models.ChargingStation)
    
    return station