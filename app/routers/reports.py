from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_roles
from app.models import Debt, Order, User, UserRole, WalletTransaction
from app.reports import generate_excel_report, generate_pdf_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/financial.xlsx")
def download_excel(db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER))):
    rows = []
    for transaction in db.query(WalletTransaction).order_by(WalletTransaction.created_at.desc()).all():
        rows.append({
            "date": str(transaction.created_at.date()),
            "description": transaction.description,
            "amount": float(transaction.amount),
            "balance": float(transaction.amount),
        })
    content = generate_excel_report(rows)
    return Response(content=content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=financial-report.xlsx"})


@router.get("/financial.pdf")
def download_pdf(db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CASHIER))):
    rows = []
    for transaction in db.query(WalletTransaction).order_by(WalletTransaction.created_at.desc()).all():
        rows.append({
            "date": str(transaction.created_at.date()),
            "description": transaction.description,
            "amount": float(transaction.amount),
            "balance": float(transaction.amount),
        })
    content = generate_pdf_report(rows)
    return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=financial-report.pdf"})
