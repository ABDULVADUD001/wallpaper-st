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
    CallbackQueryHandler,
    ContextTypes,
    filters
)


TOKEN = os.getenv("BOT_TOKEN")

WEB_APP_URL = "https://abdulvadud001.github.io/wallpaper-st/"


# =========================
# START
# =========================

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
                web_app=WebAppInfo(
                    url=WEB_APP_URL
                )
            )
        ]
    ]

    await update.message.reply_text(
        "🌟 Anime & Wallpaper Bot'ga xush kelibsiz!\n\n"
        "🔍 Anime qidirish uchun tugmani bosing.\n"
        "🖼 Wallpaperlarni ko‘rish uchun Wallpaper App'ni oching.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# ANIME SEARCH BUTTON
# =========================

async def anime_search_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        "🔍 Anime nomini yozing.\n\n"
        "Masalan:\n"
        "• Naruto\n"
        "• One Piece\n"
        "• Solo Leveling\n"
        "• Bleach\n"
        "• Demon Slayer"
    )


# =========================
# SEARCH ANIME
# =========================

async def search_anime(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    anime_name = update.message.text.strip()

    if len(anime_name) < 2:
        await update.message.reply_text(
            "❌ Anime nomini to‘liqroq yozing."
        )
        return

    loading = await update.message.reply_text(
        "🔎 Anime qidirilmoqda..."
    )

    url = "https://api.jikan.moe/v4/anime"

    params = {
        "q": anime_name,
        "limit": 5,
        "sfw": "true"
    }

    try:

        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                params=params
            ) as response:

                print("Jikan status:", response.status)

                if response.status == 429:
                    await loading.edit_text(
                        "⏳ Juda ko‘p so‘rov yuborildi.\n"
                        "10-20 soniyadan keyin yana urinib ko‘ring."
                    )
                    return

                if response.status != 200:

                    error_text = await response.text()

                    print(
                        "Jikan API xatosi:",
                        response.status,
                        error_text
                    )

                    await loading.edit_text(
                        f"❌ Anime serverida xatolik.\n"
                        f"Status: {response.status}"
                    )

                    return

                result = await response.json()

        anime_list = result.get("data", [])

        if not anime_list:

            await loading.edit_text(
                "😕 Anime topilmadi.\n\n"
                "Boshqa nom bilan urinib ko‘ring."
            )

            return

        await loading.delete()

        # Faqat 5 ta natija
        for anime in anime_list[:5]:

            title = anime.get(
                "title",
                "Noma'lum"
            )

            title_english = anime.get(
                "title_english"
            )

            score = anime.get("score")
            episodes = anime.get("episodes")

            year = anime.get("year")

            if not year:

                aired = anime.get("aired", {})

                from_date = aired.get(
                    "from"
                )

                if from_date:
                    year = from_date[:4]

            synopsis = anime.get(
                "synopsis"
            )

            if synopsis:
                synopsis = synopsis[:400]

                if len(anime.get("synopsis", "")) > 400:
                    synopsis += "..."

            else:
                synopsis = "Ma'lumot mavjud emas."

            image_url = (
                anime
                .get("images", {})
                .get("jpg", {})
                .get("large_image_url")
            )

            mal_url = anime.get("url")

            text = (
                f"🎬 {title}\n\n"
            )

            if title_english and title_english != title:
                text += (
                    f"🇬🇧 {title_english}\n\n"
                )

            text += (
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

            keyboard = (
                InlineKeyboardMarkup(buttons)
                if buttons
                else None
            )

            if image_url:

                try:

                    await update.message.reply_photo(
                        photo=image_url,
                        caption=text,
                        reply_markup=keyboard
                    )

                except Exception as image_error:

                    print(
                        "Rasm yuborish xatosi:",
                        image_error
                    )

                    await update.message.reply_text(
                        text,
                        reply_markup=keyboard
                    )

            else:

                await update.message.reply_text(
                    text,
                    reply_markup=keyboard
                )

    except aiohttp.ClientError as e:

        print(
            "Internet/API xatosi:",
            e
        )

        try:
            await loading.edit_text(
                "❌ Anime serveriga ulanib bo‘lmadi.\n"
                "Birozdan keyin yana urinib ko‘ring."
            )
        except:
            pass

    except Exception as e:

        print(
            "Anime Search xatosi:",
            repr(e)
        )

        try:
            await loading.edit_text(
                "❌ Kutilmagan xatolik yuz berdi."
            )
        except:
            pass


# =========================
# MAIN
# =========================

def main():

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # 🔍 Anime Search tugmasi
    app.add_handler(
        CallbackQueryHandler(
            anime_search_button,
            pattern="^anime_search$"
        )
    )

    # Anime nomini qabul qilish
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
