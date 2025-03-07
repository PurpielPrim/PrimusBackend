from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/stations",
    tags=['Charging Stations']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingStationCreate)
def create_station(charging_station: schemas.ChargingStationCreate, db: Session = Depends(get_db)):
    """
    Creates a new charging station
    Args:
        charging_station: Station data to create
        db: Database session
    Returns:
        schemas.ChargingStationCreate: Created station
    """
    new_station = models.ChargingStation(**charging_station.dict())
    db.add(new_station)
    db.commit()
    db.refresh(new_station)
    return new_station

@router.get('/{id}', response_model=schemas.ChargingStationOut)
def get_station(id: str, db: Session = Depends(get_db)):
    """
    Gets a single charging station by ID
    Args:
        id: Station ID
        db: Database session
    Returns:
        schemas.ChargingStationOut: Found station
    Raises:
        HTTPException: When station is not found
    """
    station = db.query(models.ChargingStation).filter(models.ChargingStation.id == id).first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Station with id: {id} does not exist"
        )
    return station

@router.get('/', response_model=List[schemas.ChargingStationOut])
def get_all_stations(db: Session = Depends(get_db)):
    """
    Gets all charging stations
    Args:
        db: Database session
    Returns:
        List[schemas.ChargingStationOut]: List of all stations
    """
    stations = db.query(models.ChargingStation)
    return stations.all()

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_station(id: int, db: Session = Depends(get_db)):
    """
    Deletes a charging station
    Args:
        id: Station ID
        db: Database session
    Returns:
        Response: No content response on success
    Raises:
        HTTPException: When station is not found
    """
    station_query = db.query(models.ChargingStation).filter(models.ChargingStation.id == id)
    station = station_query.first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id: {id} does not exist"
        )

    station_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch('/{id}', response_model=schemas.ChargingStationOut)
def update_station(id: int, updated_station: schemas.ChargingStationUpdate, db: Session = Depends(get_db)):
    """
    Updates a charging station
    Args:
        id: Station ID
        updated_station: New station data
        db: Database session
    Returns:
        schemas.ChargingStationOut: Updated station
    Raises:
        HTTPException: When station is not found
    """
    station_query = db.query(models.ChargingStation).filter(models.ChargingStation.id == id)
    station = station_query.first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id: {id} does not exist"
        )

    station_query.update(updated_station.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return station_query.first()