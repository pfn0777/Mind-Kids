"""Mind Kids Telegram bot.

Opens the Mind Kids Mini App (37 brain-training games for kids 4-12) from
`/start` and the chat's Menu Button, and keeps a minimal, anonymous usage
count (`user_id` + timestamps only) for `/stats`.

Pattern copied from the Dunyo Hotel Mini App bot, which runs on the same
server (`Settings`/`load_settings`/`ConfigError`, `WelcomePhoto` file_id
cache, `build_dispatcher`, `main` with `drop_pending_updates`).
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    MenuButtonWebApp,
    User,
    WebAppInfo,
)
from dotenv import load_dotenv

import db

logger = logging.getLogger("mindkids_bot")

# Relative paths (WELCOME_PHOTO_PATH, DB_PATH) resolve against this file's
# directory, so the bot behaves the same run from bot/ or from /opt.
HERE = Path(__file__).resolve().parent
DEFAULT_WELCOME_PHOTO = "media/welcome.png"
DEFAULT_DB_PATH = "data/users.db"


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    token: str
    webapp_url: str
    admin_id: int
    welcome_photo: Path = HERE / DEFAULT_WELCOME_PHOTO
    db_path: Path = HERE / DEFAULT_DB_PATH


def load_settings() -> Settings:
    load_dotenv()

    def require(name: str) -> str:
        value = os.environ.get(name, "").strip()
        if not value:
            raise ConfigError(f"Missing required .env value: {name}")
        return value

    # Checked in the order an operator fills a fresh .env, so the first blank
    # line is what gets reported, not the third.
    token = require("BOT_TOKEN")

    url = require("WEBAPP_URL")
    if not url.startswith("https://"):
        raise ConfigError("WEBAPP_URL must be an https:// URL — Telegram rejects anything else")

    try:
        admin_id = int(require("ADMIN_ID"))
    except ValueError as exc:
        raise ConfigError("ADMIN_ID must be an integer") from exc

    photo = Path(os.environ.get("WELCOME_PHOTO_PATH", "").strip() or DEFAULT_WELCOME_PHOTO)
    if not photo.is_absolute():
        photo = HERE / photo
    # Checked here rather than at the first /start: a missing photo is an
    # operator mistake, and the deploy script's config check should catch it
    # before systemd starts a bot that greets every parent with a stack trace.
    if not photo.is_file():
        raise ConfigError(f"Welcome photo not found: {photo}")

    db_path = Path(os.environ.get("DB_PATH", "").strip() or DEFAULT_DB_PATH)
    if not db_path.is_absolute():
        db_path = HERE / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return Settings(
        token=token,
        webapp_url=url,
        admin_id=admin_id,
        welcome_photo=photo,
        db_path=db_path,
    )


TEXTS = {
    "uz": {
        # Caption of the welcome photo. Telegram caps a caption at 1024
        # characters; keep this comfortably under it.
        "welcome": (
            "🧠 Mind Kids — bolangiz uchun aqliy o‘yinlar!\n\n"
            "4 dan 12 yoshgacha bo‘lgan bolalar uchun 37 ta rivojlantiruvchi "
            "o‘yin: diqqat, xotira, mantiq va tezkor fikrlash.\n\n"
            "Boshlash uchun quyidagi tugmani bosing 👇"
        ),
        "open": "🧠 O'yinlarni ochish",
        "menu_button": "O'yinlarni ochish",
        "fallback": "Mind Kids o'yinlarini ochish uchun quyidagi tugmani bosing.",
        "stats": (
            "📊 Statistika\n\n"
            "Jami foydalanuvchilar: {total}\n"
            "Bugun qo'shilgan: {today}\n"
            "Oxirgi 7 kunda yangi: {new_7d}\n"
            "Oxirgi 7 kunda faol: {active_7d}"
        ),
    },
}
LANG = "uz"


def is_admin(user: User | None, admin_id: int) -> bool:
    return user is not None and user.id == admin_id


def open_app_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[LANG]["open"], web_app=WebAppInfo(url=webapp_url))]
        ]
    )


class WelcomePhoto:
    """Sends the welcome photo, reusing Telegram's `file_id` after the first upload.

    `/start` is the most-pressed thing in this bot, and re-uploading the same
    ~2 MB on every press is bandwidth spent for nothing. The id lives in
    memory only: a restart simply pays for one more upload.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._file_id: str | None = None

    async def send(self, message: Message, caption: str, markup: InlineKeyboardMarkup) -> bool:
        """True if the photo reached the user, False if both attempts failed."""
        if self._file_id is not None:
            try:
                await message.answer_photo(self._file_id, caption=caption, reply_markup=markup)
                return True
            except TelegramAPIError:
                # A cached id can stop working (Telegram expired it, the bot
                # was migrated). Drop it and fall through to a real upload
                # rather than greeting every user with nothing from here on.
                logger.warning("Cached welcome photo file_id rejected; re-uploading")
                self._file_id = None

        try:
            sent = await message.answer_photo(
                FSInputFile(self._path), caption=caption, reply_markup=markup
            )
        except TelegramAPIError:
            logger.exception("Could not send the welcome photo from %s", self._path)
            return False

        if sent.photo:
            self._file_id = sent.photo[-1].file_id
        return True


def build_dispatcher(settings: Settings) -> Dispatcher:
    dp = Dispatcher()
    welcome_photo = WelcomePhoto(settings.welcome_photo)

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        user = message.from_user
        if user is not None:
            try:
                await db.upsert_user(settings.db_path, user.id, datetime.now(timezone.utc))
            except Exception:
                # The greeting must go out even if the DB write fails — a kid
                # waiting for the button is not this bot's problem to solve
                # with an error message.
                logger.exception("Could not upsert user_id=%s", user.id)
        else:
            logger.warning("/start with no sender; skipping DB upsert")

        markup = open_app_keyboard(settings.webapp_url)
        caption = TEXTS[LANG]["welcome"]

        # The button rides on the photo. If the photo cannot be sent, the
        # same text goes out as a plain message — a user left without the
        # button has no way into the Mini App at all.
        if not await welcome_photo.send(message, caption, markup):
            await message.answer(caption, reply_markup=markup)

    @dp.message(Command("stats"), lambda message: is_admin(message.from_user, settings.admin_id))
    async def on_stats(message: Message) -> None:
        result = await db.stats(settings.db_path, datetime.now(timezone.utc))
        await message.answer(
            TEXTS[LANG]["stats"].format(
                total=result.total,
                today=result.today,
                new_7d=result.new_7d,
                active_7d=result.active_7d,
            )
        )

    # Registered last: aiogram matches handlers in registration order, so a
    # non-admin's /stats falls through here — it must never reveal the
    # command exists, so this is a plain fallback, not an "access denied".
    @dp.message()
    async def on_anything_else(message: Message) -> None:
        await message.answer(TEXTS[LANG]["fallback"], reply_markup=open_app_keyboard(settings.webapp_url))

    return dp


async def main() -> None:
    # Before basicConfig, or LOG_LEVEL from .env is read after logging is
    # already configured and silently ignored. load_dotenv is idempotent;
    # load_settings calls it again harmlessly.
    load_dotenv()
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s"
    )
    settings = load_settings()
    await db.init(settings.db_path)

    bot = Bot(settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher(settings)

    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text=TEXTS[LANG]["menu_button"], web_app=WebAppInfo(url=settings.webapp_url)
            )
        )
    except TelegramAPIError:
        # Not fatal: /start's inline button still opens the Mini App even if
        # the persistent Menu Button could not be set.
        logger.exception("Could not set the chat menu button")

    logger.info("Mini App: %s", settings.webapp_url)
    # Updates queued while the bot was down are dropped: replaying old
    # /start presses long after the fact would only upsert stale timestamps.
    await dp.start_polling(
        bot,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConfigError as exc:
        # A misconfigured .env is an operator mistake, not a crash: say which
        # line is wrong instead of burying it under a traceback in journalctl.
        raise SystemExit(f"Configuration error: {exc}") from None
    except KeyboardInterrupt:
        pass
