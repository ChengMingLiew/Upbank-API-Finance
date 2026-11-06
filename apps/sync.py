from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from apps.up_client import UpClient
from apps.db import session_scope
from apps.models.account import Account
from apps.schemas.accounts import AccountResource
from apps.models.category import Category
from apps.schemas.categories import CategoryResource


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