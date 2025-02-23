from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# Stwórz nową płatność
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PaymentOut)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_payment = models.Payment(**payment.dict())
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

# Wypisz jedną płatność dla użytkownika
@router.get("/{id}", response_model=schemas.PaymentOut)
def get_payment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    return payment

# Wypisz wszystkie płatności dla użytkownika
@router.get("/", response_model=List[schemas.PaymentOut])
async def get_payments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        payments = (
            db.query(models.Payment)
            .filter(models.Payment.user_id == current_user.id)
            .all()
        )
        return payments
    except Exception as e:
        logger.error(f"Error fetching payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )

# Zaktualizuj płatność
@router.put("/{id}", response_model=schemas.PaymentOut)
def update_payment(
    id: int,
    payment_update: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    for key, value in payment_update.dict().items():
        setattr(payment, key, value)
    
    db.commit()
    db.refresh(payment)
    
    return payment

# Usuń płatność
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    
    return