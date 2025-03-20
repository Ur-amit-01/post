from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db  # Assuming you have a database helper

# Command to add multiple channels
@Client.on_message(filters.command("addchannel") & filters.private)
async def add_channel(client, message: Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("❌ Usage: `/addchannel <channel_id1>, <channel_id2>, ...`\nExample: `/addchannel -1001234567890, -1009876543210`", parse_mode="markdown")
        return

    channel_ids = args[1].replace(" ", "").split(",")  # Remove spaces and split by comma
    added_channels = []
    already_added = []
    failed_channels = []

    for channel_id in channel_ids:
        try:
            channel_id = int(channel_id)
            chat = await client.get_chat(channel_id)  # Fetch channel info
            channel_name = chat.title

            added = await db.add_channel(channel_id, channel_name)  # Save to DB
            if added:
                added_channels.append(channel_name)
            else:
                already_added.append(channel_name)

        except Exception as e:
            failed_channels.append(channel_id)
            print(f"Error adding channel {channel_id}: {e}")

    response = "✅ **Channel(s) Added Successfully:**\n" + "\n".join(added_channels) if added_channels else ""
    response += "\nℹ️ **Already Added:**\n" + "\n".join(already_added) if already_added else ""
    response += "\n❌ **Failed to Add:**\n" + ", ".join(failed_channels) if failed_channels else ""

    await message.reply(response if response else "❌ No channels were added.")

# Command to delete multiple channels
@Client.on_message(filters.command("delchannel") & filters.private)
async def del_channel(client, message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.reply("❌ Usage: `/delchannel <channel_id1>, <channel_id2>, ...`\nExample: `/delchannel -1001234567890, -1009876543210`", parse_mode="markdown")
        return

    channel_ids = args[1].replace(" ", "").split(",")  # Remove spaces and split by comma
    deleted_channels = []
    not_found_channels = []

    for channel_id in channel_ids:
        try:
            channel_id = int(channel_id)

            deleted = await db.delete_channel(channel_id)  # Remove from DB
            if deleted:
                deleted_channels.append(str(channel_id))
            else:
                not_found_channels.append(str(channel_id))

        except Exception as e:
            not_found_channels.append(str(channel_id))
            print(f"Error deleting channel {channel_id}: {e}")

    response = "✅ **Channel(s) Deleted Successfully:**\n" + "\n".join(deleted_channels) if deleted_channels else ""
    response += "\n❌ **Not Found in Database:**\n" + ", ".join(not_found_channels) if not_found_channels else ""

    await message.reply(response if response else "❌ No channels were deleted.")

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

