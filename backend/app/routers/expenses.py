import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Expense
from ..schemas import ExpenseCreate, ExpenseResponse
from ..auth import verify_api_key

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense entry."""
    expense = Expense(
        amount=payload.amount,
        category=payload.category,
        note=payload.note,
        date=payload.date,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime.date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[datetime.date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    List expenses with optional filters.

    - **category**: exact match (case-insensitive)
    - **start_date** / **end_date**: inclusive date range
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be on or before end_date",
        )

    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category.strip().lower())
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    return query.order_by(Expense.date.desc(), Expense.id.desc()).all()
