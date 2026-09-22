from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Expense
from ..schemas import SummaryResponse, CategoryTotal, MonthlySpend, SpendAlert
from ..auth import verify_api_key

router = APIRouter(prefix="/summary", tags=["summary"], dependencies=[Depends(verify_api_key)])


@router.get("", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    """
    Return a spending summary:
    - total_spend: sum of all expenses
    - by_category: total per category
    - month_over_month: per-month totals with % change from previous month
    - alerts: categories where current month spend increased >20% vs previous month
    """
    expenses = db.query(Expense).all()

    if not expenses:
        return SummaryResponse(
            total_spend=0.0,
            by_category=[],
            month_over_month=[],
            alerts=[],
        )

    # ── Totals ────────────────────────────────────────────────────────────
    total_spend = sum(e.amount for e in expenses)

    # ── By category ───────────────────────────────────────────────────────
    cat_totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        cat_totals[e.category] += e.amount

    by_category = [
        CategoryTotal(category=cat, total=round(total, 2))
        for cat, total in sorted(cat_totals.items())
    ]

    # ── Month-over-month ──────────────────────────────────────────────────
    month_totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        key = e.date.strftime("%Y-%m")
        month_totals[key] += e.amount

    sorted_months = sorted(month_totals.keys())
    month_over_month: list[MonthlySpend] = []
    for i, month in enumerate(sorted_months):
        total = round(month_totals[month], 2)
        change_pct = None
        if i > 0:
            prev = month_totals[sorted_months[i - 1]]
            if prev > 0:
                change_pct = round(((total - prev) / prev) * 100, 2)
        month_over_month.append(MonthlySpend(month=month, total=total, change_pct=change_pct))

    # ── Alerts: >20% category increase vs previous month ──────────────────
    # Build per-category-per-month totals
    cat_month_totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for e in expenses:
        key = e.date.strftime("%Y-%m")
        cat_month_totals[e.category][key] += e.amount

    alerts: list[SpendAlert] = []
    if len(sorted_months) >= 2:
        current_month = sorted_months[-1]
        previous_month = sorted_months[-2]

        for cat in sorted(cat_month_totals.keys()):
            prev_val = cat_month_totals[cat].get(previous_month, 0)
            curr_val = cat_month_totals[cat].get(current_month, 0)

            if prev_val > 0 and curr_val > prev_val:
                pct = ((curr_val - prev_val) / prev_val) * 100
                if pct > 20:
                    alerts.append(
                        SpendAlert(
                            category=cat,
                            current_month=current_month,
                            previous_month=previous_month,
                            change_pct=round(pct, 2),
                            message=(
                                f"Spending on '{cat}' increased {round(pct, 1)}% "
                                f"from {previous_month} (₹{prev_val:.2f}) "
                                f"to {current_month} (₹{curr_val:.2f})"
                            ),
                        )
                    )

    return SummaryResponse(
        total_spend=round(total_spend, 2),
        by_category=by_category,
        month_over_month=month_over_month,
        alerts=alerts,
    )
