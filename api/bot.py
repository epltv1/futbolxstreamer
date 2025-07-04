import logging
import os
import aiohttp
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Use /stream <m3u8_link> <rtmp_url> <stream_key> to get an FFmpeg streaming command."
    )

async def validate_m3u8(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=5) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Error validating M3U8 URL: {e}")
        return False

async def stream_to_rtmp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = update.message.text.split()[1:]
    if len(args) != 3:
        await update.message.reply_text(
            "Usage: /stream <m3u8_link> <rtmp_url> <stream_key>\n"
            "Example: /stream https://example.com/playlist.m3u8 rtmp://a.rtmp.youtube.com/live2 my-key"
        )
        return

    m3u8_url, rtmp_base_url, stream_key = args
    full_rtmp_url = f"{rtmp_base_url}/{stream_key}"

    if not await validate_m3u8(m3u8_url):
        await update.message.reply_text("Invalid M3U8 URL. Please try again.")
        return

    ffmpeg_command = (
        f"ffmpeg -i {m3u8_url} -c:v copy -c:a aac -f flv {full_rtmp_url}"
    )
    await update.message.reply_text(
        f"Run this command on a server with FFmpeg to stream:\n{ffmpeg_command}"
    )

@app.post("/api/bot")
async def webhook(request: Request):
    try:
        body = await request.json()
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("stream", stream_to_rtmp))
        update = Update.de_json(body, application.bot)
        if update:
            await application.process_update(update)
            return {"message": "Update processed"}
        else:
            return {"error": "Invalid update"}, 400
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {"error": str(e)}, 500
