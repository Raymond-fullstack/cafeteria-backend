from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Debt, DebtStatus, Order, OrderItem, OrderStatus, Product, User, WalletTransaction


def _as_decimal(value) -> Decimal:
    return Decimal(str(value))


def create_order_for_user(db: Session, user: User, payload) -> Order:
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must include at least one item")

    product_ids = [item.product_id for item in payload.items]
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    product_map = {product.id: product for product in products}
    if len(product_map) != len(product_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more products were not found")

    total_amount = Decimal("0.00")
    order_items = []
    for item in payload.items:
        product = product_map[item.product_id]
        if item.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")
        line_total = _as_decimal(product.price) * item.quantity
        total_amount += line_total
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )

    order = Order(user_id=user.id, total_amount=total_amount, status=OrderStatus.PENDING, notes=payload.notes or "")
    db.add(order)
    db.flush()

    for item in order_items:
        item.order_id = order.id
        db.add(item)

    wallet_balance = _as_decimal(user.wallet_balance)
    if wallet_balance >= total_amount:
        user.wallet_balance = wallet_balance - total_amount
        order.status = OrderStatus.PAID
        db.add(
            WalletTransaction(
                user_id=user.id,
                order_id=order.id,
                type="debit",
                amount=total_amount,
                description=f"Payment for order #{order.id}",
            )
        )
    else:
        if wallet_balance > 0:
            user.wallet_balance = Decimal("0.00")
            db.add(
                WalletTransaction(
                    user_id=user.id,
                    order_id=order.id,
                    type="debit",
                    amount=wallet_balance,
                    description=f"Wallet contribution toward order #{order.id}",
                )
            )

        remaining_amount = total_amount - wallet_balance
        debt = Debt(
            user_id=user.id,
            amount=remaining_amount,
            remaining_amount=remaining_amount,
            status=DebtStatus.OPEN,
            notes=f"Outstanding debt created for order #{order.id}",
        )
        db.add(debt)
        order.status = OrderStatus.PENDING

    db.commit()
    db.refresh(order)
    return order


def top_up_wallet(db: Session, user: User, amount) -> User:
    amount = _as_decimal(amount)
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Top-up amount must be greater than zero")

    user.wallet_balance = _as_decimal(user.wallet_balance) + amount
    db.add(
        WalletTransaction(
            user_id=user.id,
            type="credit",
            amount=amount,
            description="Wallet top-up",
        )
    )
    db.commit()
    db.refresh(user)
    return user


def settle_debt(db: Session, user: User, debt: Debt, amount) -> Debt:
    amount = _as_decimal(amount)
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Settlement amount must be greater than zero")
    if debt.user_id != user.id and user.role not in {"admin", "manager", "cashier"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot settle this debt")
    if amount > debt.remaining_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Settlement exceeds remaining debt")

    debt.remaining_amount = debt.remaining_amount - amount
    user.wallet_balance = _as_decimal(user.wallet_balance) - amount
    if debt.remaining_amount == 0:
        debt.status = DebtStatus.PAID
    else:
        debt.status = DebtStatus.PARTIAL

    db.add(
        WalletTransaction(
            user_id=user.id,
            type="debit",
            amount=amount,
            description=f"Debt settlement for debt #{debt.id}",
        )
    )
    db.commit()
    db.refresh(debt)
    return debt


def get_dashboard_summary(db: Session):
    from app.models import User as UserModel

    total_users = db.query(UserModel).count()
    total_orders = db.query(Order).count()
    total_sales = sum((order.total_amount for order in db.query(Order).all()), Decimal("0.00"))
    outstanding_debt = sum((debt.remaining_amount for debt in db.query(Debt).filter(Debt.status != DebtStatus.PAID).all()), Decimal("0.00"))
    available_wallet_value = sum((user.wallet_balance for user in db.query(UserModel).all()), Decimal("0.00"))
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "outstanding_debt": outstanding_debt,
        "available_wallet_value": available_wallet_value,
    }
