from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from apps.models.base import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"))