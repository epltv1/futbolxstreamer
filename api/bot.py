import logging
import os
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from http import HTTPStatus
import json

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OVERLAY_TEXT = os.getenv("OVERLAY_TEXT", "Streamed by @M3U8toRTMPBot")

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

async def apply_overlays(m3u8_url: str) -> str:
    # Placeholder: Fetch a sample frame (e.g., via external API or static image)
    # For simplicity, create a blank image with overlays
    try:
        img = Image.new('RGB', (640, 360), color='black')
        draw = ImageDraw.Draw(img)
        
        # Add text overlay
        font = ImageFont.load_default()  # Use default font
        draw.text((10, 10), OVERLAY_TEXT, fill='white')
        
        # Add logo overlay
        logo = Image.open('logo.png').convert('RGBA')
        logo = logo.resize((100, 100))
        img.paste(logo, (540, 260), logo)  # Bottom-right
        
        # Save to temporary file
        output_path = '/tmp/output.jpg'
        img.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error applying overlays: {e}")
        return None

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

    # Apply overlays and get output
    output_path = await apply_overlays(m3u8_url)
    if not output_path:
        await update.message.reply_text("Failed to apply overlays.")
        return

    await update.message.reply_text(
        f"Overlays applied. Stream to {full_rtmp_url} manually using FFmpeg on your RTMP server:\n"
        f"ffmpeg -i {m3u8_url} -i {output_path} -filter_complex overlay=10:10 -c:v libx264 -c:a aac -f flv {full_rtmp_url}"
    )

async def webhook(request):
    try:
        # Initialize the application
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("stream", stream_to_rtmp))

        # Parse the incoming request
        update = Update.de_json(await request.get_json(force=True), application.bot)
        await application.process_update(update)

        return {
            "statusCode": HTTPStatus.OK,
            "body": json.dumps({"message": "Update processed"})
        }
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "body": json.dumps({"error": str(e)})
        }
