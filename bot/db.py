"""SQLite storage for the Mind Kids bot.

Only `user_id` plus two timestamps are kept — no name, no username, no phone.
This is a kids' app; the owner only needs counts, never who is behind them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite

# Uzbekistan is UTC+5 year-round and observes no DST, so a fixed offset is
# exact and avoids depending on the tz database being present on the host.
TASHKENT = timezone(timedelta(hours=5))
STATS_WINDOW_DAYS = 7

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
)
"""


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


async def init(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(path) as conn:
        await conn.execute(_SCHEMA)
        await conn.commit()


async def upsert_user(path: Path, user_id: int, now: datetime) -> None:
    ts = _iso(now)
    async with aiosqlite.connect(path) as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, first_seen, last_seen) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_seen = excluded.last_seen
            """,
            (user_id, ts, ts),
        )
        await conn.commit()


@dataclass(frozen=True)
class Stats:
    total: int
    today: int
    new_7d: int
    active_7d: int


def _tashkent_midnight_utc_iso(now: datetime) -> str:
    """Start of "today" in Tashkent, expressed as a UTC ISO timestamp."""
    local_midnight = now.astimezone(TASHKENT).replace(hour=0, minute=0, second=0, microsecond=0)
    return _iso(local_midnight)


async def stats(path: Path, now: datetime) -> Stats:
    today_cutoff = _tashkent_midnight_utc_iso(now)
    week_cutoff = _iso(now - timedelta(days=STATS_WINDOW_DAYS))

    async with aiosqlite.connect(path) as conn:
        total = (await (await conn.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        today = (
            await (
                await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE first_seen >= ?", (today_cutoff,)
                )
            ).fetchone()
        )[0]
        new_7d = (
            await (
                await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE first_seen >= ?", (week_cutoff,)
                )
            ).fetchone()
        )[0]
        active_7d = (
            await (
                await conn.execute(
                    "SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week_cutoff,)
                )
            ).fetchone()
        )[0]

    return Stats(total=total, today=today, new_7d=new_7d, active_7d=active_7d)
