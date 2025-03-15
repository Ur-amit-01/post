from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import RENAME_MODE


async def get_settings_text(user_id):
    """Returns the settings text with thumbnail and caption info."""
    thumb = await db.get_thumbnail(user_id)
    caption = await db.get_caption(user_id)

    text = "**⚙️ Settings Menu**\n\n"
    text += "🖼 **Thumbnail:** " + ("✅ Set" if thumb else "❌ Not Set") + "\n"
    text += "📝 **Caption:** " + (f"✅ Set\n\n📄 `{caption}`" if caption else "❌ Not Set") + "\n"
    text += "\n🔽 **Use the buttons below to manage your settings.**"

    return text


@Client.on_message(filters.private & filters.command("settings"))
async def settings_menu(client, message):
    if not RENAME_MODE:
        return

    user_id = message.from_user.id
    text = await get_settings_text(user_id)

    buttons = [
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="set_thumb")],
        [InlineKeyboardButton("📷 View Thumbnail", callback_data="show_thumb"),
         InlineKeyboardButton("❌ Delete Thumbnail", callback_data="del_thumb")],
        [InlineKeyboardButton("✏️ Set Caption", callback_data="set_caption")],
        [InlineKeyboardButton("📄 View Caption", callback_data="see_caption"),
         InlineKeyboardButton("🗑 Delete Caption", callback_data="del_caption")]
    ]

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
        await query.message.edit_text("✅ **Thumbnail saved successfully!**", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    else:
        await query.message.edit_text("❌ **Invalid file! Please send an image.**", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))


@Client.on_callback_query(filters.regex("^show_thumb$"))
async def show_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    thumb = await db.get_thumbnail(query.from_user.id)
    if thumb:
        await query.message.edit_media(
            media=enums.InputMediaPhoto(thumb),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="settings")]])
        )
    else:
        await query.answer("😔 No thumbnail found!", show_alert=True)


@Client.on_callback_query(filters.regex("^del_thumb$"))
async def delete_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    thumb = await db.get_thumbnail(query.from_user.id)
    if not thumb:
        return await query.answer("No thumbnail found! ❌", show_alert=True)

    await db.get_thumbnail(query.from_user.id, file_id=None)
    await query.message.edit_text("✅ **Thumbnail deleted successfully!**", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]))


@Client.on_callback_query(filters.regex("^set_caption$"))
async def set_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    await query.message.edit_text(
        "✏ **Send me a caption to set.**\n\n"
        "📂 **Available Fillings:**\n"
        "📂 File Name: `{filename}`\n"
        "💾 Size: `{filesize}`\n"
        "⏰ Duration: `{duration}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="settings")]])
    )

    caption = await client.ask(query.message.chat.id, "✏ **Enter your caption:**")
    await db.set_caption(query.from_user.id, caption=caption.text)
    await query.message.edit_text("✅ **Caption saved successfully!**", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]))


@Client.on_callback_query(filters.regex("^see_caption$"))
async def see_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    caption = await db.get_caption(query.from_user.id)
    if caption:
        await query.message.edit_text(f"📄 **Your Caption:**\n\n`{caption}`", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))
    else:
        await query.answer("No caption found! ❌", show_alert=True)


@Client.on_callback_query(filters.regex("^del_caption$"))
async def delete_caption(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    caption = await db.get_caption(query.from_user.id)
    if not caption:
        return await query.answer("No caption found! ❌", show_alert=True)

    await db.set_caption(query.from_user.id, caption=None)
    await query.message.edit_text("✅ **Caption deleted successfully!**", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]))


@Client.on_callback_query(filters.regex("^settings$"))
async def back_to_settings(client: Client, query: CallbackQuery):
    """Handles the 'Back' button to return to the settings menu."""
    if not RENAME_MODE:
        return

    user_id = query.from_user.id
    text = await get_settings_text(user_id)

    buttons = [
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="set_thumb")],
        [InlineKeyboardButton("📷 View Thumbnail", callback_data="show_thumb"),
         InlineKeyboardButton("❌ Delete Thumbnail", callback_data="del_thumb")],
        [InlineKeyboardButton("✏️ Set Caption", callback_data="set_caption")],
        [InlineKeyboardButton("📄 View Caption", callback_data="see_caption"),
         InlineKeyboardButton("🗑 Delete Caption", callback_data="del_caption")]
    ]

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

