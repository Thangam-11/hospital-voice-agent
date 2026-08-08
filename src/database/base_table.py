"""
One-off script: creates all tables (patients, doctors, appointment_slots,
appointments, medical_records, call_logs) in the configured Postgres database.

Run this ONCE before seed_data.py, or any time you change models.py and
want to recreate tables in a fresh/empty database.

Usage:
    python -m src.database.create_tables
"""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.database.base import Base
from src.database.base_engine import engine
# Import models so their tables register on Base.metadata before create_all.
import src.database.models  # noqa: F401


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")


if __name__ == "__main__":
    asyncio.run(main())