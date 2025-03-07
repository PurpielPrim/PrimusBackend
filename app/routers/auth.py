from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .. import models, database
from ..config import settings
from typing import List
from .. import schemas

router = APIRouter(
    prefix="/auth",
    tags=['Uwierzytelnianie']
)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def decode_jwt_token(token: str) -> dict:
    """
    Dekoduje token JWT i weryfikuje jego poprawność
    Args:
        token: Token JWT do zdekodowania
    Returns:
        dict: Zdekodowana zawartość tokenu
    Raises:
        HTTPException: Gdy token jest nieprawidłowy lub wygasł
    """
    try:
        if not token:
            raise JWTError("Brak tokenu")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub wygasły token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Pobiera aktualnie zalogowanego użytkownika na podstawie tokenu JWT
    Args:
        token: Token JWT
        db: Sesja bazy danych
    Returns:
        models.User: Obiekt użytkownika
    Raises:
        HTTPException: Gdy autoryzacja się nie powiedzie
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nie dostarczono tokenu uwierzytelniającego",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nieprawidłowe dane uwierzytelniające",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nie znaleziono użytkownika", 
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autoryzacja nie powiodła się",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/protected-route/")
async def protected_route(user: dict = Depends(get_current_user)):
    """Chroniona ścieżka testowa"""
    return {"message": "Masz dostęp!", "user": user.email}

@router.get("/vehicles/", response_model=List[schemas.VehicleOut])
async def get_vehicles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Pobiera wszystkie pojazdy zalogowanego użytkownika
    Args:
        current_user: Zalogowany użytkownik
        db: Sesja bazy danych
    Returns:
        List[schemas.VehicleOut]: Lista pojazdów użytkownika
    """
    try:
        vehicles = (
            db.query(models.Vehicle)
            .filter(models.Vehicle.user_id == current_user.id)
            .all()
        )
        return vehicles
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas pobierania pojazdów: {str(e)}"
        )