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
@Client.on_message(filters.command("post") & filters.private)
async def send_post(client, message: Message):
    if not message.reply_to_message:
        await message.reply("❌ Reply to a message to post it.")
        return

    post_content = message.reply_to_message
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("No channels connected yet.")
        return

    sent_messages = {}
    for channel in channels:
        try:
            sent_message = await client.copy_message(
                chat_id=channel["_id"],
                from_chat_id=message.chat.id,
                message_id=post_content.id
            )
            sent_messages[channel["_id"]] = sent_message.id
            print(f"Posted to {channel['name']} (ID: {channel['_id']})")
        except Exception as e:
            print(f"Error posting to {channel['name']}: {e}")

    await db.save_latest_post(sent_messages)
    await message.reply("✅ Post sent to all channels!")

# Command to delete the latest post
@Client.on_message(filters.command("del_post") & filters.private)
async def delete_post(client, message: Message):
    latest_post = await db.get_latest_post()

    if not latest_post:
        await message.reply("❌ No posts sent yet.")
        return

    for channel_id, message_id in latest_post.items():
        try:
            await client.delete_messages(channel_id, message_id)
            print(f"Deleted post from channel {channel_id}")
        except Exception as e:
            print(f"Error deleting post from {channel_id}: {e}")

    await db.delete_latest_post()
    await message.reply("✅ Latest post deleted!")

# Command to get stats for the latest post
@Client.on_message(filters.command("stats") & filters.private)
async def get_stats(client, message: Message):
    latest_post = await db.get_latest_post()

    if not latest_post:
        await message.reply("❌ No posts sent yet.")
        return

    total_views = 0
    channel_list = []
    for channel_id, message_id in latest_post.items():
        try:
            message = await client.get_messages(channel_id, message_id)
            views = message.views
            total_views += views
            channel_name = (await client.get_chat(channel_id)).title
            channel_list.append(f"📢 **{channel_name}**: {views} views")
        except Exception as e:
            print(f"Error fetching stats for {channel_id}: {e}")

    stats_message = (
        f"📊 **Post Stats**\n\n"
        f"👀 **Total Views**: {total_views}\n\n"
        "**Channels**:\n" + "\n".join(channel_list)
    )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]])
    await message.reply_text(stats_message, reply_markup=keyboard)

# Handle callback queries (e.g., Refresh button)
@Client.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    if callback_query.data == "refresh_stats":
        latest_post = await db.get_latest_post()

        if not latest_post:
            await callback_query.answer("❌ No posts sent yet.")
            return

        total_views = 0
        channel_list = []
        for channel_id, message_id in latest_post.items():
            try:
                message = await client.get_messages(channel_id, message_id)
                views = message.views
                total_views += views
                channel_name = (await client.get_chat(channel_id)).title
                channel_list.append(f"📢 **{channel_name}**: {views} views")
            except Exception as e:
                print(f"Error fetching stats for {channel_id}: {e}")

        updated_message = (
            f"📊 **Post Stats**\n\n"
            f"👀 **Total Views**: {total_views}\n\n"
            "**Channels**:\n" + "\n".join(channel_list)
        )

        await callback_query.message.edit_text(updated_message, reply_markup=callback_query.message.reply_markup)
        await callback_query.answer("✅ Stats refreshed!")
        
