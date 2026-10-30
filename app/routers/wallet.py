from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import User, UserRole, WalletTransaction
from app.schemas import WalletSummary, WalletTopUp
from app.security import get_current_user

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


@router.get("/summary", response_model=WalletSummary)
def wallet_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(WalletTransaction).filter(WalletTransaction.user_id == current_user.id).order_by(WalletTransaction.created_at.desc()).limit(10).all()
    return {"user_id": current_user.id, "wallet_balance": current_user.wallet_balance, "recent_transactions": transactions}


@router.post("/top-up")
def top_up_wallet(payload: WalletTopUp, db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER))):
    if payload.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")
    current_user.wallet_balance += payload.amount
    db.add(WalletTransaction(user_id=current_user.id, type="credit", amount=payload.amount, description="Wallet top-up"))
    db.commit()
    return {"message": "Wallet top-up successful", "balance": current_user.wallet_balance}
