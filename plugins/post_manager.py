from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Database helper
import time
import random
from config import *

LOG_TEXT = "**New User:** {}\n**User ID:** `{}`\n**Total Users:** `{}`"  # Log message format

# Function to check if the user is the admin
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN

# Command to start the bot (public command)
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)  # React with a random emoji
    except:
        pass

    # Add user to the database if they don't exist
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        total_users = await db.total_users_count()
        await client.send_message(LOG_CHANNEL, LOG_TEXT.format(message.from_user.mention, message.from_user.id, total_users))

    # Welcome message
    txt = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        f"**🔋Welcome to the Channel Manager Bot, Manage multiple channels and post messages with ease!**\n\n"
        f"> **ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 :- @Axa_bachha**"
    )
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')]
    ])

    # Send the start message with or without a picture
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)

# Command to add the current channel to the database
@Client.on_message(filters.command("add") & filters.channel)
async def add_current_channel(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only my owner can use me.")
        return

    channel_id = message.chat.id
    channel_name = message.chat.title

    try:
        added = await db.add_channel(channel_id, channel_name)
        if added:
            await message.reply(f"**Channel '{channel_name}' added! ✅**")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' already exists.")
    except Exception as e:
        print(f"Error adding channel: {e}")
        await message.reply("❌ Failed to add channel. Contact developer.")

# Command to remove the current channel from the database
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_current_channel(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only my owner can use me.")
        return

    channel_id = message.chat.id
    channel_name = message.chat.title

    try:
        if await db.is_channel_exist(channel_id):
            await db.delete_channel(channel_id)
            await message.reply(f"**Channel '{channel_name}' removed from my database!**")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' not found.")
    except Exception as e:
        print(f"Error removing channel: {e}")
        await message.reply("❌ Failed to remove channel. Try again.")

# Command to list all connected channels
@Client.on_message(filters.command("channels") & filters.private)
async def list_channels(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only my owner can use me.")
        return

    # Retrieve all channels from the database
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("No channels connected yet.")
        return

    total_channels = len(channels)

    # Format the list of channels
    channel_list = [f"📢 **{channel['name']}** (`{channel['_id']}`)" for channel in channels]
    response = (
        f"> **Total Channels :- ({total_channels})**\n\n"  # Add total count here
        + "\n".join(channel_list)
    )

    await message.reply(response)

@Client.on_message(filters.command("post") & filters.private)
async def send_post(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only my owner can use me.")
        return

    # Check if the user is replying to a message
    if not message.reply_to_message:
        await message.reply("❌ Reply to a message to post it.")
        return

    post_content = message.reply_to_message
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("No channels connected yet.")
        return

    # Generate a unique post ID (using timestamp)
    post_id = int(time.time())
    sent_messages = []

    for channel in channels:
        try:
            # Copy the message to the channel
            sent_message = await client.copy_message(
                chat_id=channel["_id"],  # Channel ID
                from_chat_id=message.chat.id,  # User's chat ID
                message_id=post_content.id  # ID of the replied message
            )

            # Save the sent message details
            sent_messages.append({"channel_id": channel["_id"], "message_id": sent_message.id})
        except Exception as e:
            print(f"Error posting to channel {channel['_id']}: {e}")
            await message.reply(f"❌ Failed to post to channel {channel['_id']}. Error: {e}")

    # Save the post with its unique ID
    await db.save_post(post_id, sent_messages)

    # Reply with post status and user ID
    await message.reply(
        f"**• Post sent to all channels! ✅\n"
        f"• Post ID: `{post_id}` ✍🏻\n"
        f"• User ID: `{message.from_user.id}`**"
    )

@Client.on_message(filters.command("del_post") & filters.private)
async def delete_post(client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply("❌ Only my owner can use me.")
        return

    # Check if the user provided a post ID
    if len(message.command) < 2:
        await message.reply("**Usage: /del_post <post_id>**")
        return

    # Extract the post ID
    post_id = message.command[1]

    try:
        post_id = int(post_id)  # Convert to integer
    except ValueError:
        await message.reply("❌ Invalid post ID. Please provide a valid integer.")
        return

    # Retrieve the post's details from the database
    post = await db.get_post(post_id)

    if not post:
        await message.reply(f"❌ No post found with ID `{post_id}`.")
        return

    # Delete the messages from all channels
    for msg in post:
        try:
            await client.delete_messages(
                chat_id=msg["channel_id"],  # Channel ID
                message_ids=msg["message_id"]  # Message ID
            )
        except Exception as e:
            print(f"Error deleting message from channel {msg['channel_id']}: {e}")
            await message.reply(f"❌ Failed to delete message from channel {msg['channel_id']}. Error: {e}")

    # Delete the post from the database
    await db.delete_post(post_id)
    await message.reply(f"**✅ Post `{post_id}` deleted from all channels!**")

