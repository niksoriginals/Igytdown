import os
import yt_dlp
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # Railway me BOT_TOKEN env set karna hoga


# ---------------- VIDEO DOWNLOADER ----------------
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please send a link.\n\nUsage: /d <link>")
        return

    url = context.args[0]
    await update.message.reply_text("⬇️ Downloading video...")

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")

        with open(filename, "rb") as f:
            await update.message.reply_video(InputFile(f, filename=os.path.basename(filename)),
                                             caption=info.get("title", ""))

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# ---------------- MUSIC DOWNLOADER ----------------
async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please send a song name or link.\n\nUsage: /song <name or link>")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🎵 Fetching: {query}")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": "music.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".m4a")

        with open(filename, "rb") as f:
            await update.message.reply_audio(InputFile(f, filename=os.path.basename(filename)),
                                             title=info.get("title", ""),
                                             performer=info.get("uploader", ""))

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Use:\n"
        "🎬 /d <link> → Download video\n"
        "🎵 /song <name or link> → Download music\n"
    )


# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("d", download_video))
    app.add_handler(CommandHandler("song", download_song))

    app.run_polling()


if __name__ == "__main__":
    main()
