from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, timezone
from typing import List
import logging
from .. import models, schemas
from ..database import get_db
from .auth import get_current_user
from sqlalchemy import text

COST_PER_KWH = 1.0

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=['Charging Sessions']
)

def end_charging_session(session_id: int, db: Session, end_time: datetime):
    """
    Ends a charging session and updates vehicle battery state
    Args:
        session_id: ID of the session to end
        db: Database session
        end_time: Time when charging ended
    Returns:
        models.ChargingSession: Updated session
    Raises:
        HTTPException: When vehicle is not found or update fails
    """
    session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if session and session.status == "IN_PROGRESS":
        try:
            start_time = session.start_time.replace(tzinfo=timezone.utc) if session.start_time.tzinfo is None else session.start_time
            end_time = end_time.replace(tzinfo=timezone.utc) if end_time.tzinfo is None else end_time
            charging_time_hours = (end_time - start_time).total_seconds() / 3600
            
            vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == session.vehicle_id).first()
            if vehicle:
                max_charge = vehicle.battery_capacity_kwh
                current_charge = vehicle.current_battery_capacity_kw
                charge_rate = min(22, vehicle.max_charging_powerkwh)
                
                charge_added = charging_time_hours * charge_rate
                new_charge = min(max_charge, current_charge + charge_added)
                
                vehicle.current_battery_capacity_kw = new_charge
                
                session.end_time = end_time
                session.status = "COMPLETED"
                session.energy_used_kwh = charge_added
                session.total_cost = calculate_cost(charge_added)
                
                db.commit()
                db.refresh(vehicle)
                db.refresh(session)
                
                return session
            else:
                raise HTTPException(status_code=404, detail="Vehicle not found")
                
        except Exception as e:
            db.rollback()
            raise

def calculate_cost(energy_used: float) -> float:
    """
    Calculates charging cost
    Args:
        energy_used: Amount of energy used in kWh
    Returns:
        float: Cost in currency units
    """
    return max(0, energy_used * COST_PER_KWH)

@router.post("/start", response_model=schemas.ChargingSessionBase)
def add_log(
    session_data: schemas.ChargingSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Creates a new charging session
    Args:
        session_data: Session details
        db: Database session
        current_user: Currently authenticated user
    Returns:
        schemas.ChargingSessionBase: Created session
    """
    try:
        new_session = models.ChargingSession(
            user_id=str(current_user.id),
            vehicle_id=session_data.vehicle_id,
            port_id=session_data.port_id,
            start_time=datetime.utcnow(),
            energy_used_kwh=float(session_data.energy_used_kwh),
            total_cost=float(session_data.total_cost),
            status=session_data.status,
            payment_status="PENDING"
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return new_session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create charging session: {str(e)}"
        )

@router.post("/{session_id}/stop", response_model=schemas.ChargingSessionBase)
def stop_charging_session_endpoint(
    session_id: int,
    capacity_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        session = db.query(models.ChargingSession).filter(
            models.ChargingSession.id == session_id,
            models.ChargingSession.user_id == current_user.id,
            models.ChargingSession.status == "IN_PROGRESS"
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Active session not found")

        new_capacity = capacity_update.get('current_battery_capacity_kw')
        energy_used = capacity_update.get('energy_used_kwh')
        total_cost = capacity_update.get('total_cost')

        if new_capacity is None:
            raise HTTPException(
                status_code=400,
                detail="current_battery_capacity_kw is required"
            )

        # Get vehicle
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == session.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Update vehicle capacity
        vehicle.current_battery_capacity_kw = new_capacity

        # Update session with values from frontend
        session.end_time = datetime.utcnow()
        session.status = "COMPLETED"
        session.energy_used_kwh = energy_used or 0
        session.total_cost = total_cost or 0

        db.commit()
        db.refresh(vehicle)
        db.refresh(session)

        return session

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop charging session: {str(e)}"
        )

@router.get("/", response_model=List[schemas.ChargingSessionOut])
async def get_charging_sessions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Update the query to explicitly select all columns
        sessions = db.query(models.ChargingSession).filter(
            models.ChargingSession.user_id == str(current_user.id)  # Ensure user_id is string
        ).all()
        
        # Add debug logging
        logger.info(f"Query result: {sessions}")
        for session in sessions:
            logger.info(f"Session ID: {session.id}")
            logger.info(f"Vehicle ID: {session.vehicle_id}")
            logger.info(f"Port ID: {session.port_id}")
            
        return sessions
        
    except Exception as e:
        logger.error(f"Error fetching charging sessions: {str(e)}")
        # Add more detailed error logging
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch charging sessions: {str(e)}"
        )

@router.get("/active", response_model=schemas.ChargingSessionBase)
def get_active_session(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = db.query(models.ChargingSession).filter(
        models.ChargingSession.user_id == current_user.id,
        models.ChargingSession.status == "IN_PROGRESS"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active charging session found"
        )
    
    return session

@router.get("/active/{port_id}", response_model=List[schemas.ChargingSessionOut])
def get_active_sessions_for_port(
    port_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    active_sessions = db.query(models.ChargingSession).filter(
        models.ChargingSession.port_id == port_id,
        models.ChargingSession.status == "IN_PROGRESS"
    ).all()
    
    return active_sessions

@router.get("/{session_id}", response_model=schemas.ChargingSessionBase)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        **session.__dict__,
        "duration_minutes": session.duration_minutes,
        "vehicle_id": session.vehicle_id  # Explicitly include vehicle_id
    }

@router.patch("/{session_id}/update", response_model=schemas.ChargingSessionOut)
def update_session_state(
    session_id: int,
    session_update: schemas.ChargingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        logger.info(f"Received update request for session {session_id}:")
        logger.info(f"Update data: {session_update.dict()}")

        session = db.query(models.ChargingSession).filter(
            models.ChargingSession.id == session_id,
            models.ChargingSession.user_id == current_user.id,
            models.ChargingSession.status == "IN_PROGRESS"
        ).first()
        
        if not session:
            logger.error(f"No active session found for ID {session_id}")
            raise HTTPException(status_code=404, detail="Active session not found")
        
        # Use values directly from frontend
        session.energy_used_kwh = float(session_update.energy_used_kwh)
        session.total_cost = float(session_update.total_cost)
        
        # If current_battery_level is provided, update vehicle battery level
        if session_update.current_battery_level is not None:
            vehicle = db.query(models.Vehicle).filter(
                models.Vehicle.id == session.vehicle_id
            ).first()
            if vehicle:
                vehicle.current_battery_capacity_kw = float(session_update.current_battery_level)
        
        db.commit()
        db.refresh(session)
            
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )

# Add a new endpoint to update payment status
@router.patch("/{session_id}/payment", response_model=schemas.ChargingSessionOut)
def update_payment_status(
    session_id: int,
    payment_status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        session = db.query(models.ChargingSession).filter(
            models.ChargingSession.id == session_id,
            models.ChargingSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.payment_status = payment_status
        db.commit()
        db.refresh(session)
            
        return session
        
    except Exception as e:
        logger.error(f"Error updating payment status for session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update payment status: {str(e)}"
        )