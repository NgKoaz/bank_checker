import asyncio
from datetime import datetime, timedelta
from captcha_solver import MbBankSolver
from mbbank import MBBankAsync, MBBankError
from database.database import Database
from database.models import Bank, Transaction
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from config import Config
import aiohttp



async def fetch_banks_info():
    if await Database.has_banks():
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(Config.BANK_INFO_URL) as response:
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
            print(f"username={Config.BANK_USERNAME}, password={Config.BANK_PASSWORD}")
            print("Reconnecting to the bank server")
            await asyncio.sleep(3)


async def main():
    await Database.init_db()
    await fetch_banks_info()
    await fetch_transactions()


asyncio.run(main())


