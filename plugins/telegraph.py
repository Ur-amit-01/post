import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Function to upload media to envs.sh
def upload_image_requests(image_path):
    upload_url = "https://envs.sh"

    try:
        with open(image_path, 'rb') as file:
            files = {'file': file} 
            response = requests.post(upload_url, files=files)

            if response.status_code == 200:
                return response.text.strip() 
            else:
                print(f"Upload failed with status code {response.status_code}")
                return None

    except Exception as e:
        print(f"Error during upload: {e}")
        return None

# Command to handle /telegraph
@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_upload(bot: Client, message: Message):
    # Check if the command is used as a reply
    if not message.reply_to_message:
        await message.reply_text("❌ **Please reply to a media message with /telegraph.**")
        return

    # Check if the replied message contains media
    if not message.reply_to_message.media:
        await message.reply_text("❌ **The replied message does not contain any media.**")
        return

    # Download the media
    path = await message.reply_to_message.download()
    uploading_message = await message.reply_text("<b>⏳ Uploading...</b>")

    try:
        # Upload the media to envs.sh
        image_url = upload_image_requests(path)
        if not image_url:
            await uploading_message.edit_text("❌ **Failed to upload file.**")
            return
    except Exception as error:
        await uploading_message.edit_text(f"❌ **Upload failed: {error}**")
        return
    finally:
        # Clean up the downloaded file
        if os.path.exists(path):
            os.remove(path)

    # Send the uploaded link
    await uploading_message.edit_text(
        text=f"<b>🔗 **Link** :-\n{image_url}</b>",
        disable_web_page_preview=True
    )

