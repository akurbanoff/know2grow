from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')

SECRET = os.environ.get('SECRET')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

CRYPTO_PANIC_API = os.environ.get("CRYPTO_PANIC_API")
BINANCE_API = os.environ.get('BINANCE_API')
BINANCE_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY')

SENTRY_CDN = os.environ.get('SENTRY_CDN')

KNOW2GROW_SMTP_PASS = os.environ.get('KNOW2GROW_SMTP_PASS')
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = os.environ.get('SMTP_PORT')
SMTP_USER = os.environ.get('SMTP_USER')

TEST_DB_USER = os.environ.get('TEST_DB_USER')
TEST_DB_PASS = os.environ.get('TEST_DB_PASS')
TEST_DB_HOST = os.environ.get('TEST_DB_HOST')
TEST_DB_NAME = os.environ.get('TEST_DB_NAME')
TEST_DB_PORT = os.environ.get('TEST_DB_PORT')