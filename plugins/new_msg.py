from pyrogram import Client, filters
from helper.database import db

# Command to add the channel (Only works if sent in a channel)
@Client.on_message(filters.command("add") & filters.channel)
async def add_channel(client, message):
    channel_id = message.chat.id
    added = await db.add_channel(channel_id)  # Using the new database function

    if added:
        await message.reply("✅ Channel added! Now, all messages will be formatted.")
    else:
        await message.reply("ℹ️ This channel is already added.")

# Command to remove the channel (Only works if sent in a channel)
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_channel(client, message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if the channel exists
        await db.remove_channel(channel_id)
        await message.reply("❌ Channel removed! Messages will no longer be formatted.")
    else:
        await message.reply("ℹ️ This channel is not in the list.")

# Automatically format messages in added channels
@Client.on_message(filters.channel)
async def format_message(client, message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if channel is in the database
        if message.text and not message.text.startswith("/"):  # Ignore commands
            formatted_text = f"```\n{message.text}\n```"
            await message.edit_text(formatted_text)  # Edit message with formatting

# Save formatting when user sends /cap with a message
@Client.on_message(filters.command("cap") & filters.channel)
async def save_formatting(client, message):

    # Check if the user provided any text after /cap
    if len(message.command) < 2:
        help_message = (
            "**How to use /cap:**\n\n"
            "To save a formatting template for media captions, use the following format:\n"
            "/cap Your formatting text with `{filename}` and `{filecaption}`\n\n"
            "**Example:**\n"
            "/cap File: `{filename}`\nCaption: `{filecaption}`\n\n"
            "This will save the formatting and apply it to all upcoming media files in this channel."
        )
        return await message.reply(help_message)

    # Extract the formatting text from the /cap command
    formatting_text = " ".join(message.command[1:])  # Extract text after /cap
    await db.save_formatting(channel_id, formatting_text)  # Save formatting in the database
    await message.reply("✅ Formatting saved! It will be applied to all upcoming media captions.")

# Apply saved formatting to media captions
@Client.on_message(filters.channel & (filters.document | filters.photo | filters.video | filters.audio))
async def apply_formatting_to_media(client, message):
    channel_id = message.chat.id
    if not await db.is_channel_exist(channel_id):
        return

    # Get saved formatting from the database
    formatting = await db.get_formatting(channel_id)
    if not formatting:
        return

    # Prepare caption with variables
    filename = message.document.file_name if message.document else None
    filecaption = message.caption if message.caption else ""
    caption = formatting.format(filename=filename, filecaption=filecaption)

    # Edit the media caption with the formatted text
    await message.edit_caption(caption)
