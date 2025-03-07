from fastapi import status, Depends, HTTPException, APIRouter
from app import models
from app.schemas import DiscountIn, DiscountOut
from .auth import get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List
import time

router = APIRouter(
    prefix="/discounts",
    tags=["discounts"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DiscountOut)
def create_discount(
    discount: DiscountIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
): 
    existing_discount = db.query(models.Discount).filter(models.Discount.code == discount.code).first()
    if (existing_discount):
        raise HTTPException(status_code=400, detail="Discount code already exists")

    # Fix: Use datetime.utcnow() instead of datetime.datetime.utcnow()
    expiration_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0)
    new_discount = models.Discount(
        code=discount.code,
        description=discount.description,
        discount_percentage=discount.discount_percentage,
        expiration_date=expiration_date,
    )

    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)

    return new_discount

@router.get("/{code}", response_model=DiscountOut)
def get_discount(
    code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
): 
    discount = db.query(models.Discount).filter(models.Discount.code == code).first()

    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    if isinstance(discount.expiration_date, datetime):
        expiration_datetime = discount.expiration_date.replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        expiration_datetime = datetime.combine(discount.expiration_date, datetime.max.time())

    if expiration_datetime < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Discount code has expired")

    return discount

@router.delete("/expired", status_code=status.HTTP_204_NO_CONTENT)
def delete_expired_discounts(
    db: Session = Depends(get_db)
):
    expired_discounts = db.query(models.Discount).filter(models.Discount.expiration_date < datetime.utcnow()).all()

    if not expired_discounts:
        raise HTTPException(status_code=404, detail="No expired discounts found")

    for discount in expired_discounts:
        db.delete(discount)

    db.commit()  

    return {"detail": "Expired discounts deleted successfully"}

def delete_discount_and_return_percentage(discount_id: int, db: Session) -> int:
    discount = db.query(models.Discount).filter(models.Discount.id == discount_id).first()

    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    discount_percentage = discount.discount_percentage

    db.delete(discount)
    db.commit() 

    return discount_percentage

@router.get("/", response_model=List[DiscountOut])
def get_all_discounts(
    db: Session = Depends(get_db)
):
    """
    Pobiera wszystkie rabaty z bazy danych
    Args:
        db: Sesja bazy danych
    Returns:
        List[schemas.DiscountOut]: Lista wszystkich rabatów
    """
    discounts = db.query(models.Discount).all()
    return discounts

@router.post("/verify/{code}", response_model=dict)
def verify_discount(
    code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Weryfikuje kod rabatowy i zwraca jego wartość procentową
    """
    try:
        discount = db.query(models.Discount).filter(models.Discount.code == code.upper()).first()
        
        print(f"Verifying discount code: {code}")
        print(f"Found discount: {discount}")

        if not discount:
            return {
                "isValid": False,
                "percentage": 0,
                "message": "Kod rabatowy nie istnieje"
            }

        # Convert datetime.utcnow() to date for comparison
        current_date = datetime.utcnow().date()
        if discount.expiration_date < current_date:
            return {
                "isValid": False,
                "percentage": 0,
                "message": "Kod rabatowy wygasł"
            }

        return {
            "isValid": True,
            "percentage": discount.discount_percentage,
            "message": f"Kod rabatowy jest ważny (zniżka {discount.discount_percentage}%)"
        }
    except Exception as e:
        print(f"Error verifying discount: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Wystąpił błąd podczas weryfikacji kodu rabatowego: {str(e)}"
        )


