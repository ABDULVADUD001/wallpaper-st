import os
import aiohttp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

WEB_APP_URL = "https://abdulvadud001.github.io/wallpaper-st/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Anime Search",
                callback_data="anime_search"
            )
        ],
        [
            InlineKeyboardButton(
                "🖼 Wallpaper App",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]

    await update.message.reply_text(
        "🌟 *Anime & Wallpaper Bot*ga xush kelibsiz!\n\n"
        "🔍 Anime qidirish uchun tugmani bosing.\n"
        "🖼 Wallpaperlarni ko‘rish uchun Wallpaper App'ni oching.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def anime_search_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🔍 Anime nomini yozing.\n\n"
        "Masalan:\n"
        "• Naruto\n"
        "• One Piece\n"
        "• Solo Leveling\n"
        "• That Time I Got Reincarnated as a Slime"
    )


async def search_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime_name = update.message.text.strip()

    if len(anime_name) < 2:
        await update.message.reply_text(
            "❌ Anime nomini biroz to‘liqroq yozing."
        )
        return

    await update.message.reply_text(
        "🔎 Anime qidirilmoqda..."
    )

    url = "https://api.jikan.moe/v4/anime"

    params = {
        "q": anime_name,
        "limit": 5,
        "sfw": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:

            async with session.get(
                url,
                params=params,
                timeout=20
            ) as response:

                if response.status != 200:
                    await update.message.reply_text(
                        "❌ Anime qidirishda xatolik yuz berdi."
                    )
                    return

                result = await response.json()

        anime_list = result.get("data", [])

        if not anime_list:
            await update.message.reply_text(
                "😕 Anime topilmadi.\n"
                "Boshqa nom bilan urinib ko‘ring."
            )
            return

        for anime in anime_list:

            title = anime.get("title", "Noma'lum")

            score = anime.get("score")
            episodes = anime.get("episodes")
            year = anime.get("year")

            synopsis = anime.get("synopsis")

            if synopsis:
                synopsis = synopsis[:500]
                synopsis += "..."
            else:
                synopsis = "Ma'lumot mavjud emas."

            image_url = (
                anime.get("images", {})
                .get("jpg", {})
                .get("large_image_url")
            )

            mal_url = anime.get("url")

            text = (
                f"🎬 *{title}*\n\n"
                f"⭐ Reyting: {score or 'N/A'}\n"
                f"📺 Qismlar: {episodes or 'N/A'}\n"
                f"📅 Yil: {year or 'N/A'}\n\n"
                f"📝 {synopsis}"
            )

            buttons = []

            if mal_url:
                buttons.append([
                    InlineKeyboardButton(
                        "🌐 MyAnimeList",
                        url=mal_url
                    )
                ])

            if image_url:
                await update.message.reply_photo(
                    photo=image_url,
                    caption=text,
                    parse_mode="Markdown",
                    reply_markup=(
                        InlineKeyboardMarkup(buttons)
                        if buttons else None
                    )
                )
            else:
                await update.message.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=(
                        InlineKeyboardMarkup(buttons)
                        if buttons else None
                    )
                )

    except Exception as e:

        print("Anime Search xatosi:", e)

        await update.message.reply_text(
            "❌ Server bilan bog‘lanishda xatolik yuz berdi."
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^🔍 Anime Search$"),
            anime_search_button
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_anime
        )
    )

    print("Bot ishga tushdi...")

    app.run_polling()


if __name__ == "__main__":
    main()
