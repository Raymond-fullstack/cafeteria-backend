from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import Debt, DebtStatus, User, UserRole
from app.schemas import DebtRead, DebtSettlement
from app.security import get_current_user
from app.services import settle_debt

router = APIRouter(prefix="/api/debts", tags=["debts"])


@router.get("", response_model=list[DebtRead])
def list_debts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role in {UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER}:
        return db.query(Debt).all()
    return db.query(Debt).filter(Debt.user_id == current_user.id).all()


@router.post("/{debt_id}/settle")
def settle_debt_route(debt_id: int, payload: DebtSettlement, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found")
    if current_user.role not in {UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER} and debt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    settle_debt(db, current_user, debt, payload.amount)
    return {"message": "Debt settled successfully"}
