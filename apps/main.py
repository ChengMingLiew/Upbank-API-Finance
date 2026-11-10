import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import HTMLResponse
from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from apps.db import get_session
from apps.models.account import Account
from apps.models.transaction import Transaction

BASE_DIR = Path(__file__).resolve().parent
LOCAL_TZ = ZoneInfo("Australia/Sydney")
PAGE_SIZE = 10

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(request, "error_page.html", status_code=exc.status_code, context={"error": exc})


def money(amount_in_cents: int) -> str:
    dollars = abs(amount_in_cents) / 100
    sign = "-" if amount_in_cents < 0 else ""
    return f"{sign}${dollars:,.2f}"


templates.env.filters["money"] = money


def local_date(value: datetime) -> str:
    return value.astimezone(LOCAL_TZ).strftime("%d %b %Y")


templates.env.filters["local_date"] = local_date


def month_range(year_month: str) -> tuple[datetime, datetime]:
    """Turn 'YYYY-MM' into [start of month, start of next month) in local time."""
    year, month = map(int, year_month.split("-"))
    start = datetime(year, month, 1, tzinfo=LOCAL_TZ)

    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=LOCAL_TZ)
    else:
        end = datetime(year, month + 1, 1, tzinfo=LOCAL_TZ)

    return start, end


def get_month_options(db: Session) -> list[dict[str, str]]:
    """Every month that has transactions, newest first, for the dropdown."""
    local_created = func.timezone(str(LOCAL_TZ), Transaction.created_at)
    year_expr = extract("year", local_created).label("year")
    month_expr = extract("month", local_created).label("month")

    stmt = (
        select(year_expr, month_expr)
        .distinct()
        .order_by(year_expr.desc(), month_expr.desc())
    )

    options = []
    for row in db.execute(stmt).all():
        year, month = int(row.year), int(row.month)
        options.append(
            {
                "value": f"{year}-{month:02d}",
                "label": datetime(year, month, 1).strftime("%B %Y"),
            }
        )
    return options


@app.get("/")
def home():
    return RedirectResponse(url="/home")

@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/accounts")
def accounts(request: Request, db: Session = Depends(get_session)):
    stmt = select(Account).order_by(Account.account_type, Account.display_name)
    account_list = db.scalars(stmt).all()
    total_cents = sum(account.balance_cents for account in account_list)

    return templates.TemplateResponse(
        request,
        "accounts.html",
        context={"accounts": account_list, "total_cents": total_cents},
    )


@app.get("/transactions")
def transactions(
    request: Request,
    page: int = 1,
    year_month: str | None = None,
    db: Session = Depends(get_session),
):
    stmt = (
        select(
            Transaction.id,
            Transaction.created_at,
            Transaction.status,
            Transaction.description,
            Transaction.message,
            Transaction.amount_cents,
            Transaction.currency_code,
            Transaction.category_id,
            Account.display_name.label("account_name"),
        )
        .join(Account, Transaction.account_id == Account.id)
    )

    if year_month:
        start, end = month_range(year_month)
        stmt = stmt.where(
            Transaction.created_at >= start,
            Transaction.created_at < end,
        ).order_by(Transaction.created_at.asc())

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    total_pages = max(1, math.ceil(total / PAGE_SIZE))
    page = min(max(page, 1), total_pages)

    stmt = (
        stmt.order_by(Transaction.created_at.desc())
        .limit(PAGE_SIZE + 1)
        .offset((page - 1) * PAGE_SIZE)
    )

    rows = db.execute(stmt).all()
    return templates.TemplateResponse(
        request,
        "transactions.html",
        context={
            "transactions": rows[:PAGE_SIZE],
            "total_pages": total_pages,
            "page": page,
            "has_next": len(rows) > PAGE_SIZE,
            "month_options": get_month_options(db),
            "year_month": year_month or "",
        },
    )