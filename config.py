import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "22012880")
API_HASH = os.environ.get("API_HASH", "5b0e07f5a96d48b704eb9850d274fe1d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 

DB_NAME = os.environ.get("DB_NAME","Z900")     
DB_URL = os.environ.get("DB_URL","")

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6803505727').split()]
PORT = os.environ.get("PORT", "8080")

# Rename Info : If True Then Bot Rename File Else Not
RENAME_MODE = bool(environ.get('RENAME_MODE', True)) # Set True or False

ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', False))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002027394591"))

NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
SESSION_STRING = os.environ.get("SESSION_STRING", "")
REACTIONS = ["🤝", "😇", "🤗", "😍", "🎅", "🥰", "🤩", "😘", "😛", "😈", "🎉", "🫡", "😎", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions


#Force Sub
FORCE_SUB_CHANNEL1 = int(os.environ.get("FORCE_SUB_CHANNEL1", "-1002385466192"))#put 0 to disable
FORCE_SUB_CHANNEL2 = int(os.environ.get("FORCE_SUB_CHANNEL2", "0"))#put 0 to disable
FORCE_SUB_CHANNEL3 = int(os.environ.get("FORCE_SUB_CHANNEL3", "0"))#put 0 to disable
FORCE_SUB_CHANNEL4 = int(os.environ.get("FORCE_SUB_CHANNEL4", "0"))#put 0 to disable

FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "<b>ʜᴇʟʟᴏ ᴜꜱᴇʀ 👋🏻\nᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴄʟɪᴄᴋ ʀᴇʟᴏᴀᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴍʏ ꜰᴜɴᴄᴛɪᴏɴꜱ. 😊</b>")

AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1002385466192').split()] # give channel id with seperate space. Ex : ('-10073828 -102782829 -1007282828')

