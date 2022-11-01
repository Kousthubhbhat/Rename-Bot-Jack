# (c) @AbirHasan2005

from typing import Union
from pyromod import listen
from pyrogram import Client as RawClient
from pyrogram.storage import Storage
from configs import Config
from bot.core.new import New
from bot.core.db.database import db
LOGGER = Config.LOGGER
log = LOGGER.getLogger(__name__)

if Config.REPLIT:
    from threading import Thread

    from flask import Flask, jsonify
    
    app = Flask('')
    
    @app.route('/')
    def main():
        res = {
            "status":"running",
            "hosted":"replit.com",
        }
        
        return jsonify(res)

    def run():
      app.run(host="0.0.0.0", port=8000)
    
    async def keep_alive():
      server = Thread(target=run)
      server.start()

async def create_app(session, API_ID, API_HASH, BOT_TOKEN,) -> "Client":
    return Client(session, API_ID, API_HASH, bot_token=BOT_TOKEN)

class Client(RawClient, New):
    """ Custom Bot Class """

    # client1: "Client" = None

    def __init__(self, session_name: Union[str, Storage] = "RenameBot"):
        super().__init__(
            session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(
                root="bot/plugins"
            )
        )

    async def start(self):
        if Config.REPLIT:
            await keep_alive()

        await super().start()
        config = await db.get_bot_stats()
        if not config:
            config = await db.create_stats()

        if "on_progress" not in config.keys():
            await db.update_stats({"on_progress":[]})

        # self.client1 = (await create_app("account_1", Config.API_ID, Config.API_HASH,Config.BOT_TOKEN_1)).start()

        log.info("Bot Started!")

    async def stop(self, *args):
        await super().stop()
        log.info("Bot Stopped!")
