import os
import logging
import asyncio
from pathlib import Path
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN")

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download directory
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 Use command:\n\n`/d <youtube/instagram link>`")

# /d command
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/d <link>`")
        return

    url = context.args[0]
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

        with open(file, "rb") as f:
            await update.message.reply_video(
                video=InputFile(f, filename=file.name),
                caption=info.get("title", "")
            )

        file.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Download error: {e}")
        await update.message.reply_text(f"⚠️ Error: {e}")

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("d", download_video))   # 👈 only /d command

    app.run_polling()

if __name__ == "__main__":
    main()
