from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import Callable, List, Any
from config import Config
from database.models import Base
from datetime import datetime


class Database:    
    __engine = create_async_engine("mysql+aiomysql://" + Config.DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=__engine, class_=AsyncSession, expire_on_commit=False)

    @staticmethod
    async def init_db():
        async with Database.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def has_banks() -> bool:
        async with Database.SessionLocal() as session:
            session: AsyncSession
            result = await session.execute(text("SELECT COUNT(*) FROM banks"))
            return result.scalar() > 0

    @staticmethod
    async def get_latest_transaction_date() -> datetime:
        async with Database.SessionLocal() as session:
            session: AsyncSession
            result = await session.execute(text("SELECT MAX(date) FROM transactions"))
            return result.scalar() or datetime.min

    @staticmethod
    async def delete_old_transactions(session: AsyncSession, date: datetime):
        query = text("""
            DELETE FROM transactions 
            WHERE date < DATE_SUB(:date, INTERVAL 2 DAY)
            AND date NOT IN (
                SELECT MAX(date) FROM transactions
            )
        """)
        return await session.execute(query, {"date": date.strftime("%Y-%m-%d %H:%M:%S")})

    @staticmethod
    async def exec_transaction(operations: List[Callable[[AsyncSession], Any]]) -> List[Any]:
        async with Database.SessionLocal() as session:
            session: AsyncSession
            async with session.begin():  
                results = []
                for operation in operations:
                    results.append(await operation(session=session))  
                return results