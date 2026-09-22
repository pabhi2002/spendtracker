import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Request schemas ──────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount, must be positive")
    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    note: Optional[str] = Field(None, max_length=500, description="Optional note")
    date: datetime.date = Field(..., description="Date of the expense (YYYY-MM-DD)")

    @field_validator("category")
    @classmethod
    def category_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Category must not be blank")
        return stripped.lower()


# ── Response schemas ─────────────────────────────────────────────────────────

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    note: Optional[str]
    date: datetime.date
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthlySpend(BaseModel):
    month: str  # "YYYY-MM"
    total: float
    change_pct: Optional[float] = None  # % change vs previous month


class SpendAlert(BaseModel):
    category: str
    current_month: str
    previous_month: str
    change_pct: float
    message: str


class SummaryResponse(BaseModel):
    total_spend: float
    by_category: list[CategoryTotal]
    month_over_month: list[MonthlySpend]
    alerts: list[SpendAlert]
