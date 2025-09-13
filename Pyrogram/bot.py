import os
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from YourApp import app  # Import your Pyrogram Client

# UPLOAD URL WITH API KEY
API_KEY = "" # get you api key from https://endtrz.vercel.app

UPLOAD_URL = f"https://endtrz.vercel.app/api/{API_KEY}/upload"


async def upload_to_server(file_path, file_name):
    """Upload file to Flask server via /api/upload"""
    async with aiohttp.ClientSession() as session:
        with open(file_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("file", f, filename=file_name)
            async with session.post(UPLOAD_URL, data=form) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return None


@app.on_message(filters.command("tgm"))
async def tgm_handler(_, message: Message):
    """Reply to any message with /tgm to upload and get link"""
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Please reply to a message to upload.")

    replied = message.reply_to_message
    status = await message.reply_text("⬆️ Uploading content to server...")

    file_path = None
    try:
        # Download media if exists, else save text to temp file
        if replied.media:
            file_path = await replied.download()
        else:
            file_path = "temp.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(replied.text or "No text content")

        file_name = os.path.basename(file_path)

        # Upload to Flask server
        result = await upload_to_server(file_path, file_name)

        if result and "url" in result:
            file_link = result["url"]

            caption = (
                f"➼ **Uploaded to [Endtrz]({file_link})**\n"
                f"➼ **Copy Link :** `{file_link}`"
            )

            # Inline buttons
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌍 Open Link", url=file_link)]
            ])

            await status.edit(
                caption,
                reply_markup=buttons,
                disable_web_page_preview=False
            )
        else:
            await status.edit("❌ Upload failed. Please try again.")

    except Exception as e:
        await status.edit(f"⚠️ Error: {str(e)}")

    finally:
        # Clean up temp file if exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
