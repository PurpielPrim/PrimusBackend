from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/vehicles",
    tags=['Vehicles']
)

# Zarejestruj samochód
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.VehicleCreate)
def create_station(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):

    new_vehicle = models.Vehicle(**vehicle.dict())

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle

# Wypisz jeden samochód
@router.get('/{id}', response_model=schemas.VehicleOut)
def get_vehicle(id: int, db: Session = Depends(get_db)):
    
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == id).first()

    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f"Station with id: {id} does not exist")
    
    return vehicle

# Wypisz wszystkie samochody
@router.get('/', response_model=List[schemas.VehicleOut])
def get_all_vehicles(db: Session = Depends(get_db)):
    
    vehicle = db.query(models.Vehicle)
    
    return vehicle
