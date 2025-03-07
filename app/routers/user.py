from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import engine, get_db

router = APIRouter(
    prefix="/User",
    tags=['User']
)

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: str, db: Session = Depends(get_db)):
    """
    Retrieves a single user by ID
    Args:
        id: User ID to find
        db: Database session
    Returns:
        schemas.UserOut: Found user data
    Raises:
        HTTPException: When user is not found
    """
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    
    return user

@router.get('/', response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """
    Retrieves all users from the database
    Args:
        db: Database session
    Returns:
        List[schemas.UserOut]: List of all users
    """
    users = db.query(models.User)
    return users.all()