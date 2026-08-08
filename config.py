import os
import sys
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID_RAW = os.getenv("GROUP_CHAT_ID_RAW")
PORT = int(os.getenv("PORT", 10000))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан")
if not GROUP_CHAT_ID_RAW:
    raise ValueError("GROUP_CHAT_ID_RAW не задан")

GROUP_CHAT_ID = int(GROUP_CHAT_ID_RAW)

# Можно вывести для отладки (потом убрать)
print(f"BOT_TOKEN = {BOT_TOKEN[:10]}...", file=sys.stderr)
print(f"GROUP_CHAT_ID = {GROUP_CHAT_ID}", file=sys.stderr)
