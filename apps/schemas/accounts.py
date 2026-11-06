from apps.schemas.up_model import UpModel
from apps.schemas.common import Money, Links
from datetime import datetime

class AccountAttributes(UpModel):
    display_name: str
    account_type: str
    ownership_type: str
    balance: Money
    created_at: datetime

class AccountResource(UpModel):
    id: str
    attributes: AccountAttributes

class AccountsPage(UpModel):
    data: list[AccountResource]
    links: Links