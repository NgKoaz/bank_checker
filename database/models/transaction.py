from sqlalchemy import Integer, String, ForeignKey, DateTime
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bank_bin: Mapped[int] = mapped_column(Integer, ForeignKey("banks.bin"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    ref_no: Mapped[str] = mapped_column(String(30), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

