from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    DATABASE_URL=os.getenv("DATABASE_URL")

    BANK_USERNAME=os.getenv("BANK_USERNAME")
    BANK_PASSWORD=os.getenv("BANK_PASSWORD")
    BANK_ACCOUNT_NUMBER=os.getenv("BANK_ACCOUNT_NUMBER")
    BANK_BIN=int(os.getenv("BANK_BIN"))


    FETCH_TRANSACTIONS_INTERVAL = 15
    BANK_INFO_URL="https://api.vietqr.io/v2/banks"
