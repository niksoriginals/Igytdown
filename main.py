import os
import yt_dlp
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes

# Apna bot token yaha daal
BOT_TOKEN = os.getenv("8370660490:AAHVgzyJOocunWNp8m7FMrOZOvXYszDX52w")


# ---------------- VIDEO DOWNLOADER ----------------
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /d <YouTube/Instagram link>")
        return

    url = context.args[0]
    await update.message.reply_text(f"📥 Downloading video...")

    ydl_opts = {
        "format": "mp4",
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "cachedir": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4")

        with open(filename, "rb") as f:
            await update.message.reply_video(
                video=InputFile(f, filename=os.path.basename(filename)),
                caption=info.get("title", "Video")
            )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# ---------------- MUSIC DOWNLOADER (FAST) ----------------
async def download_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /song <name or link>")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🎵 Fetching: {query}")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": "music.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "cachedir": False,
    }

    try:
        search_query = query if query.startswith("http") else f"ytsearch1:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)

            if "entries" in info:  # ytsearch case
                info = info["entries"][0]

            filename = ydl.prepare_filename(info).replace(".webm", ".m4a")

        with open(filename, "rb") as f:
            await update.message.reply_audio(
                InputFile(f, filename=os.path.basename(filename)),
                title=info.get("title", "Unknown Title"),
                performer=info.get("uploader", "Unknown Artist")
            )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")


# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("d", download_video))
    

    print("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
