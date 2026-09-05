import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
CHANNEL_ID = os.environ["CHANNEL_ID"]
WEBHOOK_BASE_URL = os.environ["WEBHOOK_BASE_URL"].rstrip("/")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

DB = Path("news.db")
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = FastAPI()


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            file_id TEXT,
            file_type TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()


def save_submission(message: types.Message):
    conn = sqlite3.connect(DB)
    cur = conn.execute(
        """INSERT INTO submissions
           (user_id, username, text, file_id, file_type)
           VALUES (?, ?, ?, ?, ?)""",
        (
            message.from_user.id,
            message.from_user.username or "",
            message.caption or message.text or "",
            get_file_id(message),
            get_file_type(message),
        ),
    )
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid


def get_file_id(message):
    if message.photo:
        return message.photo[-1].file_id
    if message.video:
        return message.video.file_id
    if message.document:
        return message.document.file_id
    return None


def get_file_type(message):
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.document:
        return "document"
    return None


def get_submission(sid):
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT id,user_id,username,text,file_id,file_type,status "
        "FROM submissions WHERE id=?",
        (sid,),
    ).fetchone()
    conn.close()
    return row


def set_status(sid, status):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE submissions SET status=? WHERE id=?", (status, sid))
    conn.commit()
    conn.close()


def buttons(sid):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"publish:{sid}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{sid}")
    ]])


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "<b>Купи-Продай — предложить публикацию</b>\n\n"
        "Пришли текст, фото, видео или объявление. "
        "Материал сначала попадёт на модерацию."
    )


@dp.message()
async def receive(message: types.Message):
    sid = save_submission(message)
    username = f"@{message.from_user.username}" if message.from_user.username else "без username"
    text = message.caption or message.text or ""
    header = f"<b>📰 Новая заявка #{sid}</b>\nОт: {username}\n\n{text}"

    file_id = get_file_id(message)
    file_type = get_file_type(message)

    if file_type == "photo":
        await bot.send_photo(ADMIN_ID, file_id, caption=header[:1024],
                             reply_markup=buttons(sid))
    elif file_type == "video":
        await bot.send_video(ADMIN_ID, file_id, caption=header[:1024],
                             reply_markup=buttons(sid))
    elif file_type == "document":
        await bot.send_document(ADMIN_ID, file_id, caption=header[:1024],
                                reply_markup=buttons(sid))
    else:
        await bot.send_message(ADMIN_ID, header, reply_markup=buttons(sid))

    await message.answer(
        "Спасибо! Материал отправлен на модерацию."
    )


@dp.callback_query()
async def moderate(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    action, sid_text = callback.data.split(":")
    sid = int(sid_text)
    row = get_submission(sid)

    if not row or row[-1] != "pending":
        await callback.answer("Заявка уже обработана")
        return

    _, _, _, text, file_id, file_type, _ = row

    if action == "reject":
        set_status(sid, "rejected")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Отклонено")
        return

    try:
        if file_type == "photo":
            await bot.send_photo(CHANNEL_ID, file_id, caption=text[:1024] if text else None)
        elif file_type == "video":
            await bot.send_video(CHANNEL_ID, file_id, caption=text[:1024] if text else None)
        elif file_type == "document":
            await bot.send_document(CHANNEL_ID, file_id, caption=text[:1024] if text else None)
        else:
            await bot.send_message(CHANNEL_ID, text)

        set_status(sid, "published")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Опубликовано")
    except Exception:
        await callback.answer(
            "Ошибка публикации. Проверь права бота в канале и CHANNEL_ID.",
            show_alert=True
        )


@app.on_event("startup")
async def startup():
    init_db()
    await bot.set_webhook(WEBHOOK_BASE_URL + WEBHOOK_PATH)


@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()
    await bot.session.close()


@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
