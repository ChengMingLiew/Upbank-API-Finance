from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.models.base import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    account_type: Mapped[str]
    ownership_type: Mapped[str]
    balance_cents: Mapped[int] = mapped_column(BigInteger)
    currency_code: Mapped[str]
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )