from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from apps.db import get_session
from sqlalchemy import select
from apps.models.account import Account
from apps.models.transaction import Transaction

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "base.html")

def money(amount_in_cents: int) -> str:

    amount_in_dollars = abs(amount_in_cents) / 100

    if amount_in_cents < 0:
        value_in_str = f"-${amount_in_dollars:,.2f}"
    else:
        value_in_str = f"${amount_in_dollars:,.2f}"

    return value_in_str

templates.env.filters["money"] = money

@app.get("/accounts")
def accounts(request: Request, db: Session = Depends(get_session)):

    account_list_stmt = select(Account).order_by(Account.account_type, Account.display_name)
    account_list = db.scalars(account_list_stmt).all()
    total_cents = sum(account.balance_cents for account in account_list)

    return templates.TemplateResponse(request, "accounts.html", context={"accounts": account_list, "total_cents": total_cents})

PAGE_SIZE = 10


@app.get("/transactions")
def transactions(request: Request, page: int = 1, db: Session = Depends(get_session)):
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
        .order_by(Transaction.created_at.desc())
        .limit(PAGE_SIZE + 1)
        .offset((page - 1) * PAGE_SIZE)
    )

    rows = db.execute(stmt).all()

    has_next = len(rows) > PAGE_SIZE
    transaction_list = rows[:PAGE_SIZE]

    return templates.TemplateResponse(
        request,
        "transactions.html",
        context={
            "transactions": transaction_list,
            "page": page,
            "has_next": has_next,
        },
    )