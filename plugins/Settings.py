from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import db
from config import RENAME_MODE

# Variable for the settings page picture
Setting_pic = "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg"  # Replace with your file ID or URL

async def get_settings_text(user_id):
    """Returns the settings text with thumbnail and caption info."""
    thumb = await db.get_thumbnail(user_id)
    caption = await db.get_caption(user_id)

    text = "**╭───[ ꜱᴇᴛᴛɪɴɢꜱ ]───〄**\n"
    text += "**│**\n"
    text += f"**│ ᴛʜᴜᴍʙ sᴛᴀᴛᴜs : {'✅' if thumb else '❌'}**\n"
    text += f"**│ ᴄᴀᴘᴛɪᴏɴ ᴍᴏᴅᴇ : {'✅' if caption else '❌'}**\n"
    text += "**│**\n"
    text += "**╰───────────⍟**\n\n"
    text += "🔽 **Use the buttons below to manage your settings.**"

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

    await client.send_photo(
        chat_id=message.chat.id,
        photo=Setting_pic,
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^set_thumb$"))
async def set_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    await query.message.edit_text("📷 **Send me a thumbnail image**")

    thumb = await client.listen(query.message.chat.id, filters=filters.photo)
    await db.set_thumbnail(query.from_user.id, file_id=thumb.photo.file_id)

    # Delete user-sent message (Thumbnail)
    await thumb.delete()

    await query.message.edit_text("✅ **Thumbnail saved successfully!**", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]))


@Client.on_callback_query(filters.regex("^del_thumb$"))
async def delete_thumbnail(client: Client, query: CallbackQuery):
    if not RENAME_MODE:
        return

    thumb = await db.get_thumbnail(query.from_user.id)
    if not thumb:
        return await query.answer("No thumbnail found! ❌", show_alert=True)

    await db.set_thumbnail(query.from_user.id, file_id=None)
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
        "⏰ Duration: `{duration}`"
    )

    caption = await client.listen(query.message.chat.id, filters=filters.text)
    await db.set_caption(query.from_user.id, caption=caption.text)

    # Delete user-sent message (Caption)
    await caption.delete()

    await query.message.edit_text("✅ **Caption saved successfully!**", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ]))


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

    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup(buttons))

