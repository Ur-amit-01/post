from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import db
from config import RENAME_MODE

# Function to create the settings keyboard
def settings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Set Thumbnail", callback_data="set_thumb"),
         InlineKeyboardButton("Show Thumbnail", callback_data="show_thumb"),
         InlineKeyboardButton("Delete Thumbnail", callback_data="delete_thumb")],
        [InlineKeyboardButton("Set Caption", callback_data="set_caption"),
         InlineKeyboardButton("Show Caption", callback_data="show_caption"),
         InlineKeyboardButton("Delete Caption", callback_data="delete_caption")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_settings")]  # Back button
    ])

# Command to start the settings menu
@Client.on_message(filters.private & filters.command(['settings']))
async def settings_menu(client, message):
    if RENAME_MODE == False:
        return 
    await message.reply_text("**Settings Menu**", reply_markup=settings_keyboard())

# Callback query handler
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "set_thumb":
        await callback_query.answer("Send me your thumbnail")
        thumb = await client.ask(callback_query.message.chat.id, "**Send me your thumbnail**")
        if thumb.media and thumb.media == enums.MessageMediaType.PHOTO:
            await db.set_thumbnail(user_id, file_id=thumb.photo.file_id)
            await callback_query.message.reply("**Thumbnail saved successfully ✅️**", reply_markup=settings_keyboard())
        else:
            await callback_query.message.reply("**This is not a picture**", reply_markup=settings_keyboard())

    elif data == "show_thumb":
        thumb = await db.get_thumbnail(user_id)
        if thumb:
            await client.send_photo(chat_id=callback_query.message.chat.id, photo=thumb, reply_markup=settings_keyboard())
        else:
            await callback_query.message.reply_text("😔 **Sorry! No thumbnail found...** 😔", reply_markup=settings_keyboard())

    elif data == "delete_thumb":
        await db.set_thumbnail(user_id, file_id=None)
        await callback_query.message.reply_text("**Thumbnail deleted successfully ✅️**", reply_markup=settings_keyboard())

    elif data == "set_caption":
        await callback_query.answer("Send me your caption")
        caption = await client.ask(callback_query.message.chat.id, "**__𝙶𝚒𝚟𝚎 𝚖𝚎 � 𝚌𝚊𝚙𝚝𝚒𝚘𝚗 𝚝𝚘 �𝚜𝚎𝚝.__\n\nAvailable Filling :-\n📂 File Name: `{filename}`\n\n💾 Size: `{filesize}`\n\n⏰ Duration: `{duration}`**")
        await db.set_caption(user_id, caption=caption.text)
        await callback_query.message.reply_text("__**✅ 𝚈𝙾𝚄𝚁 𝙲𝙰𝙿𝚃𝙸𝙾𝙽 𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝚂𝙰𝚅𝙴𝙳**__", reply_markup=settings_keyboard())

    elif data == "show_caption":
        caption = await db.get_caption(user_id)
        if caption:
            await callback_query.message.reply_text(f"**Your Caption:-**\n\n`{caption}`", reply_markup=settings_keyboard())
        else:
            await callback_query.message.reply_text("😔**Sorry ! No Caption found...**😔", reply_markup=settings_keyboard())

    elif data == "delete_caption":
        await db.set_caption(user_id, caption=None)
        await callback_query.message.reply_text("**Your Caption deleted successfully**✅️", reply_markup=settings_keyboard())

    elif data == "back_to_settings":
        await callback_query.message.edit_text("**Settings Menu**", reply_markup=settings_keyboard())

    await callback_query.answer()

# Command to view thumbnail
@Client.on_message(filters.private & filters.command(['view_thumb']))
async def viewthumb(client, message):
    if RENAME_MODE == False:
        return 
    thumb = await db.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb, reply_markup=settings_keyboard())
    else:
        await message.reply_text("😔 **Sorry! No thumbnail found...** 😔", reply_markup=settings_keyboard()) 

# Command to delete thumbnail
@Client.on_message(filters.private & filters.command(['del_thumb']))
async def removethumb(client, message):
    if RENAME_MODE == False:
        return 
    await db.set_thumbnail(message.from_user.id, file_id=None)
    await message.reply_text("**Thumbnail deleted successfully ✅️**", reply_markup=settings_keyboard())

# Command to set thumbnail
@Client.on_message(filters.private & filters.command(['set_thumb']))
async def addthumbs(client, message):
    if RENAME_MODE == False:
        return 
    thumb = await client.ask(message.chat.id, "**Send me your thumbnail**")
    if thumb.media and thumb.media == enums.MessageMediaType.PHOTO:
        await db.set_thumbnail(message.from_user.id, file_id=thumb.photo.file_id)
        await message.reply("**Thumbnail saved successfully ✅️**", reply_markup=settings_keyboard())
    else:
        await message.reply("**This is not a picture**", reply_markup=settings_keyboard())

# Command to set caption
@Client.on_message(filters.private & filters.command('set_caption'))
async def add_caption(client, message):
    if RENAME_MODE == False:
        return 
    caption = await client.ask(message.chat.id, "**__𝙶𝚒𝚟𝚎 �𝚖𝚎 � �𝚌𝚊𝚙𝚝𝚒𝚘𝚗 �𝚝𝚘 �𝚜𝚎𝚝.__\n\nAvailable Filling :-\n📂 File Name: `{filename}`\n\n💾 Size: `{filesize}`\n\n⏰ Duration: `{duration}`**")
    await db.set_caption(message.from_user.id, caption=caption.text)
    await message.reply_text("__**✅ 𝚈𝙾𝚄𝚁 𝙲𝙰𝙿𝚃𝙸𝙾𝙽 𝚂𝚄𝙲𝙲𝙴𝚂𝚂𝙵𝚄𝙻𝙻𝚈 𝚂𝙰𝚅𝙴𝙳**__", reply_markup=settings_keyboard())

# Command to delete caption
@Client.on_message(filters.private & filters.command('del_caption'))
async def delete_caption(client, message):
    if RENAME_MODE == False:
        return 
    caption = await db.get_caption(message.from_user.id)  
    if not caption:
       return await message.reply_text("😔**Sorry ! No Caption found...**😔", reply_markup=settings_keyboard())
    await db.set_caption(message.from_user.id, caption=None)
    await message.reply_text("**Your Caption deleted successfully**✅️", reply_markup=settings_keyboard())
                                       
# Command to see caption
@Client.on_message(filters.private & filters.command('see_caption'))
async def see_caption(client, message):
    if RENAME_MODE == False:
        return 
    caption = await db.get_caption(message.from_user.id)  
    if caption:
       await message.reply_text(f"**Your Caption:-**\n\n`{caption}`", reply_markup=settings_keyboard())
    else:
       await message.reply_text("😔**Sorry ! No Caption found...**😔", reply_markup=settings_keyboard())

  
