import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

PRIMARY_ADMIN = int(os.getenv("PRIMARY_ADMIN"))

ADMINS = list(map(int, os.getenv("ADMINS").split(",")))

CHANNELS = os.getenv("CHANNELS").split(",") if os.getenv("CHANNELS") else []
