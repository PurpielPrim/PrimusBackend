from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db
from ..routers.auth import get_current_user
from sqlalchemy import text

router = APIRouter(
    prefix="/vehicles",
    tags=['Vehicles']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.VehicleCreate)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Creates a new vehicle entry
    Args:
        vehicle: Vehicle data to create
        db: Database session
        current_user: Currently authenticated user
    Returns:
        schemas.VehicleCreate: Created vehicle
    """
    vehicle_data = vehicle.dict(exclude={"user_id"})
    new_vehicle = models.Vehicle(**vehicle_data, user_id=current_user.id)

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle

@router.put("/{license_plate}", response_model=schemas.VehicleOut)
def update_vehicle(license_plate: str, vehicle_update: schemas.VehicleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Updates vehicle information
    Args:
        license_plate: Vehicle license plate
        vehicle_update: Updated vehicle data
        db: Database session
        current_user: Currently authenticated user
    Returns:
        schemas.VehicleOut: Updated vehicle
    Raises:
        HTTPException: When vehicle is not found or user is not authorized
    """
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.license_plate == license_plate).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this vehicle"
        )
    
    update_data = vehicle_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle

@router.get('/{id}', response_model=schemas.VehicleOut)
def get_vehicle(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves a single vehicle
    Args:
        id: Vehicle ID
        db: Database session
        current_user: Currently authenticated user
    Returns:
        schemas.VehicleOut: Found vehicle
    Raises:
        HTTPException: When vehicle is not found
    """
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == id, models.Vehicle.user_id == current_user.id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Vehicle with id: {id} does not exist"
        )
    
    return vehicle

@router.get('/', response_model=List[schemas.VehicleOut])
def get_all_vehicles(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves all vehicles for the current user
    Args:
        db: Database session
        current_user: Currently authenticated user
    Returns:
        List[schemas.VehicleOut]: List of user's vehicles
    """
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.user_id == current_user.id).all()
    return vehicles

@router.patch("/{vehicle_id}/capacity")
def update_vehicle_capacity(
    vehicle_id: int,
    capacity_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Updates vehicle battery capacity
    Args:
        vehicle_id: Vehicle ID
        capacity_update: New capacity data
        db: Database session
        current_user: Currently authenticated user
    Returns:
        dict: Updated vehicle battery information
    Raises:
        HTTPException: When vehicle is not found or capacity value is invalid
    """
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == vehicle_id,
        models.Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    try:
        new_capacity = float(capacity_update["current_battery_capacity_kw"])
        
        if new_capacity < 0 or new_capacity > vehicle.battery_capacity_kwh:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid battery capacity value. Must be between 0 and {vehicle.battery_capacity_kwh}"
            )
            
        vehicle.current_battery_capacity_kw = new_capacity
        db.commit()
        db.refresh(vehicle)
        
        return {
            "id": vehicle.id,
            "current_battery_capacity_kw": new_capacity,
            "battery_capacity_kWh": vehicle.battery_capacity_kwh,
            "battery_condition": vehicle.battery_condition
        }
        
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")