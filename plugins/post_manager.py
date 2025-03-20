from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Assuming you have a database helper
import time

# Command to add the current channel to the database
@Client.on_message(filters.command("add") & filters.channel)
async def add_current_channel(client, message: Message):
    # Extract channel details
    channel_id = message.chat.id
    channel_name = message.chat.title

    # Debug: Print channel details
    print(f"Channel ID: {channel_id}, Channel Name: {channel_name}")

    # Save the channel to the database
    try:
        added = await db.add_channel(channel_id, channel_name)
        if added:
            await message.reply(f"**✅ Channel '{channel_name}' added to my database! 😋**")
        else:
            await message.reply(f"**ℹ️ Channel '{channel_name}' is already added.**")
    except Exception as e:
        print(f"Error adding channel: {e}")
        await message.reply("**❌ An error occurred while adding the channel. Please contact my developer.**")

# Command to remove the current channel from the database
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_current_channel(client, message: Message):
    # Extract channel details
    channel_id = message.chat.id
    channel_name = message.chat.title

    # Debug: Print channel details
    print(f"Channel ID: {channel_id}, Channel Name: {channel_name}")

    # Remove the channel from the database
    try:
        if await db.is_channel_exist(channel_id):
            await db.delete_channel(channel_id)
            await message.reply(f"**✅ Channel '{channel_name}' removed!**")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' is not in the database.")
    except Exception as e:
        print(f"Error removing channel: {e}")
        await message.reply("❌ An error occurred while removing the channel. Please try again.")

# Command to list all connected channels
@Client.on_message(filters.command("channels") & filters.private)
async def list_channels(client, message: Message):
    # Get all connected channels from the database
    channels = await db.get_all_channels()

    if not channels:
        await message.reply("No channels are connected yet.")
        return

    # Prepare the list of channels
    channel_list = [f"📢 **{channel['name']}** (`{channel['_id']}`)" for channel in channels]
    response = "**Connected Channels:**\n" + "\n".join(channel_list)

    await message.reply(response)

# Command to send a post to all connected channels
@Client.on_message(filters.command("post") & filters.private)
async def send_post(client, message: Message):
    if not message.reply_to_message:
        await message.reply("**Please reply to the message you want to post. 🤦🏻**")
        return

    post_content = message.reply_to_message
    print(f"Post Content: {post_content}")  # Debug: Check if post_content is valid

    # Get all connected channels from the database
    channels = await db.get_all_channels()
    print(f"Channels: {channels}")  # Debug: Check if channels are retrieved

    if not channels:
        await message.reply("No channels are connected yet.")
        return

    # Use the message ID from the user's DM as the unique identifier
    post_id = str(message.reply_to_message.id)
    sent_messages = {}

    # Send the post to each channel
    for channel in channels:
        try:
            # Use copy_message to handle media and captions
            sent_message = await client.copy_message(
                chat_id=channel["_id"],
                from_chat_id=message.chat.id,
                message_id=post_content.id
            )
            sent_messages[channel["_id"]] = sent_message.id  # Store message ID for later management
            print(f"Post sent to channel {channel['_id']} with message ID {sent_message.id}")  # Debug
        except Exception as e:
            print(f"Error sending post to channel {channel['_id']}: {e}")

    # Save the sent message IDs in the database with the unique post ID
    await db.save_post_messages(post_id, sent_messages)
    await message.reply(f"**✅ Post sent to all connected channels!**\n\n**Post ID:** `{post_id}`")

# Command to delete the post from all channels
@Client.on_message(filters.command("del_post") & filters.private)
async def delete_post(client, message: Message):
    if not message.reply_to_message:
        await message.reply("**Please reply to the original post message to delete it. 🤦🏻**")
        return

    # Use the message ID from the user's DM as the unique identifier
    post_id = str(message.reply_to_message.id)

    # Get the message IDs for the specified post ID
    post_messages = await db.get_post_messages(post_id)

    if not post_messages:
        await message.reply(f"❌ No posts found with ID: `{post_id}`")
        return

    # Delete the post from each channel
    for channel_id, message_id in post_messages.items():
        try:
            await client.delete_messages(channel_id, message_id)
        except Exception as e:
            print(f"Error deleting post from channel {channel_id}: {e}")

    # Remove the post from the database
    await db.delete_post_messages(post_id)
    await message.reply(f"✅ Post `{post_id}` deleted from all channels!")

# Command to get detailed stats
@Client.on_message(filters.command("stats") & filters.private)
async def get_stats(client, message: Message):
    if not message.reply_to_message:
        await message.reply("**Please reply to the original post message to get stats. 🤦🏻**")
        return

    # Use the message ID from the user's DM as the unique identifier
    post_id = str(message.reply_to_message.id)

    # Get the message IDs for the specified post ID
    post_messages = await db.get_post_messages(post_id)

    if not post_messages:
        await message.reply(f"❌ No posts found with ID: `{post_id}`")
        return

    # Calculate total views and prepare channel list
    total_views = 0
    channel_list = []
    for channel_id, message_id in post_messages.items():
        try:
            message = await client.get_messages(channel_id, message_id)
            views = message.views
            total_views += views
            channel_name = (await client.get_chat(channel_id)).title
            channel_list.append(f"📢 **{channel_name}**: {views} views")
        except Exception as e:
            print(f"Error fetching stats for channel {channel_id}: {e}")

    # Create the stats message
    stats_message = (
        f"📊 **Post Stats**\n\n"
        f"👀 **Total Views**: {total_views}\n\n"
        "**Channels**:\n" + "\n".join(channel_list)
    )

    # Add a Refresh button with the post ID in the callback data
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh_stats:{post_id}")]
        ]
    )

    # Send the interactive message
    await message.reply_text(stats_message, reply_markup=keyboard)

# Handle callback queries (e.g., Refresh button)
@Client.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    # Extract the post ID from the callback data
    callback_data = callback_query.data
    if callback_data.startswith("refresh_stats:"):
        post_id = callback_data.split(":")[1]

        # Get the updated stats
        post_messages = await db.get_post_messages(post_id)

        total_views = 0
        channel_list = []
        for channel_id, message_id in post_messages.items():
            try:
                message = await client.get_messages(channel_id, message_id)
                views = message.views
                total_views += views
                channel_name = (await client.get_chat(channel_id)).title
                channel_list.append(f"📢 **{channel_name}**: {views} views")
            except Exception as e:
                print(f"Error fetching stats for channel {channel_id}: {e}")

        # Update the stats message
        updated_message = (
            f"📊 **Post Stats**\n\n"
            f"👀 **Total Views**: {total_views}\n\n"
            "**Channels**:\n" + "\n".join(channel_list)
        )

        # Update the message with the new stats
        await callback_query.message.edit_text(updated_message, reply_markup=callback_query.message.reply_markup)
        await callback_query.answer("**Stats refreshed!**")
