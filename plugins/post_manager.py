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

)


# Command to post a message to all channels
@app.on_message(filters.command("post") & filters.private & filters.reply)
def post_message_command(client: Client, message: Message):
    # Get the replied message
    replied_message = message.reply_to_message

    # Get all channels from the database
    channels = get_all_channels()

    if not channels:
        message.reply_text("❌ No channels in the database!")
        return

    # Forward the replied message to all channels
    for channel_id in channels:
        try:
            replied_message.forward(chat_id=channel_id)
        except Exception as e:
            print(f"Failed to forward message to channel {channel_id}: {e}")

    message.reply_text("✅ Message posted to all channels!")

# Command to delete a message from all channels
@app.on_message(filters.command("delete") & filters.private & filters.reply)
def delete_message_command(client: Client, message: Message):
    # Get the replied message
    replied_message = message.reply_to_message

    # Get all channels from the database
    channels = get_all_channels()

    if not channels:
        message.reply_text("❌ No channels in the database!")
        return

    # Delete the replied message from all channels
    for channel_id in channels:
        try:
            client.delete_messages(chat_id=channel_id, message_ids=replied_message.id)
        except Exception as e:
            print(f"Failed to delete message from channel {channel_id}: {e}")

    message.reply_text("✅ Message deleted from all channels!")
