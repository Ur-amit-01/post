from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import RENAME_MODE


@Client.on_message(filters.private & filters.command("settings"))
async def settings_menu(client, message):
    if not RENAME_MODE:
        return

    user_id = message.from_user.id
    thumb = await db.get_thumbnail(user_id)
    caption = await db.get_caption(user_id)

    buttons = [
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="set_thumb")],
        [InlineKeyboardButton("📷 Show Thumbnail", callback_data="show_thumb"),
         InlineKeyboardButton("❌ Delete Thumbnail", callback_data="del_thumb")],
        [InlineKeyboardButton("✏️ Set Caption", callback_data="set_caption")],
        [InlineKeyboardButton("📄 Show Caption", callback_data="see_caption"),
         InlineKeyboardButton("🗑 Delete Caption", callback_data="del_caption")]
    ]

    text = "**🔧 Settings Menu**\n\n"
    if thumb:
        text += "✅ **Thumbnail Set**\n"
    else:
        text += "❌ **No Thumbnail**\n"
    
    if caption:
        text += f"✅ **Caption:** `{caption}`\n"
    else:
        text += "❌ **No Caption**\n"

    await message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^set_thumb$"))
async def set_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    await query.message.edit_text("📷 **Send me a thumbnail image**")

    thumb = await client.ask(query.message.chat.id, "📷 **Send a thumbnail image:**")
    if thumb.media and thumb.media == enums.MessageMediaType.PHOTO:
        await db.set_thumbnail(query.from_user.id, file_id=thumb.photo.file_id)
        await query.message.edit_text("✅ **Thumbnail saved successfully!**")
    else:
        await query.message.edit_text("❌ **Invalid file! Please send an image.**")


@Client.on_callback_query(filters.regex("^show_thumb$"))
async def show_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    thumb = await db.get_thumbnail(query.from_user.id)
    if thumb:
        await client.send_photo(query.message.chat.id, photo=thumb)
    else:
        await query.answer("😔 No thumbnail found!", show_alert=True)


@Client.on_callback_query(filters.regex("^del_thumb$"))
async def delete_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    await db.set_thumbnail(query.from_user.id, file_id=None)
    await query.message.edit_text("✅ **Thumbnail deleted successfully!**")


@Client.on_callback_query(filters.regex("^set_caption$"))
async def set_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    await query.message.edit_text(
        "✏ **Send me a caption to set.**\n\n"
        "Available Fillings:\n"
        "📂 File Name: `{filename}`\n"
        "💾 Size: `{filesize}`\n"
        "⏰ Duration: `{duration}`"
    )

    caption = await client.ask(query.message.chat.id, "✏ **Enter your caption:**")
    await db.set_caption(query.from_user.id, caption=caption.text)
    await query.message.edit_text("✅ **Caption saved successfully!**")


@Client.on_callback_query(filters.regex("^see_caption$"))
async def see_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    caption = await db.get_caption(query.from_user.id)
    if caption:
        await query.message.edit_text(f"📄 **Your Caption:**\n\n`{caption}`")
    else:
        await query.answer("😔 No caption found!", show_alert=True)


@Client.on_callback_query(filters.regex("^del_caption$"))
async def delete_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    caption = await db.get_caption(query.from_user.id)
    if not caption:
        return await query.answer("😔 No caption found!", show_alert=True)

    await db.set_caption(query.from_user.id, caption=None)
    await query.message.edit_text("✅ **Caption deleted successfully!**")

