from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Database helper
import time
import random
import asyncio
from datetime import datetime, timedelta
from config import *

# Command to start the bot (public command)
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        total_users = await db.total_users_count()
        await client.send_message(LOG_CHANNEL, LOG_TEXT.format(message.from_user.mention, message.from_user.id, total_users))

    txt = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n"
        f"**Welcome to the Channel Manager Bot, Manage multiple channels and post messages with ease! 😌**\n\n"
        f"> **ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 :- @Axa_bachha**"
    )
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'), InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')]
    ])

    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)

@Client.on_message(filters.command("add") & filters.channel)
async def add_current_channel(client, message: Message):
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

@Client.on_message(filters.command("rem") & filters.channel)
async def remove_current_channel(client, message: Message):
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

@Client.on_message(filters.command("channels") & filters.private & filters.user(ADMIN))
async def list_channels(client, message: Message):
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("**No channels connected yet.🙁**")
        return

    total_channels = len(channels)
    channel_list = [f"📢 **{channel['name']}** :- `{channel['_id']}`" for channel in channels]
    response = (
        f"> **Total Channels :- ({total_channels})**\n\n"
        + "\n".join(channel_list)
    )

    await message.reply(response)

async def delete_post_after_delay(client, post_id, delay_seconds, owner_id):
    await asyncio.sleep(delay_seconds)
    
    post = await db.get_post(post_id)
    if not post:
        return
    
    deleted_channels = []
    failed_channels = []
    
    for msg in post['messages']:
        try:
            await client.delete_messages(
                chat_id=msg["channel_id"],
                message_ids=msg["message_id"]
            )
            channel = await db.get_channel(msg["channel_id"])
            if channel:
                deleted_channels.append(channel['name'])
        except Exception as e:
            print(f"Error deleting message from channel {msg['channel_id']}: {e}")
            channel = await db.get_channel(msg["channel_id"])
            if channel:
                failed_channels.append(channel['name'])
    
    await db.delete_post(post_id)
    
    # Send confirmation to owner
    confirmation_msg = "⏰ **Auto-Deletion Complete**\n\n"
    if deleted_channels:
        confirmation_msg += f"✅ Successfully deleted from:\n- " + "\n- ".join(deleted_channels) + "\n\n"
    if failed_channels:
        confirmation_msg += f"❌ Failed to delete from:\n- " + "\n- ".join(failed_channels)
    
    try:
        await client.send_message(owner_id, confirmation_msg)
    except Exception as e:
        print(f"Error sending deletion confirmation: {e}")

def parse_time(time_str):
    try:
        # Handle formats like "9h", "30m", "1d", "45s"
        if time_str[-1].isdigit():
            return int(time_str), "hour"  # Default to hours if no unit specified
        
        unit = time_str[-1].lower()
        value = int(time_str[:-1])
        
        if unit == 'h':
            return value * 3600, "hour"
        elif unit == 'm':
            return value * 60, "minute"
        elif unit == 'd':
            return value * 86400, "day"
        elif unit == 's':
            return value, "second"
        else:
            return None, None
    except:
        return None, None

@Client.on_message(filters.command("post") & filters.private & filters.user(ADMIN))
async def send_post(client, message: Message):
    if not message.reply_to_message:
        await message.reply("**Reply to a message to post it.**")
        return

    delete_after = None
    time_unit = None
    
    if len(message.command) > 1:
        # Try parsing compact format first (e.g., "9h", "30m")
        time_str = " ".join(message.command[1:])
        seconds, time_unit = parse_time(time_str)
        
        if seconds is None:
            # Try parsing spaced format (e.g., "9 hour", "30 min")
            try:
                time_value = int(message.command[1])
                if len(message.command) > 2:
                    time_unit = message.command[2].lower()
                else:
                    time_unit = "hour"  # Default unit
                
                if time_unit in ["hour", "hours", "h"]:
                    seconds = time_value * 3600
                elif time_unit in ["minute", "minutes", "min", "m"]:
                    seconds = time_value * 60
                elif time_unit in ["day", "days", "d"]:
                    seconds = time_value * 86400
                elif time_unit in ["second", "seconds", "sec", "s"]:
                    seconds = time_value
                else:
                    raise ValueError("Invalid time unit")
            except (ValueError, IndexError):
                await message.reply("❌ Invalid time format. Use: /post [time][unit] or /post [time] [unit]\nExamples:\n/post 9h\n/post 30m\n/post 1d\n/post 45s\n/post 2 hour")
                return
        
        delete_after = seconds
    else:
        # No time specified
        pass

    post_content = message.reply_to_message
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("**No channels connected yet.**")
        return

    post_id = int(time.time())
    sent_messages = []

    for channel in channels:
        try:
            sent_message = await client.copy_message(
                chat_id=channel["_id"],
                from_chat_id=message.chat.id,
                message_id=post_content.id
            )
            sent_messages.append({"channel_id": channel["_id"], "message_id": sent_message.id})
        except Exception as e:
            print(f"Error posting to channel {channel['_id']}: {e}")
            await message.reply(f"❌ Failed to post to channel {channel['_id']}. Error: {e}")

    post_data = {
        "post_id": post_id,
        "messages": sent_messages,
        "delete_after": delete_after,
        "owner_id": message.from_user.id
    }
    await db.save_post(post_id, post_data)

    if delete_after:
        asyncio.create_task(delete_post_after_delay(client, post_id, delete_after, message.from_user.id))
        # Format time display
        if time_unit.startswith("hour"):
            time_display = f"{delete_after//3600} hour{'s' if delete_after//3600 > 1 else ''}"
        elif time_unit.startswith("minute"):
            time_display = f"{delete_after//60} minute{'s' if delete_after//60 > 1 else ''}"
        elif time_unit.startswith("day"):
            time_display = f"{delete_after//86400} day{'s' if delete_after//86400 > 1 else ''}"
        else:
            time_display = f"{delete_after} second{'s' if delete_after > 1 else ''}"
        
        deletion_note = f"\n• This post will auto-delete after {time_display} ⏳"
    else:
        deletion_note = ""

    await message.reply(
        f"**• Post sent to all channels! ✅\n"
        f"• Post ID: `{post_id}` ✍🏻"
        f"{deletion_note}**"
    )

@Client.on_message(filters.command("del_post") & filters.private & filters.user(ADMIN))
async def delete_post(client, message: Message):
    if len(message.command) < 2:
        await message.reply("**Usage: /del_post <post_id>**")
        return

    post_id = message.command[1]

    try:
        post_id = int(post_id)
    except ValueError:
        await message.reply("❌ Invalid post ID. Please provide a valid integer.")
        return

    post = await db.get_post(post_id)

    if not post:
        await message.reply(f"❌ No post found with ID `{post_id}`.")
        return

    deleted_channels = []
    failed_channels = []

    for msg in post['messages']:
        try:
            await client.delete_messages(
                chat_id=msg["channel_id"],
                message_ids=msg["message_id"]
            )
            channel = await db.get_channel(msg["channel_id"])
            if channel:
                deleted_channels.append(channel['name'])
        except Exception as e:
            print(f"Error deleting message from channel {msg['channel_id']}: {e}")
            channel = await db.get_channel(msg["channel_id"])
            if channel:
                failed_channels.append(channel['name'])

    await db.delete_post(post_id)
    
    response = f"**✅ Post `{post_id}` deletion results:**\n"
    if deleted_channels:
        response += f"\n✔️ Deleted from:\n- " + "\n- ".join(deleted_channels)
    if failed_channels:
        response += f"\n\n❌ Failed to delete from:\n- " + "\n- ".join(failed_channels)
    
    await message.reply(response)

# ========================================= CALLBACKS =============================================
# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "start":
        txt = (
            f"> **✨👋🏻 Hey {query.from_user.mention} !!**\n"
            f"**Welcome to the Channel Manager Bot, Manage multiple channels and post messages with ease! 😌**\n\n"
            f"> **ᴅᴇᴠᴇʟᴏᴘᴇʀ 🧑🏻‍💻 :- @Axa_bachha**"
        )
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton('📜 ᴀʙᴏᴜᴛ', callback_data='about'),
             InlineKeyboardButton('🕵🏻‍♀️ ʜᴇʟᴘ', callback_data='help')]
        ])

    elif data == "help":
        txt = HELP_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʀᴇᴏ̨ᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛᴏʀ", callback_data="request")],
            [InlineKeyboardButton("ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ sᴀᴠᴇʀ", callback_data="restricted")],
            [InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')]
        ])

    elif data == "about":
        txt = ABOUT_TXT.format(client.mention)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/axa_bachha"),
             InlineKeyboardButton("🏠 𝙷𝙾𝙼𝙴 🏠", callback_data="start")]
        ])

    elif data == "restricted":
        txt = RESTRICTED_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    elif data == "request":
        txt = REQUEST_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data="help")]
        ])

    await query.message.edit_text(text=txt, reply_markup=reply_markup, disable_web_page_preview=True)


# ========================================= TEXTS =============================================

LOG_TEXT = """<blockquote><b>#NewUser ॥ @interferons_bot </b></blockquote>
<blockquote><b>☃️ Nᴀᴍᴇ :~ {}
🪪 ID :~ <code>{}</code>
👨‍👨‍👦‍👦 ᴛᴏᴛᴀʟ :~ {}</b></blockquote>"""


ABOUT_TXT = """
<b>╭───────────⍟
├➢ ᴍʏꜱᴇʟꜰ : {}
├➢ ᴏᴡɴᴇʀ : <a href=https://t.me/axa_bachha>𝐻𝑜𝑚𝑜 𝑠𝑎𝑝𝑖𝑒𝑛『❅』</a>
├➢ ʟɪʙʀᴀʀʏ : <a href=https://github.com/pyrogram>ᴘʏʀᴏɢʀᴀᴍ</a>
├➢ ʟᴀɴɢᴜᴀɢᴇ : <a href=https://www.python.org>ᴘʏᴛʜᴏɴ 3</a>
├➢ ᴅᴀᴛᴀʙᴀꜱᴇ : <a href=https://cloud.mongodb.com>MᴏɴɢᴏDB</a>
├➢ ꜱᴇʀᴠᴇʀ : <a href=https://apps.koyeb.com>ᴋᴏʏᴇʙ</a>
├➢ ʙᴜɪʟᴅ ꜱᴛᴀᴛᴜꜱ  : ᴘʏᴛʜᴏɴ v3.6.8
╰───────────────⍟

➢ ɴᴏᴛᴇ :- ʀᴇᴘᴏ ɪꜱ ᴘᴀɪᴅ, ᴅᴏɴ'ᴛ ᴅᴍ ꜰᴏʀ ᴛɪᴍᴇᴘᴀꜱꜱ 🙏🏻
</b>"""

HELP_TXT = """
🛸 <b><u>My Functions</u></b> 🛸
"""


RESTRICTED_TXT = """
> **💡 Restricted Content Saver**

**1. 🔒 Private Chats**
➥ For My Owner Only :)

**2. 🌐 Public Chats**
➥ Simply share the post link. I'll download it for you.

**3. 📂 Batch Mode**
➥ Download multiple posts using this format:
> **https://t.me/xxxx/1001-1010**
"""

REQUEST_TXT = """
<b>
> ⚙️ Join Request Acceptor

• I can accept all pending join requests in your channel. 🤝

• Promote @xDzod and @Z900_RoBot with full admin rights in your channel. 🔑

• Send /accept command in the channel to accept all requests at once. 💯
</b>
"""
