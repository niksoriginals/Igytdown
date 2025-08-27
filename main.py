import os
import logging
import asyncio
from pathlib import Path
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Telegram Bot Token (Railway me env variable set karo)
TOKEN = os.getenv("BOT_TOKEN")

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 Send me a YouTube or Instagram link 🔗")

# Download function
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("⚠️ Invalid link.")
        return

    user_dir = DOWNLOAD_DIR / str(update.message.from_user.id)
    user_dir.mkdir(exist_ok=True)

    opts = {
        "outtmpl": str(user_dir / "%(title).70s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        loop = asyncio.get_event_loop()
        def _download():
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info), info

        file_path, info = await loop.run_in_executor(None, _download)
        file = Path(file_path)

        # Send file to user
        with open(file, "rb") as f:
            await update.message.reply_video(
                video=InputFile(f, filename=file.name),
                caption=info.get("title", "")
            )

        # Cleanup
        file.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text(f"⚠️ Error: {e}")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == "__main__":
    main()
