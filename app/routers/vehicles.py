from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db
from ..routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/vehicles",
    tags=['Vehicles']
)

# Zarejestruj samochód
@router.post("/", response_model=schemas.VehicleOut, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle: schemas.VehicleCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Creating vehicle for user {current_user.id}")
        logger.debug(f"Vehicle data: {vehicle.dict()}")
        
        new_vehicle = models.Vehicle(
            **vehicle.dict(),
            user_id=current_user.id
        )
        
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        
        logger.info(f"Successfully created vehicle {new_vehicle.id}")
        return new_vehicle
        
    except Exception as e:
        logger.exception("Failed to create vehicle")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create vehicle",
                "error": str(e)
            }
        )

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
@router.get("/", response_model=List[schemas.VehicleOut])
async def get_vehicles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Getting vehicles for user ID: {current_user.id}")
    
    try:
        vehicles = (
            db.query(models.Vehicle)
            .filter(models.Vehicle.user_id == current_user.id)
            .all()
        )
        
        logger.info(f"Found {len(vehicles)} vehicles for user {current_user.id}")
        return vehicles
        
    except Exception as e:
        logger.exception("Error fetching vehicles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to fetch vehicles",
                "error": str(e)
            }
        )