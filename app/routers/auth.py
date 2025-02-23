from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .. import models, database
from ..config import settings
import logging
from typing import List
from .. import schemas

router = APIRouter(
    prefix="/auth",
    tags=['Authentication']
)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def decode_jwt_token(token: str) -> dict:
    try:
        logger.debug(f"Decoding token: {token}")
        if not token:
            raise JWTError("Token is null")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded payload: {payload}")
        return payload
    except JWTError as e:
        logger.error(f"JWT decoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # Add null check for token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found", 
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"Authenticated user: {user.email}")
        return user

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/protected-route/")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": "You have access!", "user": user.email}

@router.get("/vehicles/", response_model=List[schemas.VehicleOut])
async def get_vehicles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        logger.info(f"Getting vehicles for user ID: {current_user.id}")
        
        vehicles = (
            db.query(models.Vehicle)
            .filter(models.Vehicle.user_id == current_user.id)
            .all()
        )
        
        logger.info(f"Found {len(vehicles)} vehicles")
        return vehicles
        
    except Exception as e:
        logger.exception("Error fetching vehicles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )