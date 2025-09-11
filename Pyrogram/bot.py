import os
import aiohttp
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from YourApp import app  # Import your Pyrogram Client

# Publicly visible web server
UPLOAD_URL = f"https://endtrz.vercel.app/api/upload"


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
    """Reply to a file with /tgm to upload and get link"""
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Please reply to a file to upload.")

    replied = message.reply_to_message
    if not (replied.document or replied.photo or replied.video):
        return await message.reply_text("⚠️ Only documents, photos, or videos are supported.")

    status = await message.reply_text("⬆️ Uploading file to server...")

    try:
        # Download the file
        file_path = await replied.download()
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
                [
                    InlineKeyboardButton("🌍 Open Link", url=file_link)
                ]
            ])

            await status.edit_text(
                caption,
                reply_markup=buttons,
                disable_web_page_preview=False
            )
        else:
            await status.edit_text("❌ Upload failed. Please try again.")

        # Clean up temp file
        os.remove(file_path)

    except Exception as e:
        await status.edit_text(f"⚠️ Error: {str(e)}")
