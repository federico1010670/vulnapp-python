from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="member")
    is_active: Mapped[bool] = mapped_column(default=True)
    reset_password_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reset_password_exp: Mapped[datetime | None] = mapped_column(nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    region: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="open")
    amount_cents: Mapped[int] = mapped_column(default=0)
    pdf_path: Mapped[str] = mapped_column(String(255), default="")


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    role: str
    password_hash: str


class UserPublic(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    role: str
