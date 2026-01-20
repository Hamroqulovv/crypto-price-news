from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from data import config
from utils.db_api.sqlite import Database


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database()
db = Database(path_to_db="main.db")