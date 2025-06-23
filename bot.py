import logging
import subprocess
import aiohttp
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OVERLAY_TEXT = os.getenv("OVERLAY_TEXT", "Streamed by @M3U8toRTMPBot")

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Use /stream <m3u8_link> <rtmp_url> <stream_key> to start streaming."
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
    args = context.args
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

    await update.message.reply_text("Starting stream...")

    try:
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", m3u8_url,
            "-i", "logo.png",
            "-filter_complex", f"drawtext=text='{OVERLAY_TEXT}':fontfile=/usr/share/fonts/dejavu/DejaVuSans.ttf:fontsize=20:fontcolor=black:box=1:boxcolor=white@0.5:x=10:y=10,overlay=W-w-10:H-h-10",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-c:a", "aac",
            "-f", "flv",
            full_rtmp_url
        ]
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        context.user_data['ffmpeg_process'] = process
        await update.message.reply_text(f"Streaming to {full_rtmp_url}. Use /stop to end.")
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        await update.message.reply_text("Failed to start stream.")

async def stop_stream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    process = context.user_data.get('ffmpeg_process')
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
            await update.message.reply_text("Stream stopped.")
        except subprocess.TimeoutExpired:
            process.kill()
            await update.message.reply_text("Stream forcefully stopped.")
        finally:
            context.user_data.pop('ffmpeg_process', None)
    else:
        await update.message.reply_text("No active stream.")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stream", stream_to_rtmp))
    application.add_handler(CommandHandler("stop", stop_stream))
    application.run_polling()

if __name__ == "__main__":
    main()
