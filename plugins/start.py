from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, BotCommand
from config import *
from helper.txt import mr
from helper.database import db
from pyrogram.errors import *
import random
from plugins.Fsub import auth_check

# =====================================================================================
@Client.on_message(filters.private & filters.command("start"))
@auth_check
async def start(client, message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass    
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        total_users = await db.total_users_count()
        await client.send_message(LOG_CHANNEL, LOG_TEXT.format(message.from_user.mention, message.from_user.id, total_users))
    
    txt = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        f"**🔋 I am an advanced bot designed to assist you. I can merge PDFs/images, rename your files, and much more.**\n\n"
        f"**🔘 Click on the help button to learn more about my functions!**\n\n"
        f"> **Developer 🧑🏻‍💻 :- @Axa_bachha**"
    )
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('📜 About', callback_data='about'), InlineKeyboardButton('🕵🏻‍♀️ Help', callback_data='help')]
    ])
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)
        
# =====================================================================================

# Set bot commands
@Client.on_message(filters.command("set") & filters.user(ADMIN))
async def set_commands(client: Client, message: Message):
    await client.set_bot_commands([
        BotCommand("start", "🤖 Start the bot"),
        BotCommand("merge", "🛠 Start PDF merge"),
        BotCommand("done", "📂 Merge PDFs"),
        BotCommand("telegraph", "🌐 Get Telegraph link"),
        BotCommand("stickerid", "🎭 Get sticker ID"),
        BotCommand("accept", "✅ Accept pending join requests"),
        BotCommand("users", "👥 Total users"),
        BotCommand("broadcast", "📢 Send message")
    ])
    await message.reply_text("✅ Bot commands have been set.")

# ========================================= CALLBACKS =============================================
# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "start":
        txt = (
            f"> **✨👋🏻 Hey {query.from_user.mention} !!**\n\n"
            f"**🔋 I am an advanced bot designed to assist you. I can merge PDFs/images, rename your files, and much more.**\n\n"
            f"**🔘 Click on the help button to learn more about my functions!**\n\n"
            f"> **Developer 🧑🏻‍💻 :- @Axa_bachha**"
        )
        
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Developer", url='https://t.me/axa_bachha')],
            [InlineKeyboardButton('📜 About', callback_data='about'),
             InlineKeyboardButton('🕵🏻‍♀️ Help', callback_data='help')]
        ])

    elif data == "help":
        txt = HELP_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Contact Developer 🕵🏻‍♀️", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("Request Acceptor", callback_data="request"),
             InlineKeyboardButton("Merge 📄", callback_data="merger")],
            [InlineKeyboardButton("Restricted Content Saver", callback_data="restricted")],
            [InlineKeyboardButton('Telegraph', callback_data='tele'),
             InlineKeyboardButton('Sticker-ID', callback_data='sticker')],
            [InlineKeyboardButton('File Rename ✍🏻📃', callback_data='rename')],
            [InlineKeyboardButton('🏠 Home 🏠', callback_data='start')]
        ])

    elif data == "about":
        txt = ABOUT_TXT.format(client.mention)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Developer", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("🔒 Close", callback_data="close"),
             InlineKeyboardButton("🏠 Home 🏠", callback_data="start")]
        ])

    elif data == "rename":
        await query.message.edit_text(
            text=Rename_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ Back", callback_data="help")]
            ])
        )

    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
        return

    elif data == "sticker":
        txt = STICKER_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="help")]
        ])

    elif data == "tele":
        txt = TELEGRAPH_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="help")]
        ])

    elif data == "restricted":
        txt = RESTRICTED_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="help")]
        ])

    elif data == "merger":
        txt = MERGER_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="help")]
        ])

    elif data == "request":
        txt = REQUEST_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Back", callback_data="help")]
        ])

    await query.message.edit_text(text=txt, reply_markup=reply_markup, disable_web_page_preview=True)


# ========================================= TEXTS =============================================

LOG_TEXT = """<blockquote><b>#NewUser ॥ @z900_Robot</b></blockquote>
<blockquote><b>☃️ Name :~ {}
🪪 ID :~ <code>{}</code>
👨‍👨‍👦‍👦 Total :~ {}</b></blockquote>"""

PROGRESS_BAR = """
╭━━━━❰ Gangster Hacking... ❱━➣
┣⪼ 🗂️ : {1} | {2}
┣⪼ ⏳️ : {0}%
┣⪼ 🚀 : {3}/s
┣⪼ ⏱️ : {4}
╰━━━━━━━━━━━━━━━➣ """

ABOUT_TXT = """
<b>
╭───────────⍟
├➢ Myself : {}
├➢ Owner : <a href=https://t.me/axa_bachha>𝐻𝑜𝑚𝑜 𝑠𝑎𝑝𝑖𝑒𝑛『❅』</a> 
├➢ Library : <a href=https://github.com/pyrogram>Pyrogram</a>
├➢ Language : <a href=https://www.python.org>Python 3</a>
├➢ Database : <a href=https://cloud.mongodb.com>MongoDB</a>
├➢ Server : <a href=https://apps.koyeb.com>Koyeb</a>
├➢ Build Status : Python v3.6.8              
╰───────────────⍟

➢ Note :- Please don't ask for the repo 🤡
</b>
"""

HELP_TXT = """
🌌 <b><u>My Functions 👇🏻</u></b>
"""

Rename_TXT = """
<blockquote>✏️ <b><u>How to Rename a File</u></b></blockquote>
•> /rename - After this command, send your file to rename.
<blockquote>🌌 <b><u>How to Set Thumbnail</u></b></blockquote>
•> /set_thumb - Send a picture to set the thumbnail.  
•> /delthumb - Use this command to delete your old thumbnail.  
•> /viewthumb - Use this command to view your current thumbnail.  

<blockquote>📑 <b><u>How to Set Custom Caption</u></b></blockquote>
•> /set_caption - Set a custom caption  
•> /see_caption - See your custom caption  
•> /del_caption - Delete custom caption  

Example:- /set_caption 📕 File Name: {filename}  
💾 Size: `{filesize}`  
⏰ Duration: `{duration}`
"""

STICKER_TXT = """
<b>
⚝ Command : /stickerid

Use this command to find any sticker ID. (For developers) 👨🏻‍💻
</b>
"""

TELEGRAPH_TXT = """
<b>
⚝ Usage : /telegraph

Reply with /telegraph on a picture or video under (5MB) to get a link like this 👇🏻

https://envs.sh/Fyw.jpg
</b>
"""

RESTRICTED_TXT = """
>💡 **Restricted Content Saver**                
1. 🔒 **Private Chats**
➥ Currently not working. 🙁

2. 🌐 **Public Chats**
➥ Simply share the post link. I'll download it for you.

3. 📂 **Batch Mode**
➥ Download multiple posts using this format:
> https://t.me/xxxx/1001-1010
"""

MERGER_TXT = """
> **📜 PDF Merging :**\n\n
• /merge - Start merging process\n
• Upload PDFs or Images in sequence\n
• /done : Merge all PDFs\n\n
> **⚠ Limitations : **\n
• Max File Size: 500 MB\n
• Max Files per Merge: 20\n\n
> **✨ Customizations :**\n
• Filename: Provide a custom name\n
• Thumbnail: Use (Filename) -t (Thumbnail link)
"""

REQUEST_TXT = """
> **⚙️ Join Request Acceptor**\n\n
**• I can accept all pending join requests in your channel. **🤝\n\n
**• Promote @Axa_bachha and @Z900_RoBot with full admin rights in your channel. **🔑\n\n
**• Send /accept command in the channel to accept all requests at once. 💯**
"""

