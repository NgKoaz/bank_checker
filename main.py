import asyncio
from datetime import datetime, timedelta
from captcha_solver import MbBankSolver
from mbbank import MBBankAsync, MBBankError
from database.database import Database
from database.models import Bank, Transaction
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from config import Config
import logging
import aiohttp


logging.basicConfig(
    level=logging.DEBUG,  # Ghi log từ DEBUG trở lên
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("bank_checking")

async def fetch_banks_info():
    if await Database.has_banks():
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(Config.BANK_INFO_URL) as response:
            logger.info("Fetching bank info")
            result = await response.json()
            banks = result['data']
            async def save_banks(session: AsyncSession):
                for bank in banks:
                    session.add(Bank(bin=bank['bin'], name=bank['name'], code=bank['code'], short_name=bank['short_name']))
            await Database.exec_transaction([save_banks])


async def fetch_transactions():
    solver = MbBankSolver()
    mb = MBBankAsync(username=Config.BANK_USERNAME, password=Config.BANK_PASSWORD, ocr_class=solver)
    lastest_payment_date = datetime.min
    while True:
        end_query_day = datetime.now()
        start_query_day = end_query_day - timedelta(days=1)
        try:
            logger.info("Fetching transactions")
            results = await mb.getTransactionAccountHistory(from_date=start_query_day, to_date=end_query_day)
            transactions = results['transactionHistoryList']
            lastest_payment_date = await Database.get_latest_transaction_date()
            async def save_transactions(session: AsyncSession):
                query = text("SELECT * FROM transactions WHERE date = :date")
                result = await session.execute(query, {"date": lastest_payment_date.strftime("%Y-%m-%d %H:%M:%S")})
                old_trans = [Transaction(**old_tran) for old_tran in result.mappings().all()]

                for transaction in transactions:
                    amount = int(transaction['creditAmount'])
                    ref_no = transaction['refNo']
                    transaction_date = datetime.strptime(transaction['transactionDate'], "%d/%m/%Y %H:%M:%S")
                    description = transaction['description'].replace(" ", "")

                    if (lastest_payment_date < transaction_date or 
                        (lastest_payment_date == transaction_date and not any(ref_no == t.ref_no for t in old_trans))):
                        session.add(Transaction(
                            bank_bin=Config.BANK_BIN,
                            amount=amount,
                            ref_no=ref_no,
                            date=transaction_date,
                            description=description
                        ))

            await Database.exec_transaction([lambda session: save_transactions(session)])
            await asyncio.sleep(Config.FETCH_TRANSACTIONS_INTERVAL)
        except MBBankError:
            mb = MBBankAsync(username=Config.BANK_USERNAME, password=Config.BANK_PASSWORD, ocr_class=solver)
            logger.info("Reconnecting to the bank server")
            await asyncio.sleep(3)


async def schedule_cleanup():
    while True:
        await Database.exec_transaction([lambda session: Database.delete_old_transactions(session, datetime.now())])
        logger.info("Cleaned up old transactions")
        await asyncio.sleep(24 * 3600)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Database.init_db())
    loop.run_until_complete(Database.has_banks())
    loop.create_task(schedule_cleanup())
    loop.create_task(fetch_transactions())
    loop.run_forever()



