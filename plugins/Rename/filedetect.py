from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

async def refunc(client, message, new_name, msg):
    try:
        file = getattr(msg, msg.media.value, None)
        if not file:
            await message.reply_text("**Error**: Unable to fetch file details.")
            return

        filename = file.file_name
        if not filename:
            await message.reply_text("**Error**: No filename detected in the file metadata.")
            return

        types = file.mime_type.split("/") if file.mime_type else ["unknown"]
        mime = types[0]

        # Clean new name to avoid issues
        new_name = new_name.replace(".mp4", "").replace(".mkv", "").replace(".", "")

        try:
            out_name = filename.split(".")[-1]  # Extract file extension
            out_filename = f"{new_name}.{out_name}"
        except:
            await message.reply_text("**Error**: No extension in file, not supported.")
            return

        # Define markup based on mime type
        if mime == "video":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Document", callback_data="upload_document"),
                 InlineKeyboardButton("🎥 Video", callback_data="upload_video")]
            ])
        elif mime == "audio":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Document", callback_data="upload_document"),
                 InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")]
            ])
        else:
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Document", callback_data="upload_document")]
            ])

        await message.reply_text(f"**Select the output file type**\n**🎞New Name:** `{out_filename}`",
                                 reply_to_message_id=msg.id, reply_markup=markup)

    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text(f"**Unexpected Error**: {e}")
