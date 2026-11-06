from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from apps.models.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    raw_text: Mapped[str | None]
    description: Mapped[str]
    message: Mapped[str | None]
    currency_code: Mapped[str]
    amount_cents: Mapped[int] = mapped_column(BigInteger)
    foreign_currency_code: Mapped[str | None]
    foreign_amount_cents: Mapped[int | None] = mapped_column(BigInteger)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    transfer_account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), index=True)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )