from apps.schemas.up_model import UpModel
from apps.schemas.common import Links, Money, ResourceRef
from datetime import datetime

class TransactionAttributes(UpModel):
    status: str
    raw_text: str | None = None
    description: str
    message: str | None = None
    amount: Money
    foreign_amount: Money | None = None
    settled_at: datetime | None = None
    created_at: datetime

class TransactionResourceRef(UpModel):
    data: ResourceRef | None = None

class TransactionRelationships(UpModel):
    account: TransactionResourceRef
    transfer_account: TransactionResourceRef 
    category: TransactionResourceRef 

class TransactionResource(UpModel):
    id: str
    attributes: TransactionAttributes
    relationships: TransactionRelationships

class TransactionsPage(UpModel):
    data: list[TransactionResource]
    links: Links
