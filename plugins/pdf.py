import requests
import os
import re
import logging
import tempfile
import asyncio
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
from config import LOG_CHANNEL
from helper.database import db
from plugins.Fsub import auth_check


logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 350 * 1024 * 1024  # 350MB

user_file_metadata = {}  # Store metadata for each user's files
user_states = {}  # Track user states
pending_filename_requests = {}  # Track pending filename requests

async def reset_user_state(user_id: int):
    await asyncio.sleep(300)  # 5 minutes
    if user_id in user_file_metadata:
        user_file_metadata.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)
        user_states.pop(user_id, None)
        logger.info(f"Reset state for user {user_id} due to inactivity.")

async def show_progress_bar(progress_message, current, total, bar_length=10):
    progress = min(current / total, 1.0)  # Ensure progress doesn't exceed 1.0
    filled_length = int(bar_length * progress)
    bar = "●" * filled_length + "○" * (bar_length - filled_length)  # Filled and empty parts
    percentage = int(progress * 100)
    text = f"**🛠️ Processing...**\n`[{bar}]` {percentage}% ({current}/{total})"
    await progress_message.edit_text(text)

async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_metadata[user_id] = []  # Reset file list for the user
    user_states[user_id] = "collecting_files"  # Set user state
    await message.reply_text(
        "**📤 ɴᴏᴡ ꜱᴇɴᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇǫᴜᴇɴᴄᴇ !! 🧾**"
    )
    # Start a timer to reset the state after 2 minutes
    asyncio.create_task(reset_user_state(user_id))

async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only accept PDFs if the user has started the merge process
    if user_id not in user_states or user_states[user_id] != "collecting_files":
        return

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if len(user_file_metadata[user_id]) >= 20:
        await message.reply_text("⚠️ You can merge only 20 files at once. Type /done ✅ to merge them.")
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File size is too large! Please send a file under 350MB.")
        return

    user_file_metadata[user_id].append(
        {
            "type": "pdf",
            "file_id": message.document.file_id,
            "file_name": message.document.file_name,
        }
    )
    await message.reply_text(
        f"•**ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: {len(user_file_metadata[user_id])} 📄**\n"
        "•**/done: ᴛᴏ ᴍᴇʀɢᴇ ᴀʟʟ ꜰɪʟᴇꜱ ✅**"
    )

async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only accept images if the user has started the merge process
    if user_id not in user_states or user_states[user_id] != "collecting_files":
        return

    user_file_metadata[user_id].append(
        {
            "type": "image",
            "file_id": message.photo.file_id,
            "file_name": f"photo_{len(user_file_metadata[user_id]) + 1}.jpg",
        }
    )
    await message.reply_text(
        f"•**ᴛᴏᴛᴀʟ ɪᴍᴀɢᴇꜱ: {len(user_file_metadata[user_id])} 🖼️\n"
        "•**/done: ᴛᴏ ᴍᴇʀɢᴇ ᴀʟʟ ɪᴍᴀɢᴇꜱ ✅**"
    )

async def merge_files(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_metadata or not user_file_metadata[user_id]:
        await message.reply_text("**⚠️ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ғɪʟᴇs ʏᴇᴛ. Usᴇ /merge ᴛᴏ sᴛᴀʀᴛ.**")
        return

    await message.reply_text("**✍️ Type a name for your merged PDF 📄.**")
    user_states[user_id] = "waiting_for_filename"  # Set user state

async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    # Only process if the user is in the "waiting_for_filename" state
    if user_id not in user_states or user_states[user_id] != "waiting_for_filename":
        return

    custom_filename = message.text.strip()

    if not custom_filename:
        await message.reply_text("❌ Filename cannot be empty. Please try again.")
        return

    # Check if the filename contains a thumbnail link
    match = re.match(r"(.*)\s*-t\s*(https?://\S+)", custom_filename)
    if match:
        filename_without_thumbnail = match.group(1).strip()
        thumbnail_link = match.group(2).strip()

        # Validate the thumbnail link
        try:
            response = requests.get(thumbnail_link, timeout=10)
            if response.status_code != 200:
                await message.reply_text("❌ Failed to fetch the image. Please provide a valid thumbnail link.")
                return

            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_thumbnail:
                temp_thumbnail.write(response.content)
                thumbnail_path = temp_thumbnail.name

            # Process the thumbnail (resize and convert to JPEG)
            Image.open(thumbnail_path).convert("RGB").save(thumbnail_path)
            img = Image.open(thumbnail_path)
            img.resize((320, 320))
            img.save(thumbnail_path, "JPEG")

        except Exception as e:
            await message.reply_text(f"❌ Error while downloading or processing the thumbnail: {e}")
            return

    else:
        filename_without_thumbnail = custom_filename
        thumbnail_path = None  # No thumbnail provided

        # Fetch thumbnail from the database if available
        c_thumb = await db.get_thumbnail(user_id)  # Assuming db.get_thumbnail is defined
        if c_thumb:
            try:
                # Download the thumbnail from the database
                thumbnail_path = await client.download_media(c_thumb)
                # Process the thumbnail (resize and convert to JPEG)
                Image.open(thumbnail_path).convert("RGB").save(thumbnail_path)
                img = Image.open(thumbnail_path)
                img.resize((320, 320))
                img.save(thumbnail_path, "JPEG")
            except Exception as e:
                logger.error(f"Error processing thumbnail from database: {e}")
                thumbnail_path = None  # Fallback to no thumbnail

    # Proceed to merge the files
    progress_message = await message.reply_text("**🛠️ Merging your files... Please wait... ⏰**")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, f"{filename_without_thumbnail}.pdf")
            merger = PdfMerger()

            total_files = len(user_file_metadata[user_id])
            for index, file_data in enumerate(user_file_metadata[user_id], start=1):
                if file_data["type"] == "pdf":
                    file_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    merger.append(file_path)
                    await show_progress_bar(progress_message, index, total_files)  # Update progress bar
                elif file_data["type"] == "image":
                    img_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    image = Image.open(img_path).convert("RGB")
                    img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                    image.save(img_pdf_path, "PDF")
                    merger.append(img_pdf_path)
                    await show_progress_bar(progress_message, index, total_files)  # Update progress bar

            merger.write(output_file)
            merger.close()

            # Send the merged file with or without the thumbnail
            await asyncio.gather(
                client.send_document(
                    chat_id=message.chat.id,
                    document=output_file,
                    thumb=thumbnail_path if thumbnail_path else None,  # Set thumbnail if available
                    caption="**🎉 Here is your merged PDF 📄.**",
                ),
                client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    thumb=thumbnail_path if thumbnail_path else None,  # Set thumbnail if available
                    caption=(
                        f">**📑 Merged PDF**\n"
                        f">**☃️ By :- [{message.from_user.first_name}](tg://user?id={message.from_user.id})**\n"
                        f">**🪪 ID :- `{message.from_user.id}`**"
                    ),
                ),
            )

            # Send a sticker after sending the merged PDF and delete progress message
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"
            )
            await progress_message.delete()

    except Exception as e:
        await progress_message.edit_text(f"❌ Failed to merge files: {e}")

    finally:
        # Reset the user's state
        user_file_metadata.pop(user_id, None)
        user_states.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)

        # Clean up temporary files
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

# Register handlers
@Client.on_message(filters.command(["merge"]))
@auth_check
async def start_file_collection_handler(client: Client, message: Message):
    await start_file_collection(client, message)

@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "collecting_files":
        await handle_pdf_metadata(client, message)

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "collecting_files":
        await handle_image_metadata(client, message)

@Client.on_message(filters.command(["done"]))
@auth_check
async def merge_files_handler(client: Client, message: Message):
    await merge_files(client, message)

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "settings", "set_thumb", "del_thumb", "view_thumb", "see_caption", "del_caption", "set_caption", "rename", "cancel", "ask", "id", "set", "telegraph", "stickerid", "accept", "users", "broadcast", "rename"]) & ~filters.regex("https://t.me/"))           
async def handle_filename_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "waiting_for_filename":
        await handle_filename(client, message)

