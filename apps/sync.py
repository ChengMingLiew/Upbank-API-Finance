from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from apps.up_client import UpClient
from apps.db import session_scope
from apps.models.account import Account
from apps.schemas.accounts import AccountResource
from apps.models.category import Category
from apps.schemas.categories import CategoryResource
from apps.schemas.transactions import TransactionResource
from apps.models.transaction import Transaction


def build_account_rows(account_list: list[AccountResource]) -> list[dict]:

    rows = []

    for account in account_list:

        row = {}
        row["id"] = account.id
        row["display_name"] = account.attributes.display_name
        row["account_type"] = account.attributes.account_type
        row["ownership_type"] = account.attributes.ownership_type
        row["balance_cents"] = account.attributes.balance.value_in_base_units
        row["currency_code"] = account.attributes.balance.currency_code
        row["opened_at"] = account.attributes.created_at

        rows.append(row)

    return rows

def sync_accounts() -> int:

    up_client = UpClient()

    try:
        accounts = up_client.list_accounts()
    finally:
        up_client.close()

    if not accounts:
        return 0

    rows = build_account_rows(accounts)
    stmt = insert(Account).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Account.id],
        set_={
            "display_name": stmt.excluded.display_name,
            "account_type": stmt.excluded.account_type,
            "ownership_type": stmt.excluded.ownership_type,
            "balance_cents": stmt.excluded.balance_cents,
            "currency_code": stmt.excluded.currency_code,
            "updated_at": func.now(),
        },
    )

    with session_scope() as session:
        session.execute(stmt)

    return len(rows)


def build_category_rows(category_list: list[CategoryResource]) -> list[dict]:

    rows = []

    for category in category_list:  

        row = {}
        row["id"] = category.id
        row["name"] = category.attributes.name

        if category.relationships.parent.data is None:
            row["parent_id"] = None
        else:
            row["parent_id"] = category.relationships.parent.data.id

        rows.append(row)

    return rows


def sync_categories() -> int:

    up_client = UpClient()

    try:
        categories = up_client.list_categories()
    finally:
        up_client.close()

    if not categories:
        return 0

    rows = build_category_rows(categories)
    stmt = insert(Category).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Category.id],
        set_={
            "name": stmt.excluded.name,
            "parent_id": stmt.excluded.parent_id
        },
    )
    with session_scope() as session:
        session.execute(stmt)

    return len(rows)

def build_transaction_rows(transaction_list: list[TransactionResource]) -> list[dict]:

    rows = []

    for transaction in transaction_list:

        row = {}
        row["id"] = transaction.id
        row["status"] = transaction.attributes.status

        if transaction.attributes.raw_text is None:
            row["raw_text"] = None
        else:
            row["raw_text"] = transaction.attributes.raw_text

        row["description"] = transaction.attributes.description
        row["message"] = transaction.attributes.message
        row["currency_code"] = transaction.attributes.amount.currency_code
        row["amount_cents"] = transaction.attributes.amount.value_in_base_units

        if transaction.attributes.foreign_amount is None:
            row["foreign_currency_code"] = None
            row["foreign_amount_cents"] = None
        else:
            row["foreign_currency_code"] = transaction.attributes.foreign_amount.currency_code
            row["foreign_amount_cents"] = transaction.attributes.foreign_amount.value_in_base_units

        if transaction.attributes.settled_at is None:
            row["settled_at"] = None
        else:
            row["settled_at"] = transaction.attributes.settled_at

        row["created_at"] = transaction.attributes.created_at
        row["account_id"] = transaction.relationships.account.data.id

        if transaction.relationships.transfer_account.data is None:
            row["transfer_account_id"] = None
        else:
            row["transfer_account_id"] = transaction.relationships.transfer_account.data.id

        if transaction.relationships.category.data is None:
            row["category_id"] = None
        else:
            row["category_id"] = transaction.relationships.category.data.id

        rows.append(row)

    return rows

def sync_transactions() -> int:

    up_client = UpClient()

    try:
        transactions = up_client.list_transactions()
    finally:
        up_client.close()

    if not transactions:
        return 0

    rows = build_transaction_rows(transactions)
    stmt = insert(Transaction).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Transaction.id],
        set_={
            "status": stmt.excluded.status,
            "raw_text": stmt.excluded.raw_text,
            "description": stmt.excluded.description,
            "message": stmt.excluded.message,
            "currency_code": stmt.excluded.currency_code,
            "amount_cents": stmt.excluded.amount_cents,
            "foreign_currency_code": stmt.excluded.foreign_currency_code,
            "foreign_amount_cents": stmt.excluded.foreign_amount_cents,
            "settled_at": stmt.excluded.settled_at,
            "category_id": stmt.excluded.category_id,
            "transfer_account_id": stmt.excluded.transfer_account_id,
            "synced_at": func.now(),
        },
    )

    with session_scope() as session:
        session.execute(stmt)

    return len(rows)