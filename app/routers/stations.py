from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/stations",
    tags=['Charging Stations']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ChargingStationBase)
def create_station(charging_station: schemas.CreateChargingStation, db: Session = Depends(get_db)):

    new_station = models.ChargingStation(**charging_station.dict())

    db.add(new_station)
    db.commit()
    db.refresh(new_station)

    return new_station