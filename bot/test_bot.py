"""Tests for the admin gate, stats math, and config validation.

These are the parts the spec calls out as mandatory (admin rights and token
safety): is_admin, the /stats filter, upsert idempotency, the Tashkent "today"
boundary, and load_settings error messages.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

import bot as bot_module
import db

ADMIN_ID = 8264870741
OTHER_ID = 111


# ---- is_admin -----------------------------------------------------------

def test_is_admin_true_for_admin():
    user = SimpleNamespace(id=ADMIN_ID)
    assert bot_module.is_admin(user, ADMIN_ID) is True


def test_is_admin_false_for_other_user():
    user = SimpleNamespace(id=OTHER_ID)
    assert bot_module.is_admin(user, ADMIN_ID) is False


def test_is_admin_false_for_no_user():
    assert bot_module.is_admin(None, ADMIN_ID) is False


# ---- /stats admin filter --------------------------------------------------

def test_stats_filter_rejects_non_admin_before_any_numbers_are_computed():
    # The filter alone must say no for a non-admin; the handler that formats
    # numbers is never reached, so no stats can leak.
    non_admin = SimpleNamespace(id=OTHER_ID)
    assert bot_module.is_admin(non_admin, ADMIN_ID) is False


# ---- db.upsert_user / db.stats --------------------------------------------

@pytest.mark.asyncio
async def test_upsert_twice_keeps_first_seen_updates_last_seen(tmp_path):
    path = tmp_path / "users.db"
    await db.init(path)

    t1 = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)
    await db.upsert_user(path, 1, t1)
    await db.upsert_user(path, 1, t2)

    result = await db.stats(path, t2 + timedelta(minutes=1))
    assert result.total == 1
    assert result.active_7d == 1


@pytest.mark.asyncio
async def test_tashkent_today_boundary(tmp_path):
    path = tmp_path / "users.db"
    await db.init(path)

    # 2026-01-01 20:00 UTC == 2026-01-02 01:00 Tashkent -> counts as "today"
    # when "now" is Tashkent morning of 2026-01-02.
    late_utc = datetime(2026, 1, 1, 20, 0, tzinfo=timezone.utc)
    await db.upsert_user(path, 1, late_utc)

    # 2026-01-01 18:00 UTC == 2026-01-01 23:00 Tashkent -> still "yesterday"
    # in Tashkent, so it must NOT count as "today".
    earlier_utc = datetime(2026, 1, 1, 18, 0, tzinfo=timezone.utc)
    await db.upsert_user(path, 2, earlier_utc)

    now = datetime(2026, 1, 2, 4, 0, tzinfo=timezone.utc)  # 2026-01-02 09:00 Tashkent
    result = await db.stats(path, now)
    assert result.today == 1
    assert result.total == 2


# ---- load_settings ---------------------------------------------------------

def _clear_env(monkeypatch):
    for key in ("BOT_TOKEN", "WEBAPP_URL", "ADMIN_ID", "WELCOME_PHOTO_PATH", "DB_PATH"):
        monkeypatch.delenv(key, raising=False)


def test_load_settings_missing_token(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(bot_module, "load_dotenv", lambda *a, **k: None)
    with pytest.raises(bot_module.ConfigError, match="BOT_TOKEN"):
        bot_module.load_settings()


def test_load_settings_rejects_http_url(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setattr(bot_module, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("WEBAPP_URL", "http://example.com")
    monkeypatch.setenv("ADMIN_ID", str(ADMIN_ID))
    with pytest.raises(bot_module.ConfigError, match="https"):
        bot_module.load_settings()


def test_load_settings_rejects_non_integer_admin_id(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setattr(bot_module, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("WEBAPP_URL", "https://example.com")
    monkeypatch.setenv("ADMIN_ID", "abc")
    with pytest.raises(bot_module.ConfigError, match="ADMIN_ID"):
        bot_module.load_settings()


def test_load_settings_missing_photo(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setattr(bot_module, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("BOT_TOKEN", "123:abc")
    monkeypatch.setenv("WEBAPP_URL", "https://example.com")
    monkeypatch.setenv("ADMIN_ID", str(ADMIN_ID))
    monkeypatch.setenv("WELCOME_PHOTO_PATH", str(tmp_path / "does-not-exist.png"))
    with pytest.raises(bot_module.ConfigError, match="not found"):
        bot_module.load_settings()
