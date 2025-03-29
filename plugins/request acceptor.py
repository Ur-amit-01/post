import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, BOT_TOKEN, NEW_REQ_MODE, SESSION_STRING
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('join_request_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command('accept'))
async def accept(client, message):
    # Log the chat type for debugging
    print(f"Received message from chat: {message.chat.type}")

    # Check if the command is issued in a private chat (DM)
    if message.chat.type == enums.ChatType.PRIVATE:
        print("Command issued in DM, sending reply...")
        return await message.reply("🚫 **This command works in channels only.**")
    
    # Proceed if the command is issued in a channel
    channel_id = message.chat.id
    show = await client.send_message(channel_id, "⏳ **Please wait...**")
    
    try:
        acc = Client("joinrequest", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("❌ **Login session has expired. Please update the session string and try again.**")
    
    # Directly accept join requests without needing a forwarded message
    msg = await show.edit("✅ **Accepting all join requests... Please wait until it's completed.**")
    
    try:
        while True:
            await acc.approve_all_chat_join_requests(channel_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(channel_id)]
            if not join_requests:
                break
        await msg.edit("🎉 **Successfully accepted all join requests!**")
    except Exception as e:
        await msg.edit(f"⚠️ **An error occurred:** {str(e)}")

@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client: Client, message: Message):
    if not NEW_REQ_MODE:
        return

    user = message.from_user
    chat = message.chat

    try:
        # Approve the request first
        await client.approve_chat_join_request(chat.id, user.id)
        logger.info(f"Approved join request for user {user.id} in chat {chat.id}")

        try:
            # Generate the appropriate channel link
            if chat.username:
                # Public channel
                channel_link = f"https://t.me/{chat.username}"
            else:
                # Private channel - convert ID to t.me/c/ format
                if str(chat.id).startswith("-100"):
                    channel_id = str(chat.id).replace("-100", "")
                else:
                    channel_id = str(chat.id)
                channel_link = f"https://t.me/c/{channel_id}"

            welcome_message = (
                f"**• Hello {user.mention}! 👋🏻\n"
                f"**• Your join request for [{chat.title}]({channel_link}) has been accepted. 💕**\n\n"
                f"> **• Powered by: @Stellar_Bots ✨ @Team_SAT_25**"
            )

            await client.send_message(
                user.id,
                welcome_message,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.MARKDOWN
            )
            logger.info(f"Sent welcome message to user {user.id}")

        except Exception as e:
            logger.error(f"Failed to send welcome message to user {user.id}: {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Failed to approve join request for user {user.id} in chat {chat.id}: {str(e)}", exc_info=True)
