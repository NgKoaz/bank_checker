from sqlalchemy import Integer, String
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Bank(Base):
    __tablename__ = "banks"
    bin: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]= mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    short_name: Mapped[str] = mapped_column(String(20), nullable=False)
    
