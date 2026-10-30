from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import Order, OrderStatus, User, UserRole
from app.schemas import OrderCreate, OrderRead
from app.security import get_current_user
from app.services import create_order_for_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER, UserRole.STAFF))):
    if current_user.role == UserRole.CUSTOMER:
        return db.query(Order).filter(Order.user_id == current_user.id).all()
    return db.query(Order).all()


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = create_order_for_user(db, current_user, payload)
    return order


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if current_user.role not in {UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER} and order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return order


@router.put("/{order_id}/status")
def update_order_status(order_id: int, status_value: str, db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if status_value not in {OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.CANCELLED}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    order.status = status_value
    db.commit()
    return {"message": "Order status updated", "status": order.status}
