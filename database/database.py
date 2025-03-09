from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, func
from database.models import Bank
from typing import Callable, List, Any
from config import Config
from database.models import Base
from datetime import datetime


class Database:    
    __engine = create_async_engine("mysql+aiomysql://" + Config.DATABASE_URL, echo=False, connect_args={"charset": "utf8mb4"})
    SessionLocal = sessionmaker(bind=__engine, class_=AsyncSession, expire_on_commit=False)

    @staticmethod
    async def init_db():
        async with Database.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def has_banks() -> bool:
        async with Database.SessionLocal() as session:
            session: AsyncSession
            async with session.begin():  
                result = await session.execute(select(func.count()).select_from(Bank))
                count = result.scalar_one_or_none()  # Ensures it doesn't crash
                return (count or 0) > 0

    @staticmethod
    async def get_latest_transaction_date() -> datetime:
        async with Database.SessionLocal() as session:
            session: AsyncSession
            async with session.begin():  
                result = await session.execute(text("SELECT MAX(date) FROM transactions"))
                return result.scalar() or datetime.min

    @staticmethod
    async def delete_old_transactions(session: AsyncSession, date: datetime):
        query = text("""
            DELETE t1 FROM transactions t1
            LEFT JOIN (
                SELECT MAX(date) AS max_date FROM transactions
            ) t2 ON t1.date = t2.max_date
            WHERE t1.date < DATE_SUB(:date, INTERVAL 2 DAY)
            AND t2.max_date IS NULL;
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