from sqlalchemy import Integer, String, ForeignKey
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_engine": "InnoDB"}


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bin: Mapped[int] = mapped_column(Integer, ForeignKey("banks.bin"), nullable=False)

