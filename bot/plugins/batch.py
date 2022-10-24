# (c) @AbirHasan2005

import asyncio
import datetime
import re
import time
import mimetypes
import traceback
from bot.client import (
    Client
)
from pyrogram import filters
from pyrogram.file_id import FileId
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_id,
    get_media_file_size,
    get_media_file_name,
    get_file_type,
    get_file_attr
)
from configs import Config
from bot.core.display import progress_for_pyrogram
from bot.core.db.database import db
from bot.core.db.add import add_user_to_database
from bot.core.handlers.not_big import handle_not_big
from bot.core.handlers.time_gap import check_time_gap
from bot.core.handlers.big_rename import handle_big_rename
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden


class temp(object):
    CANCEL = False

lock = asyncio.Lock()

@Client.on_message(filters.command(["batch"]) & filters.private & ~filters.edited & filters.user(Config.PRO_USERS))
async def batch_rename_handler(c: Client, m: Message):
    if lock.locked():
        return await m.reply('Wait until previous process complete.', quote=True)

    # Proceed
    editable = await m.reply_text("`Processing...`", quote=True)

    try:
        txt = await c.send_message(Config.FROM_CHANNEL, ".")
        last_msg_id = txt.message_id
        await txt.delete()
    except ChatWriteForbidden:
        return await m.edit("Bot is not an admin in the given channel")
    except PeerIdInvalid:
        return await m.edit("Given channel ID is invalid")
    except Exception as e:
        return await m.edit(e)


    start_time = datetime.datetime.now()
    txt = await editable.edit(text="Batch Shortening Started!")
    success = 0
    fail = 0
    total = 0
    empty=0
    total_messages = (range(1,last_msg_id))
    temp.CANCEL = False
    files_config = await db.get_bot_stats()
    try:
        for i in range(files_config["last_file_id"], len(total_messages), 200):
            channel_posts = AsyncIter(await c.get_messages(Config.FROM_CHANNEL, total_messages[i:i+200]))

            async with lock:
                async for file_message in channel_posts:
                    if temp.CANCEL:
                        break
                    if file_message.video or file_message.document:
                        try:
                            files_config = await db.get_bot_stats()
                            if file_message.document.file_id not in files_config["file_done"]:
                                fwd_msg = await file_message.forward(Config.LOG_CHANNEL)
                                m = await fwd_msg.reply("Renaming this file now...")
                                await main_btach_rename_handler(c, m, editable)
                                success += 1
                                files_config["file_done"].append(fwd_msg.document.file_id)
                                await db.update_stats({"total_files_done":files_config["total_files_done"]+1, "last_file_id":fwd_msg.message_id, "file_done":files_config["file_done"]})
                                await m.delete()
                                await fwd_msg.delete()
                                                    # await update_stats(file_message, user_method)
                        except Exception as e:
                            print(e)
                            fail+=1
                        await asyncio.sleep(1)
                    else:
                        empty += 1
                    total+=1

                    if total % 10 == 0:
                        msg = f"Batch renaming in Process !\n\nTotal: {total}\nSuccess: {success}\nFailed: {fail}\nEmpty: {empty}\n\nTo cancel the batch: /cancel"
                        await txt.edit((msg))

    except Exception as e:
        await m.reply(f"Error Occured while processing batch: `{e.message}`")

    finally:
        end_time = datetime.datetime.now()
        await asyncio.sleep(10)
        t = end_time - start_time
        time_taken = str(datetime.timedelta(seconds=t.seconds))
        msg = f"Batch Shortening Completed!\n\nTime Taken - `{time_taken}`\n\nTotal: `{total}`\nSuccess: `{success}`\nFailed: `{fail}`\nEmpty: `{empty}`"
        await txt.edit(msg)

async def main_btach_rename_handler(c: Client, m: Message, editable):
    _raw_file_name = get_media_file_name(m.reply_to_message)
    if not _raw_file_name:
        _file_ext = mimetypes.guess_extension(get_file_attr(m.reply_to_message).mime_type)
        _raw_file_name = f"UnknownFileName{_file_ext}"

    user_input_msg = clean_filename(_raw_file_name)
    print(user_input_msg)
    if user_input_msg.rsplit(".", 1)[-1].lower() != _raw_file_name.rsplit(".", 1)[-1].lower():
        file_name = user_input_msg.rsplit(".", 1)[0][:255] + "." + _raw_file_name.rsplit(".", 1)[-1].lower()
    else:
        file_name = user_input_msg[:255]
    await editable.edit("Please Wait ...")
    is_big = get_media_file_size(m.reply_to_message) > (10 * 1024 * 1024)
    if not is_big:
        _default_thumb_ = await db.get_thumbnail(m.from_user.id)
        if not _default_thumb_:
            _m_attr = get_file_attr(m.reply_to_message)
            _default_thumb_ = _m_attr.thumbs[0].file_id \
                if (_m_attr and _m_attr.thumbs) \
                else None
        await handle_not_big(c, m, get_media_file_id(m.reply_to_message), file_name, editable, get_file_type(m.reply_to_message), _default_thumb_)
        return
    file_type = get_file_type(m.reply_to_message)
    _c_file_id = FileId.decode(get_media_file_id(m.reply_to_message))
    try:
        c_time = time.time()
        file_id = await c.custom_upload(
            file_id=_c_file_id,
            file_size=get_media_file_size(m.reply_to_message),
            file_name=file_name,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading ...\n"
                f"DC: {_c_file_id.dc_id}",
                editable,
                c_time
            )
        )

        if not file_id:
            return await editable.edit("Failed to Rename!\n\nMaybe your file corrupted :(")
        await handle_big_rename(c, m, file_id, file_name, editable, file_type)
    except Exception as err:
        await editable.edit("Failed to Rename File!\n\n"
                            f"**Error:** `{err}`\n\n"
                            f"**Traceback:** `{traceback.format_exc()}`")


class AsyncIter:    
    def __init__(self, items):    
        self.items = items    

    async def __aiter__(self):    
        for item in self.items:    
            yield item  

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration as e:
            raise StopAsyncIteration from e

def clean_filename(filename):
    filename=re.sub(f"_|\.|mkv|mp4", " ", filename)
    remove_username = re.sub("(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)", "", filename)
    filename = re.sub("  ", "", remove_username)
    return f"{filename} {Config.USERNAME} {Config.TAG}.mkv"

@Client.on_message(filters.private & filters.command('cancel') & filters.user(Config.PRO_USERS))
async def stop_button(c, m):
    if m.from_user.id in Config.PRO_USERS:
        temp.CANCEL = True
        msg = await c.send_message(text="<i>Trying To Stoping.....</i>", chat_id=m.chat.id)
        await asyncio.sleep(5)
        await msg.edit("Batch Shortening Stopped Successfully 👍")
