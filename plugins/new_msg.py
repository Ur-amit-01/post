from pyrogram import Client, filters
from pyrogram.types import Message
from helper.database import db

# Command to add the channel (Only works if sent in a channel)
@Client.on_message(filters.command("add") & filters.channel)
async def add_channel(client, message: Message):
    channel_id = message.chat.id
    added = await db.add_channel(channel_id)  # Using the new database function

    if added:
        await message.reply("✅ Channel added! Now, all messages will be formatted.")
    else:
        await message.reply("ℹ️ This channel is already added.")

# Command to remove the channel (Only works if sent in a channel)
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_channel(client, message: Message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if the channel exists
        await db.remove_channel(channel_id)
        await message.reply("❌ Channel removed! Messages will no longer be formatted.")
    else:
        await message.reply("ℹ️ This channel is not in the list.")

# Command: /add_caption
@Client.on_message(filters.command("add_caption") & filters.channel)
async def set_caption(client, message: Message):
    channel_id = message.chat.id
    caption = message.text.replace("/add_caption", "").strip()

    if not caption:
        await message.reply_text("Please provide a caption.")
        return

    # Save the caption in the database
    await db.save_formatting(channel_id, caption)
    await message.reply_text("**Caption formatting has been set for this channel.\nSend /remove to stop this formatting.**")

# Command: /remove
@Client.on_message(filters.command("remove") & filters.channel)
async def rem_caption(client, message: Message):
    channel_id = message.chat.id

    # Remove the caption from the database
    await db.formatting.delete_one({"_id": channel_id})
    await message.reply_text("**Caption formatting has been removed for this channel.**")

# Handle incoming media messages
@Client.on_message(filters.media & filters.channel)
async def handle_media(client, message: Message):
    channel_id = message.chat.id

    # Retrieve the caption from the database
    formatting_text = await db.get_formatting(channel_id)

    if formatting_text:
        # Apply the formatting to the media message
        message.caption = formatting_text
        await message.edit_caption(formatting_text)

# Handle text messages in channels (excluding commands)
@Client.on_message(filters.channel)
async def format_message(client, message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if channel is in the database
        if message.text and not message.text.startswith("/"):  # Ignore commands
            formatted_text = f"```\n{message.text}\n```"
            await message.edit_text(formatted_text)  # Edit message with formatting
