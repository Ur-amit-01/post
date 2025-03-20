from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Assuming you have a database helper

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
            await message.reply(f"✅ Channel '{channel_name}' added!")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' is already added.")
    except Exception as e:
        print(f"Error adding channel: {e}")
        await message.reply("❌ An error occurred while adding the channel. Please try again.")

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
            await message.reply(f"✅ Channel '{channel_name}' removed!")
        else:
            await message.reply(f"ℹ️ Channel '{channel_name}' is not in the database.")
    except Exception as e:
        print(f"Error removing channel: {e}")
        await message.reply("❌ An error occurred while removing the channel. Please try again.")

# Command to list all connected channels
@Client.on_message(filters.command("listchannels") & filters.private)
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
        await message.reply("Please reply to the message you want to post.")
        return

    post_content = message.reply_to_message

    # Get all connected channels from the database
    channels = await db.get_all_channels()

    # Send the post to each channel
    sent_messages = {}
    for channel in channels:
        sent_message = await client.send_message(channel["_id"], post_content.text or post_content.caption, post_content.media)
        sent_messages[channel["_id"]] = sent_message.id  # Store message ID for later management

    # Save the sent message IDs in the database
    await db.save_post_messages(sent_messages)
    await message.reply("✅ Post sent to all connected channels!")

# Command to delete the post from all channels
@Client.on_message(filters.command("deletepost") & filters.private)
async def delete_post(client, message: Message):
    # Get the message IDs from the database
    post_messages = await db.get_post_messages()

    # Delete the post from each channel
    for channel_id, message_id in post_messages.items():
        await client.delete_messages(channel_id, message_id)

    await message.reply("✅ Post deleted from all channels!")

# Command to get detailed stats
@Client.on_message(filters.command("stats") & filters.private)
async def get_stats(client, message: Message):
    # Get the post message IDs from the database
    post_messages = await db.get_post_messages()

    if not post_messages:
        await message.reply("No posts have been sent yet.")
        return

    # Calculate total views and prepare channel list
    total_views = 0
    channel_list = []
    for channel_id, message_id in post_messages.items():
        message = await client.get_messages(channel_id, message_id)
        views = message.views
        total_views += views
        channel_name = (await client.get_chat(channel_id)).title
        channel_list.append(f"📢 **{channel_name}**: {views} views")

    # Create the stats message
    stats_message = (
        f"📊 **Post Stats**\n\n"
        f"👀 **Total Views**: {total_views}\n\n"
        "**Channels**:\n" + "\n".join(channel_list)
    )

    # Add a Refresh button
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")]
        ]
    )

    # Send the interactive message
    await message.reply_text(stats_message, reply_markup=keyboard)

# Handle callback queries (e.g., Refresh button)
@Client.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    if callback_query.data == "refresh_stats":
        # Get the updated stats
        post_messages = await db.get_post_messages()

        total_views = 0
        channel_list = []
        for channel_id, message_id in post_messages.items():
            message = await client.get_messages(channel_id, message_id)
            views = message.views
            total_views += views
            channel_name = (await client.get_chat(channel_id)).title
            channel_list.append(f"📢 **{channel_name}**: {views} views")

        # Update the stats message
        updated_message = (
            f"📊 **Post Stats**\n\n"
            f"👀 **Total Views**: {total_views}\n\n"
            "**Channels**:\n" + "\n".join(channel_list)
        )

        # Update the message with the new stats
        await callback_query.message.edit_text(updated_message, reply_markup=callback_query.message.reply_markup)
        await callback_query.answer("Stats refreshed!")
