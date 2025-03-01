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

# Delete station
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_station(id: int, db: Session = Depends(get_db)):
    station_query = db.query(models.ChargingStation).filter(models.ChargingStation.id == id)
    station = station_query.first()

    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Station with id: {id} does not exist")

    station_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update station
@router.patch('/{id}', response_model=schemas.ChargingStationOut)
def update_station(id: int, updated_station: schemas.ChargingStationUpdate, db: Session = Depends(get_db)):
    station_query = db.query(models.ChargingStation).filter(models.ChargingStation.id == id)
    station = station_query.first()

    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Station with id: {id} does not exist")

    station_query.update(updated_station.dict(exclude_unset=True), synchronize_session=False)
    db.commit()

    return station_query.first()