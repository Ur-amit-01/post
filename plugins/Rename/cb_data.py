

from plugins.Rename.utils import progress_for_pyrogram, convert, humanbytes
from pyrogram import Client, filters
from plugins.Rename.filedetect import refunc
from pyrogram.types import (  InlineKeyboardButton, InlineKeyboardMarkup,ForceReply)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import db
import os 
import humanize
from PIL import Image
import time
import logging
from config import LOG_CHANNEL
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot,update):
    try:
        await update.message.delete()
    except:
        return

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip()
        file = update.message.reply_to_message
        file_path = f"downloads/{new_filename}"
        ms = await update.message.edit("⚠️__**Please wait...**__\n\n__Downloading file to my server...__")
        c_time = time.time()

        try:
            path = await bot.download_media(
                message=file,
                progress=progress_for_pyrogram,
                progress_args=("**⚠️ Please wait, processing...**", ms, c_time)
            )
        except Exception as e:
            await ms.edit(e)
            return

        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)

        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except:
            pass

        user_id = update.message.chat.id
        user_name = update.message.chat.first_name
        ph_path = None
        media = getattr(file, file.media.value)
        filesize = humanize.naturalsize(media.file_size)
        c_caption = await db.get_caption(user_id)
        c_thumb = await db.get_thumbnail(user_id)

        if c_caption:
            try:
                caption = c_caption.format(filename=new_filename, filesize=filesize, duration=convert(duration))
            except Exception as e:
                await ms.edit(text=f"Your caption has an error: ({e})")
                return
        else:
            caption = f"**{new_filename}**"

        if media.thumbs or c_thumb:
            if c_thumb:
                ph_path = await bot.download_media(c_thumb)
            else:
                ph_path = await bot.download_media(media.thumbs[0].file_id)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")

        await ms.edit("⚠️__**Please wait...**__\n\n__Processing file upload...__")
        c_time = time.time()

        try:
            if type == "document":
                sent_msg = await bot.send_document(
                    user_id,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Uploading file...**__", ms, c_time)
                )
                await bot.send_document(
                    LOG_CHANNEL,
                    document=file_path,
                    caption=f"**Renamed by:** [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n**File:** `{new_filename}`"
                )

            elif type == "video":
                sent_msg = await bot.send_video(
                    user_id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Uploading file...**__", ms, c_time)
                )
                await bot.send_video(
                    LOG_CHANNEL,
                    video=file_path,
                    caption=f"**Renamed by:** [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n**File:** `{new_filename}`"
                )

            elif type == "audio":
                sent_msg = await bot.send_audio(
                    user_id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("⚠️__**Uploading file...**__", ms, c_time)
                )
                await bot.send_audio(
                    LOG_CHANNEL,
                    audio=file_path,
                    caption=f"**Renamed by:** [{user_name}](tg://user?id={user_id}) (`{user_id}`)\n**File:** `{new_filename}`"
                )

        except Exception as e:
            await ms.edit(f"Error: {e}")
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            return

        await ms.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

    except Exception as e:
        logger.error(f"Error: {e}")

	    
