from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import logging
from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=['Charging Sessions']
)

def end_charging_session(session_id: int, db: Session, end_time: datetime):
    session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if session and session.status == "IN_PROGRESS":
        session.end_time = end_time
        session.status = "DONE"

        # Obliczenie zużytej energii na podstawie czasu ładowania
        charging_time_hours = (session.end_time - session.start_time).total_seconds() / 3600
        session.energy_used_kWh = min(charging_time_hours * 22, 50)  # Przykładowo: 22 kW mocy, max 50 kWh
        session.total_cost = session.energy_used_kWh * 0.2  # Przykładowa cena 0.2 za kWh

        db.commit()
        db.refresh(session)

@router.post("/start", response_model=schemas.ChargingSessionBase)
def add_log(
    session_data: schemas.ChargingSessionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    # Sprawdzenie pojazdu i portu
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == session_data.vehicle_id,
        models.Vehicle.user_id == user_id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found or does not belong to user")

    port = db.query(models.ChargingPort).filter(models.ChargingPort.id == session_data.port_id).first()
    if not port:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Charging port not found")

    # Tworzenie sesji ładowania
    new_session = models.ChargingSession(
        user_id=user_id,
        vehicle_id=session_data.vehicle_id,
        port_id=session_data.port_id,
        start_time=datetime.utcnow(),
        end_time=None,
        energy_used_kWh=0.0,
        total_cost=0.0,
        status="IN_PROGRESS"
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Zaplanowanie zakończenia sesji po podanym czasie
    end_time = datetime.utcnow() + timedelta(minutes=session_data.duration_minutes)
    background_tasks.add_task(end_charging_session, new_session.id, db, end_time)

    return new_session

@router.get("/", response_model=List[schemas.ChargingSessionOut])
async def get_charging_sessions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        sessions = (
            db.query(models.ChargingSession)
            .filter(models.ChargingSession.user_id == current_user.id)
            .all()
        )
        logger.info(f"Found {len(sessions)} charging sessions for user {current_user.id}")
        return sessions
    except Exception as e:
        logger.error(f"Error fetching charging sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch charging sessions"
        )