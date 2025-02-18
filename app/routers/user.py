from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/User",
    tags=['User']
)

# Wypisz jednego użytkownika
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: str, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                             detail=f"User with id: {id} does not exist")
    
    return user

# Wypisz wszystkich użytkowników
@router.get('/', response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    
    user = db.query(models.User)
    
    return user