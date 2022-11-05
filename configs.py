# (c) @AbirHasan2005

import os
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

from dotenv import load_dotenv
load_dotenv()
class Config(object):
    API_ID = int(os.environ.get("API_ID", "8813038"))
    API_HASH = os.environ.get("API_HASH", "780fd96b159baa710dada78ff1621b54")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "5773205742:AAFSygtZMc_9ow_miS4sWmn5Rw0vQZMdoOc")
    # BOT_TOKEN_1 = os.environ.get("BOT_TOKEN_1", "")
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    LOGGER = logging
    OWNER_ID = int(os.environ.get("OWNER_ID", 2083503061))
    PRO_USERS = list({int(x) for x in os.environ.get("PRO_USERS", "0").split()})
    PRO_USERS.append(OWNER_ID)
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb+srv://abcd:abcd@cluster0.od5wfzt.mongodb.net/?retryWrites=true&w=majority")
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001884096843"))
    BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", "False"))
    FROM_CHANNEL = int(os.environ.get("FROM_CHANNEL", "-1001880691367"))
    TO_CHANNEL = int(os.environ.get("TO_CHANNEL", "-1001785157194"))
    USERNAME = os.environ.get("USERNAME", "@FilmyFunda_Movies")
    TAG = os.environ.get("TAG", "_Rᴏʟᴇx_")
    LIMIT_IN_MB = int(os.environ.get("LIMIT_IN_MB", "100"))
    #  Replit Config for Hosting in Replit
    REPLIT_USERNAME = os.environ.get("REPLIT_USERNAME", None) # your replit username 
    REPLIT_APP_NAME = os.environ.get("REPLIT_APP_NAME", None) # your replit app name 
    REPLIT = f"https://{REPLIT_APP_NAME.lower()}.{REPLIT_USERNAME}.repl.co" if REPLIT_APP_NAME and REPLIT_USERNAME else False
    PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "150"))
