import os
from dotenv import load_dotenv

load_dotenv()  # 自動載入 .env 內容

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "line_bot_expense")
print(f"LINE_CHANNEL_ACCESS_TOKEN in config: {repr(LINE_CHANNEL_ACCESS_TOKEN)}")
print(f"LINE_CHANNEL_SECRET in config: {repr(LINE_CHANNEL_ACCESS_TOKEN)}")
print(f"MONGO_URI in config: {repr(LINE_CHANNEL_ACCESS_TOKEN)}")
print(f"DB_NAME in config: {repr(LINE_CHANNEL_ACCESS_TOKEN)}")
