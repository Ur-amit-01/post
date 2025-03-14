# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

async def refunc(client, message, new_name, msg):
    try:
        file = getattr(msg, msg.media.value, None)
        if not file:
            return await message.reply_text("Error: Unable to detect file in the message.")

        # Get the filename if available, otherwise assign default name
        filename = file.file_name if file.file_name else None

        # Handle missing filename case
        if not filename:
            extn = "bin"
            if file.mime_type:
                mime_category = file.mime_type.split("/")[0]
                if mime_category == "video":
                    extn = "mp4"
                elif mime_category == "audio":
                    extn = "mp3"
                elif mime_category == "image":
                    extn = "jpg"

            # Assign a default name with a timestamp
            filename = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extn}"

        else:
            extn = filename.rsplit(".", 1)[-1] if "." in filename else "mkv"
        
        # Ensure new_name does not contain an extra dot or extension
        if "." in new_name:
            new_name = new_name.rsplit(".", 1)[0]

        out_filename = f"{new_name}.{extn}"

        # Define button layout based on file type
        mime_type = file.mime_type.split("/")[0] if file.mime_type else "unknown"
        if mime_type == "video":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Document", callback_data="upload_document"),
                 InlineKeyboardButton("🎥 Video", callback="upload_video")]
            ])
        elif mime_type == "audio":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📁 Document", callback_data="upload_document"),
                 InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")]
            ])
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("📁 Document", callback_data="upload_document")]])

        # Send the response
        await message.reply_text(
            text=f"**Select the output format:**\n**📄 File Name → {out_filename}**",
            reply_to_message_id=message.id,
            reply_markup=markup
        )

    except Exception as e:
        await message.reply_text(f"**Error:** {str(e)}")

