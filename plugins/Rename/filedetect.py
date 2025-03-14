from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def refunc(client, message, new_name, msg):
    try:
        file = getattr(msg, msg.media.value, None)
        if not file:
            await message.reply_text("**Error**: Unable to fetch file details.")
            return

        # Extract filename if available, otherwise use a fallback
        filename = file.file_name if file.file_name else None
        mime_type = file.mime_type if file.mime_type else "unknown/unknown"
        mime = mime_type.split("/")[0]  # Extract main type (video, audio, etc.)

        # Set default filename if missing
        if not filename:
            default_extension = "mp4" if mime == "video" else "mp3" if mime == "audio" else "bin"
            filename = f"{file.unique_id}.{default_extension}"  # Use unique_id + default extension

        # Clean new name
        new_name = new_name.replace(".mp4", "").replace(".mkv", "").replace(".", "")
        
        # Extract file extension and create new filename
        out_name = filename.split(".")[-1]  # Extract the extension
        out_filename = f"{new_name}.{out_name}"

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

