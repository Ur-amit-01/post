from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Database helper
import time

# Command to add the current channel to the database
@Client.on_message(filters.command("add") & filters.channel)
async def add_current_channel(client, message: Message):
    channel_id = message.chat.id
    channel_name = message.chat.title

    try:
        added = await db.add_channel(channel_id, channel_name)
        if added:
            await message.reply(f"✅ Channel '{channel_name}' added!")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' already exists.")
    except Exception as e:
        print(f"Error adding channel: {e}")
        await message.reply("❌ Failed to add channel. Contact developer.")

# Command to remove the current channel from the database
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_current_channel(client, message: Message):
    channel_id = message.chat.id
    channel_name = message.chat.title

    try:
        if await db.is_channel_exist(channel_id):
            await db.delete_channel(channel_id)
            await message.reply(f"✅ Channel '{channel_name}' removed!")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' not found.")
    except Exception as e:
        print(f"Error removing channel: {e}")
        await message.reply("❌ Failed to remove channel. Try again.")

# Command to list all connected channels
@Client.on_message(filters.command("channels") & filters.private)
async def list_channels(client, message: Message):
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("No channels connected yet.")
        return

    channel_list = [f"📢 **{channel['name']}** (`{channel['_id']}`)" for channel in channels]
    response = "**Connected Channels:**\n" + "\n".join(channel_list)
    await message.reply(response)

# Command to send a post to all connected channels
@Client.on_message(filters.command("post"))
async def post_message(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /post <message>")
        return

    # Extract the message text
    text = " ".join(message.command[1:])

    # Post the message to all channels
    messages = []
    for channel in CHANNELS:
        sent_message = await client.send_message(channel, text)
        messages.append({"channel_id": channel, "message_id": sent_message.id})

    # Save the latest post to the database
    await db.save_latest_post(messages)
    await message.reply_text("Message posted in all channels!")

@Client.on_message(filters.command("del_post"))
async def delete_message(client: Client, message: Message):
    # Retrieve the latest post's messages
    latest_post = await db.get_latest_post()

    if not latest_post:
        await message.reply_text("No messages to delete.")
        return
    # Delete messages from all channels
    for msg in latest_post:
        await client.delete_messages(msg["channel_id"], msg["message_id"])
    # Clear the latest post from the database
    await db.delete_latest_post()
    await message.reply_text("Messages deleted from all channels!")
