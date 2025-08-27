import os
import logging
import asyncio
from pathlib import Path
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes

# === Bot Token ===
TOKEN = os.getenv("BOT_TOKEN")  # ya direct string de sakte ho

# === Logs ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Directories ===
DOWNLOAD_DIR = Path("downloads")
MUSIC_DIR = DOWNLOAD_DIR / "music"
VIDEO_DIR = DOWNLOAD_DIR / "video"

MUSIC_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 OG Downloader Bot Ready!\n\n"
        "Use:\n"
        "📹 `/d <link>` → Download video (YT/Insta)\n"
        "🎵 `/song <name or link>` → Download music (YT)"
    )

# === /d (video download) ===
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/d <YouTube/Instagram link>`")
        return

    url = context.args[0]
    user_dir = VIDEO_DIR / str(update.message.from_user.id)
    user_dir.mkdir(exist_ok=True)

    opts = {
        "format": "mp4/best",
        "outtmpl": str(user_dir / "%(title).70s.%(ext)s"),
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
                if "entries" in info:
                    info = info["entries"][0]
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
        logger.error(f"Video Error: {e}")
        await update.message.reply_text(f"⚠️ Error: {e}")

# === /song (music download) ===
async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/song <name or YouTube link>`")
        return

    query = " ".join(context.args)
    user_dir = MUSIC_DIR / str(update.message.from_user.id)
    user_dir.mkdir(exist_ok=True)

    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(user_dir / "%(title).70s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
    }

    try:
        loop = asyncio.get_event_loop()

        def _download():
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(query, download=True)
                if "entries" in info:
                    info = info["entries"][0]
                return ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3"), info

        file_path, info = await loop.run_in_executor(None, _download)
        file = Path(file_path)

        with open(file, "rb") as f:
            await update.message.reply_audio(
                audio=InputFile(f, filename=file.name),
                title=info.get("title", ""),
                performer=info.get("uploader", "Unknown")
            )

        file.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Song Error: {e}")
        await update.message.reply_text(f"⚠️ Error: {e}")

# === Main ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("d", download_video))
    app.add_handler(CommandHandler("song", download_song))

    app.run_polling()

if __name__ == "__main__":
    main()
