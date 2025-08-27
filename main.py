import os
from pathlib import Path
import yt_dlp
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Railway env me set karna hoga

# max 50MB (Telegram limit)
MAX_BYTES = 50 * 1024 * 1024  

TEMP_DIR = Path("downloads")
TEMP_DIR.mkdir(exist_ok=True)

SUPPORTED_SITES = ["youtube.com", "youtu.be", "instagram.com", "instagr.am"]

def is_supported(url: str) -> bool:
    return any(s in url.lower() for s in SUPPORTED_SITES)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube or Instagram link 🔗")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_supported(url):
        await update.message.reply_text("❌ Only YouTube and Instagram supported.")
        return

    user_dir = TEMP_DIR / str(update.effective_user.id)
    user_dir.mkdir(exist_ok=True)

    try:
        opts = {
            "outtmpl": str(user_dir / "%(title).70s.%(ext)s"),
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file = Path(filename)

        if file.stat().st_size > MAX_BYTES:
            await update.message.reply_text(
                f"❌ File too large ({round(file.stat().st_size/1024/1024,1)} MB)."
            )
        else:
            await update.message.reply_video(
                video=InputFile(file, filename=file.name),
                caption=info.get("title", "")
            )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")
    finally:
        for f in user_dir.glob("*"):
            f.unlink()
        user_dir.rmdir()

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))
    app.run_polling()

if __name__ == "__main__":
    main()
