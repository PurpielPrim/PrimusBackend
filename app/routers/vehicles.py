from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/vehicles",
    tags=['Vehicles']
)

# Zarejestruj samochód
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.VehicleCreate)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    
    vehicle_data = vehicle.dict(exclude={"user_id"})
    new_vehicle = models.Vehicle(**vehicle_data, user_id=current_user.id)

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle

# Wypisz jeden samochód
@router.get('/{id}', response_model=schemas.VehicleOut)
def get_vehicle(id: int, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == id, models.Vehicle.user_id == current_user.id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vehicle with id: {id} does not exist"
        )
    
    return vehicle

# Wypisz wszystkie samochody
@router.get('/', response_model=List[schemas.VehicleOut])
def get_all_vehicles(db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.user_id == current_user.id).all()
    
    return vehicles