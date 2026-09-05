import os
import sqlite3
import random
from pathlib import Path

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)

# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = os.environ["BOT_TOKEN"]

WEBHOOK_BASE_URL = os.environ["WEBHOOK_BASE_URL"].rstrip("/")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

DB = Path("quiz.db")

bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ),
)

dp = Dispatcher()
app = FastAPI()


# =========================
# ВОПРОСЫ
# =========================

QUESTIONS = {

    "minecraft": [
        {
            "q": "Какой моб взрывается рядом с игроком?",
            "options": ["Крипер", "Скелет", "Зомби", "Паук"],
            "answer": 0,
        },
        {
            "q": "Как называется измерение с лавой и крепостями?",
            "options": ["Энд", "Незер", "Лунный мир", "Пустошь"],
            "answer": 1,
        },
        {
            "q": "Какой предмет нужен для создания верстака?",
            "options": ["Камень", "Железо", "Доски", "Алмазы"],
            "answer": 2,
        },
        {
            "q": "Какой моб стреляет из лука?",
            "options": ["Скелет", "Крипер", "Корова", "Железный голем"],
            "answer": 0,
        },
        {
            "q": "Что нужно для создания алмазной кирки?",
            "options": ["2 алмаза", "3 алмаза", "4 алмаза", "5 алмазов"],
            "answer": 1,
        },
        {
            "q": "Как называется главный босс в Энде?",
            "options": ["Иссушитель", "Дракон Края", "Страж", "Варден"],
            "answer": 1,
        },
        {
            "q": "Какой моб появляется из яйца дракона?",
            "options": ["Крипер", "Никто", "Дракон", "Варден"],
            "answer": 1,
        },
        {
            "q": "Какой ресурс нужен для факела?",
            "options": ["Уголь", "Алмаз", "Золото", "Редстоун"],
            "answer": 0,
        },
        {
            "q": "Как называется зелёный моб Minecraft?",
            "options": ["Крипер", "Слизень", "Зомби", "Скелет"],
            "answer": 0,
        },
        {
            "q": "Сколько блоков обсидиана нужно минимум для обычного портала в Незер?",
            "options": ["8", "10", "12", "14"],
            "answer": 1,
        },
    ],

    "roblox": [
        {
            "q": "Что такое Roblox?",
            "options": [
                "Платформа с играми",
                "Только одна игра",
                "Мессенджер",
                "Браузер"
            ],
            "answer": 0,
        },
        {
            "q": "Как называется внутриигровая валюта Roblox?",
            "options": ["Coins", "Robux", "R Coins", "Bucks"],
            "answer": 1,
        },
        {
            "q": "Как называется персонаж игрока?",
            "options": ["Avatar", "Hero", "Player", "Skin"],
            "answer": 0,
        },
        {
            "q": "Можно ли создавать собственные игры в Roblox?",
            "options": ["Да", "Нет", "Только админам", "Только на телефоне"],
            "answer": 0,
        },
        {
            "q": "Как называется программа для создания игр Roblox?",
            "options": [
                "Roblox Studio",
                "Roblox Maker",
                "Game Studio",
                "Roblox Builder"
            ],
            "answer": 0,
        },
        {
            "q": "Что можно купить за Robux?",
            "options": [
                "Предметы и аксессуары",
                "Настоящий автомобиль",
                "Еду",
                "Телефон"
            ],
            "answer": 0,
        },
        {
            "q": "Можно ли играть в Roblox с друзьями?",
            "options": ["Да", "Нет", "Только ночью", "Только на ПК"],
            "answer": 0,
        },
        {
            "q": "Как называется популярная игра Roblox про питомцев?",
            "options": [
                "Adopt Me!",
                "Pet World",
                "Animal Life",
                "Pets Online"
            ],
            "answer": 0,
        },
        {
            "q": "Что такое obby в Roblox?",
            "options": [
                "Полоса препятствий",
                "Оружие",
                "Персонаж",
                "Валюта"
            ],
            "answer": 0,
        },
        {
            "q": "На каких устройствах можно играть в Roblox?",
            "options": [
                "Только ПК",
                "Только телефон",
                "На разных устройствах",
                "Только Xbox"
            ],
            "answer": 2,
        },
    ],

    "brawl_stars": [
        {
            "q": "Как называется валюта для покупки некоторых предметов в Brawl Stars?",
            "options": ["Гемы", "Робуксы", "Монеты мира", "Кристаллы"],
            "answer": 0,
        },
        {
            "q": "Как называется персонаж в Brawl Stars?",
            "options": ["Боец", "Герой", "Воин", "Игрок"],
            "answer": 0,
        },
        {
            "q": "Кто стреляет из лука?",
            "options": ["Бо", "Шелли", "Булл", "Эль Примо"],
            "answer": 0,
        },
        {
            "q": "Как называется режим с кристаллами?",
            "options": [
                "Захват кристаллов",
                "Ограбление",
                "Нокаут",
                "Броулбол"
            ],
            "answer": 0,
        },
        {
            "q": "Какой боец использует бейсбольную биту?",
            "options": ["Биби", "Шелли", "Пайпер", "Нита"],
            "answer": 0,
        },
        {
            "q": "Какой боец связан с медведем?",
            "options": ["Нита", "Кольт", "Бо", "Дэррил"],
            "answer": 0,
        },
        {
            "q": "Как называется режим с футбольным мячом?",
            "options": ["Броулбол", "Футбол Бравлеров", "Гол", "Мяч"],
            "answer": 0,
        },
        {
            "q": "Кто использует дробовик?",
            "options": ["Шелли", "Спайк", "Леон", "Сэнди"],
            "answer": 0,
        },
        {
            "q": "Как называется особая способность бойца?",
            "options": ["Супер", "Мега", "Ульта", "Бонус"],
            "answer": 0,
        },
        {
            "q": "Какой боец умеет становиться невидимым с помощью Супера?",
            "options": ["Леон", "Булл", "Джесси", "Пэм"],
            "answer": 0,
        },
    ],

    "sport": [
        {
            "q": "Сколько игроков одной команды находится на поле в футболе?",
            "options": ["9", "10", "11", "12"],
            "answer": 2,
        },
        {
            "q": "Сколько колец у Олимпийского символа?",
            "options": ["4", "5", "6", "7"],
            "answer": 1,
        },
        {
            "q": "Как называется площадка для баскетбола?",
            "options": ["Поле", "Корт", "Трек", "Ринг"],
            "answer": 1,
        },
        {
            "q": "Сколько периодов в хоккейном матче?",
            "options": ["2", "3", "4", "5"],
            "answer": 1,
        },
        {
            "q": "Какой спорт связан с ракеткой и воланом?",
            "options": ["Теннис", "Бадминтон", "Хоккей", "Гольф"],
            "answer": 1,
        },
        {
            "q": "Как называется человек, который защищает ворота в футболе?",
            "options": ["Защитник", "Вратарь", "Капитан", "Нападающий"],
            "answer": 1,
        },
        {
            "q": "Сколько очков обычно даёт штрафной бросок в баскетболе?",
            "options": ["1", "2", "3", "4"],
            "answer": 0,
        },
        {
            "q": "В каком виде спорта используют перчатки и ринг?",
            "options": ["Бокс", "Плавание", "Волейбол", "Лёгкая атлетика"],
            "answer": 0,
        },
        {
            "q": "Как называется бег на 42 км 195 м?",
            "options": ["Спринт", "Марафон", "Эстафета", "Кросс"],
            "answer": 1,
        },
        {
            "q": "Какой мяч используют в волейболе?",
            "options": ["Овальный", "Круглый", "Тяжёлый металлический", "Маленький теннисный"],
            "answer": 1,
        },
    ],

    "space": [
        {
            "q": "Какая звезда находится ближе всего к Земле?",
            "options": ["Сириус", "Солнце", "Полярная звезда", "Вега"],
            "answer": 1,
        },
        {
            "q": "Какая планета известна своими кольцами?",
            "options": ["Марс", "Венера", "Сатурн", "Меркурий"],
            "answer": 2,
        },
        {
            "q": "На какой планете мы живём?",
            "options": ["Марс", "Земля", "Юпитер", "Венера"],
            "answer": 1,
        },
        {
            "q": "Какая планета самая большая в Солнечной системе?",
            "options": ["Сатурн", "Земля", "Юпитер", "Нептун"],
            "answer": 2,
        },
        {
            "q": "Как называется спутник Земли?",
            "options": ["Луна", "Фобос", "Европа", "Титан"],
            "answer": 0,
        },
        {
            "q": "Какая планета находится ближе всего к Солнцу?",
            "options": ["Венера", "Марс", "Меркурий", "Земля"],
            "answer": 2,
        },
        {
            "q": "Как называется наша галактика?",
            "options": [
                "Андромеда",
                "Млечный Путь",
                "Большое Магелланово Облако",
                "Северная Галактика"
            ],
            "answer": 1,
        },
        {
            "q": "Какая планета известна как Красная планета?",
            "options": ["Марс", "Венера", "Уран", "Нептун"],
            "answer": 0,
        },
        {
            "q": "Что такое астероид?",
            "options": [
                "Космическое тело",
                "Звезда",
                "Планета",
                "Галактика"
            ],
            "answer": 0,
        },
        {
            "q": "Как называется аппарат, который отправляют исследовать космос?",
            "options": ["Робот-зонд", "Подводная лодка", "Танк", "Поезд"],
            "answer": 0,
        },
    ],
}


# =========================
# НАЗВАНИЯ КАТЕГОРИЙ
# =========================

CATEGORY_NAMES = {
    "minecraft": "⛏ Minecraft",
    "roblox": "🎮 Roblox",
    "brawl_stars": "⭐ Brawl Stars",
    "sport": "⚽ Спорт",
    "space": "🚀 Космос",
}


# =========================
# БАЗА
# =========================

def init_db():

    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            games INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            questions INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_player(user_id, username=""):

    conn = sqlite3.connect(DB)

    row = conn.execute(
        """
        SELECT
            user_id,
            username,
            games,
            correct,
            questions,
            best_score
        FROM players
        WHERE user_id=?
        """,
        (user_id,),
    ).fetchone()

    if not row:

        conn.execute(
            """
            INSERT INTO players
            (
                user_id,
                username
            )
            VALUES (?, ?)
            """,
            (
                user_id,
                username,
            ),
        )

        conn.commit()

        row = conn.execute(
            """
            SELECT
                user_id,
                username,
                games,
                correct,
                questions,
                best_score
            FROM players
            WHERE user_id=?
            """,
            (user_id,),
        ).fetchone()

    conn.close()

    return row


def update_stats(
    user_id,
    correct,
    questions,
    score,
):

    conn = sqlite3.connect(DB)

    row = conn.execute(
        """
        SELECT games, correct, questions, best_score
        FROM players
        WHERE user_id=?
        """,
        (user_id,),
    ).fetchone()

    games = row[0] + 1
    total_correct = row[1] + correct
    total_questions = row[2] + questions
    best_score = max(row[3], score)

    conn.execute(
        """
        UPDATE players
        SET
            games=?,
            correct=?,
            questions=?,
            best_score=?
        WHERE user_id=?
        """,
        (
            games,
            total_correct,
            total_questions,
            best_score,
            user_id,
        ),
    )

    conn.commit()
    conn.close()


# =========================
# КЛАВИАТУРЫ
# =========================

def main_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Играть",
                    callback_data="play",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Моя статистика",
                    callback_data="stats",
                )
            ],
        ]
    )


def categories_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⛏ Minecraft",
                    callback_data="cat:minecraft",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎮 Roblox",
                    callback_data="cat:roblox",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Brawl Stars",
                    callback_data="cat:brawl_stars",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚽ Спорт",
                    callback_data="cat:sport",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚀 Космос",
                    callback_data="cat:space",
                )
            ],
        ]
    )


def answer_keyboard(question):

    buttons = []

    for i, option in enumerate(question["options"]):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=option,
                    callback_data=f"answer:{i}",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def after_game_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Играть снова",
                    callback_data="play",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="stats",
                )
            ],
        ]
    )


# =========================
# ВРЕМЕННАЯ ПАМЯТЬ ИГР
# =========================

games = {}


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: types.Message):

    get_player(
        message.from_user.id,
        message.from_user.username or "",
    )

    await message.answer(
        "<b>🎮 Викторина</b>\n\n"
        "Проверь свои знания и набери максимум очков!\n\n"
        "Выбирай категорию и начинай игру.",
        reply_markup=main_keyboard(),
    )


# =========================
# CALLBACK
# =========================

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):

    data = callback.data
    user_id = callback.from_user.id

    # -------------------------
    # ИГРАТЬ
    # -------------------------

    if data == "play":

        await callback.message.edit_text(
            "<b>Выбери категорию:</b>",
            reply_markup=categories_keyboard(),
        )

        await callback.answer()

        return

    # -------------------------
    # СТАТИСТИКА
    # -------------------------

    if data == "stats":

        row = get_player(
            user_id,
            callback.from_user.username or "",
        )

        (
            _,
            _,
            games_count,
            correct,
            questions_count,
            best_score,
        ) = row

        if questions_count:

            percent = round(
                correct / questions_count * 100
            )

        else:

            percent = 0

        await callback.message.edit_text(
            "<b>📊 Твоя статистика</b>\n\n"
            f"🎮 Игр: {games_count}\n"
            f"❓ Вопросов: {questions_count}\n"
            f"✅ Правильных ответов: {correct}\n"
            f"🎯 Точность: {percent}%\n"
            f"🏆 Лучший результат: {best_score} / 100",
            reply_markup=main_keyboard(),
        )

        await callback.answer()

        return

    # -------------------------
    # КАТЕГОРИЯ
    # -------------------------

    if data.startswith("cat:"):

        category = data.split(":", 1)[1]

        selected = random.sample(
            QUESTIONS[category],
            10,
        )

        games[user_id] = {
            "category": category,
            "questions": selected,
            "current": 0,
            "score": 0,
            "correct": 0,
        }

        await send_question(
            callback.message,
            user_id,
        )

        await callback.answer()

        return

    # -------------------------
    # ОТВЕТ
    # -------------------------

    if data.startswith("answer:"):

        game = games.get(user_id)

        if not game:

            await callback.answer(
                "Начни новую игру",
                show_alert=True,
            )

            return

        question = game["questions"][
            game["current"]
        ]

        answer = int(
            data.split(":")[1]
        )

        if answer == question["answer"]:

            game["correct"] += 1
            game["score"] += 10

            result = (
                "✅ <b>Правильно!</b>"
            )

        else:

            correct_answer = question["options"][
                question["answer"]
            ]

            result = (
                "❌ <b>Неправильно!</b>\n"
                f"Правильный ответ: "
                f"<b>{correct_answer}</b>"
            )

        game["current"] += 1

        if game["current"] >= 10:

            update_stats(
                user_id,
                game["correct"],
                10,
                game["score"],
            )

            score = game["score"]
            correct_count = game["correct"]

            if score >= 90:

                message = "🔥 Невероятный результат!"

            elif score >= 70:

                message = "🏆 Отличная игра!"

            elif score >= 50:

                message = "👍 Неплохо!"

            else:

                message = "💪 В следующий раз будет лучше!"

            await callback.message.edit_text(
                f"{result}\n\n"
                "<b>🏁 Игра закончена!</b>\n\n"
                f"Правильных ответов: "
                f"<b>{correct_count}/10</b>\n"
                f"Очки: <b>{score}/100</b>\n\n"
                f"{message}",
                reply_markup=after_game_keyboard(),
            )

            del games[user_id]

            await callback.answer()

            return

        await callback.message.edit_text(
            f"{result}\n\n"
            "Следующий вопрос...",
        )

        await send_question(
            callback.message,
            user_id,
            delay_text=True,
        )

        await callback.answer()

        return


# =========================
# ОТПРАВКА ВОПРОСА
# =========================

async def send_question(
    message,
    user_id,
    delay_text=False,
):

    game = games[user_id]

    question = game["questions"][
        game["current"]
    ]

    number = game["current"] + 1

    category = CATEGORY_NAMES[
        game["category"]
    ]

    await message.edit_text(
        f"<b>{category}</b>\n\n"
        f"❓ <b>Вопрос {number}/10</b>\n\n"
        f"{question['q']}\n\n"
        f"⭐ Очки: {game['score']}",
        reply_markup=answer_keyboard(question),
    )


# =========================
# STARTUP
# =========================

@app.on_event("startup")
async def startup():

    init_db()

    await bot.set_webhook(
        WEBHOOK_BASE_URL + WEBHOOK_PATH
    )


# =========================
# SHUTDOWN
# =========================

@app.on_event("shutdown")
async def shutdown():

    await bot.delete_webhook()

    await bot.session.close()


# =========================
# WEBHOOK
# =========================

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):

    data = await request.json()

    update = Update.model_validate(
        data,
        context={"bot": bot},
    )

    await dp.feed_update(
        bot,
        update,
    )

    return {
        "ok": True
    }


# =========================
# HEALTH
# =========================

@app.get("/")
async def health():

    return {
        "status": "ok"
    }


# =========================
# ЛОКАЛЬНЫЙ ЗАПУСК
# =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "10000",
            )
        ),
    )
