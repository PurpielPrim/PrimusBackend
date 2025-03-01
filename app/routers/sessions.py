from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, timezone
from typing import List
import logging
from .. import models, schemas
from ..database import get_db
from .auth import get_current_user
from sqlalchemy import text  # Add this import at the top

COST_PER_KWH = 1.0  # 1 PLN per kWh

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=['Charging Sessions']
)

def end_charging_session(session_id: int, db: Session, end_time: datetime):
    session = db.query(models.ChargingSession).filter(models.ChargingSession.id == session_id).first()
    if session and session.status == "IN_PROGRESS":
        try:
            # Calculate charging duration
            start_time = session.start_time.replace(tzinfo=timezone.utc) if session.start_time.tzinfo is None else session.start_time
            end_time = end_time.replace(tzinfo=timezone.utc) if end_time.tzinfo is None else end_time
            charging_time_hours = (end_time - start_time).total_seconds() / 3600
            
            # Get vehicle and update its battery capacity
            vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == session.vehicle_id).first()
            if vehicle:
                # Log initial battery condition
                initial_condition = vehicle.battery_condition
                
                max_charge = vehicle.battery_capacity_kwh
                current_charge = vehicle.current_battery_capacity_kw
                charge_rate = min(22, vehicle.max_charging_powerkwh)
                
                # Calculate new charge level
                charge_added = charging_time_hours * charge_rate
                new_charge = min(max_charge, current_charge + charge_added)
                
                logger.info(f"Final battery update for vehicle {vehicle.id}:")
                logger.info(f"Current charge: {current_charge} kWh")
                logger.info(f"Charge added: {charge_added} kWh")
                logger.info(f"New charge: {new_charge} kWh")
                logger.info(f"Cost per kWh: {COST_PER_KWH}")
                
                # Only update current battery capacity, not battery condition
                vehicle.current_battery_capacity_kw = new_charge
                
                # Log if battery condition changed
                if vehicle.battery_condition != initial_condition:
                    logger.warning(f"Battery condition changed from {initial_condition} to {vehicle.battery_condition}")
                
                # Update session with correct cost calculation
                session.end_time = end_time
                session.status = "COMPLETED"
                session.energy_used_kwh = charge_added
                session.total_cost = calculate_cost(charge_added)  # Use calculate_cost instead of direct multiplication
                
                db.commit()
                db.refresh(vehicle)
                db.refresh(session)
                
                logger.info(f"Successfully completed charging session {session_id}")
                return session
            else:
                raise HTTPException(status_code=404, detail="Vehicle not found")
                
        except Exception as e:
            logger.error(f"Error in end_charging_session: {str(e)}")
            db.rollback()
            raise

@router.post("/start", response_model=schemas.ChargingSessionBase)
def add_log(
    session_data: schemas.ChargingSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        new_session = models.ChargingSession(
            user_id=str(current_user.id),  # Convert to string
            vehicle_id=session_data.vehicle_id,
            port_id=session_data.port_id,
            start_time=datetime.utcnow(),
            energy_used_kwh=float(session_data.energy_used_kwh),  # Ensure float
            total_cost=float(session_data.total_cost),  # Ensure float
            status=session_data.status
            # Remove current_battery_capacity_kw as it's not in the model
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return new_session
    except Exception as e:
        logger.error(f"Error creating charging session: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create charging session: {str(e)}"
        )

def calculate_cost(energy_used: float) -> float:
    """Calculate cost using the same logic as frontend"""
    return max(0, energy_used * COST_PER_KWH)

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
        if new_capacity is None:
            raise HTTPException(
                status_code=400,
                detail="current_battery_capacity_kw is required"
            )

        # Get vehicle
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == session.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Calculate charge added based on the difference
        charge_added = max(0, new_capacity - vehicle.current_battery_capacity_kw)

        logger.info(f"Stopping session {session_id}:")
        logger.info(f"Current capacity: {vehicle.current_battery_capacity_kw} kWh")
        logger.info(f"New capacity: {new_capacity} kWh")
        logger.info(f"Charge added: {charge_added} kWh")

        # Update vehicle capacity
        vehicle.current_battery_capacity_kw = new_capacity

        # Calculate cost based on energy used - using same logic as frontend
        total_cost = calculate_cost(charge_added)

        # Update session
        session.end_time = datetime.utcnow()
        session.status = "COMPLETED"
        session.energy_used_kwh = charge_added
        session.total_cost = total_cost

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
        "duration_minutes": session.duration_minutes  # Use the calculated property
    }

@router.patch("/{session_id}/update", response_model=schemas.ChargingSessionOut)
def update_session_state(
    session_id: int,
    session_update: schemas.ChargingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        # Add request logging
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
        
        # Log current session state
        logger.info(f"Current session state:")
        logger.info(f"Energy used: {session.energy_used_kwh} kWh")
        logger.info(f"Total cost: {session.total_cost} PLN")
        
        # Use the energy_used_kwh directly from the update
        energy_used = max(0, session_update.energy_used_kwh)
        total_cost = calculate_cost(energy_used)
        
        logger.info(f"Calculated values:")
        logger.info(f"Energy used: {energy_used} kWh")
        logger.info(f"Total cost: {total_cost} PLN")
        
        # Update session
        session.energy_used_kwh = energy_used
        session.total_cost = total_cost
        
        # Log after update
        logger.info(f"Updated session values:")
        logger.info(f"Energy used: {session.energy_used_kwh} kWh")
        logger.info(f"Total cost: {session.total_cost} PLN")
        
        db.commit()
        db.refresh(session)
        
        # Log final state
        logger.info(f"Final session state after refresh:")
        logger.info(f"Energy used: {session.energy_used_kwh} kWh")
        logger.info(f"Total cost: {session.total_cost} PLN")
            
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