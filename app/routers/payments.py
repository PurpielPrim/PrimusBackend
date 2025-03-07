from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user
from app.routers.discount import delete_discount_and_return_percentage

router = APIRouter(
    prefix="/payments",
    tags=["Płatności"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PaymentOut)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    discount_code_id: int = Query(None)  # Opcjonalne pole dla kodu rabatowego
): 
    """
    Tworzy nową płatność
    Args:
        payment: Dane płatności do utworzenia
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
        discount_code_id: Opcjonalny identyfikator kodu rabatowego
    Returns:
        schemas.PaymentOut: Utworzona płatność
    """
    
    if discount_code_id:
        discount_percentage = None
        try:
            discount_percentage = delete_discount_and_return_percentage(discount_code_id, db)
        except HTTPException:
            discount_percentage = None  
        
        if discount_percentage:
            payment.price = payment.price * (1 - discount_percentage / 100)
    
    new_payment = models.Payment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

@router.get("/{id}", response_model=schemas.PaymentOut)
def get_payment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Pobiera pojedynczą płatność
    Args:
        id: ID płatności
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Returns:
        schemas.PaymentOut: Znaleziona płatność
    Raises:
        HTTPException: Gdy płatność nie zostanie znaleziona
    """
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Nie znaleziono płatności"
        )
    return payment

@router.get("/", response_model=List[schemas.PaymentOut])
async def get_payments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pobiera wszystkie płatności użytkownika
    Args:
        current_user: Aktualnie zalogowany użytkownik
        db: Sesja bazy danych
    Returns:
        List[schemas.PaymentOut]: Lista płatności użytkownika
    """
    try:
        payments = (
            db.query(models.Payment)
            .filter(models.Payment.user_id == current_user.id)
            .order_by(models.Payment.created_at.desc())
            .all()
        )
        return payments if payments else []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd podczas pobierania płatności: {str(e)}"
        )

@router.put("/{id}", response_model=schemas.PaymentOut)
def update_payment(
    id: int,
    payment_update: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Aktualizuje płatność
    Args:
        id: ID płatności do aktualizacji
        payment_update: Nowe dane płatności
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Returns:
        schemas.PaymentOut: Zaktualizowana płatność
    """
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Nie znaleziono płatności"
        )
    
    for key, value in payment_update.dict().items():
        setattr(payment, key, value)
    
    db.commit()
    db.refresh(payment)
    return payment

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Usuwa płatność
    Args:
        id: ID płatności do usunięcia
        db: Sesja bazy danych
        current_user: Aktualnie zalogowany użytkownik
    Raises:
        HTTPException: Gdy płatność nie zostanie znaleziona
    """
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Nie znaleziono płatności"
        )
    
    db.delete(payment)
    db.commit()