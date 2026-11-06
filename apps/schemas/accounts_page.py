from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from datetime import datetime

class UpModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class Money(UpModel):
    currency_code: str
    value_in_base_units: int

class AccountAttributes(UpModel):
    display_name: str
    account_type: str
    ownership_type: str
    balance: Money
    created_at: datetime

class AccountResource(UpModel):
    id: str
    attributes: AccountAttributes

class Links(UpModel):
    prev: str | None = None
    next: str | None = None

class AccountsPage(UpModel):
    data: list[AccountResource]
    links: Links