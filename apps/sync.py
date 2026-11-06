from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from apps.up_client import UpClient
from apps.models import Account
from apps.schemas import AccountResource
from apps.db import session_scope


def build_rows(account_list: list[AccountResource]) -> list[dict]:

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

    if accounts is []:
        return 0

    rows = build_rows(accounts)
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