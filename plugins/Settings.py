from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import RENAME_MODE

@Client.on_message(filters.private & filters.command("settings"))
async def open_settings(client, message):
    if RENAME_MODE == False:
        return

    user_id = message.from_user.id
    await update_settings_message(client, message, user_id, new_message=True)

@Client.on_callback_query(filters.regex("^settings$"))
async def callback_settings(client, query):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("toggle_thumb"))
async def toggle_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    thumb = await db.get_thumbnail(user_id)

    if thumb:
        await db.set_thumbnail(user_id, file_id=None)  # Delete thumbnail silently
    else:
        thumb_msg = await client.ask(user_id, "**Send me your thumbnail**")
        if thumb_msg.photo:
            await db.set_thumbnail(user_id, file_id=thumb_msg.photo.file_id)

    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("toggle_caption"))
async def toggle_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    caption = await db.get_caption(user_id)

    if caption:
        await db.set_caption(user_id, caption=None)  # Delete caption silently
    else:
        caption_msg = await client.ask(user_id, "**Give me a caption to set.**\n\nAvailable Fillings:\n📂 `{filename}`\n💾 `{filesize}`\n⏰ `{duration}`")
        await db.set_caption(user_id, caption=caption_msg.text)

    await update_settings_message(client, query.message, user_id)

@Client.on_callback_query(filters.regex("view_thumb"))
async def view_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    thumb = await db.get_thumbnail(user_id)

    if thumb:
        await client.send_photo(chat_id=user_id, photo=thumb)
    await query.answer()  # Silent response

@Client.on_callback_query(filters.regex("see_caption"))
async def see_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    caption = await db.get_caption(user_id)

    if caption:
        await query.message.reply_text(f"**Your Caption:**\n\n`{caption}`")
    else:
        await query.answer("😔 No caption found!", show_alert=True)

@Client.on_callback_query(filters.regex("delete_thumb"))
async def delete_thumb(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    await db.set_thumbnail(user_id, file_id=None)  # Delete thumbnail
    await update_settings_message(client, query.message, user_id)  # Update UI silently

@Client.on_callback_query(filters.regex("delete_caption"))
async def delete_caption(client, query: CallbackQuery):
    if RENAME_MODE == False:
        return

    user_id = query.from_user.id
    await db.set_caption(user_id, caption=None)  # Delete caption
    await update_settings_message(client, query.message, user_id)  # Update UI silently

@Client.on_callback_query(filters.regex("close"))
async def close_settings(client, query: CallbackQuery):
    await query.message.delete()

async def update_settings_message(client, message, user_id, new_message=False):
    """ Updates or sends the settings message dynamically. """
    thumb = await db.get_thumbnail(user_id)
    caption = await db.get_caption(user_id)

    thumb_status = "✅" if thumb else "❌"
    caption_status = "✅" if caption else "❌"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🖼 Thumbnail: {thumb_status}", callback_data="toggle_thumb"),
         InlineKeyboardButton("🔄 View", callback_data="view_thumb"),
         InlineKeyboardButton("🗑 Delete", callback_data="delete_thumb")],
        [InlineKeyboardButton(f"📝 Caption: {caption_status}", callback_data="toggle_caption"),
         InlineKeyboardButton("👀 See", callback_data="see_caption"),
         InlineKeyboardButton("🗑 Delete", callback_data="delete_caption")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

    text = (
        "**╭────[ꜱᴇᴛᴛɪɴɢꜱ]────〄**\n"
        f"**│ ᴛʜᴜᴍʙ sᴛᴀᴛᴜꜱ : {thumb_status}**\n"
        f"**│ ᴄᴀᴘᴛɪᴏɴ ᴍᴏᴅᴇ : {caption_status}**\n"
        "**╰─────────────⍟**"
    )

    if new_message:
        await message.reply_text(text, reply_markup=keyboard)
    else:
        await message.edit_text(text, reply_markup=keyboard)



@Client.on_message(filters.private & filters.command(['set_thumb']))
async def addthumbs(client, message):
    if RENAME_MODE == False:
        return 
    thumb = await client.ask(message.chat.id, "**Send me your thumbnail**")
    if thumb.media and thumb.media == enums.MessageMediaType.PHOTO:
        await db.set_thumbnail(message.from_user.id, file_id=thumb.photo.file_id)
        await message.reply("**Thumbnail saved successfully ✅️**")
    else:
        await message.reply("**This is not a picture**")
        
