from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from apps.db import get_session
from sqlalchemy import select, func
from apps.models.account import Account

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