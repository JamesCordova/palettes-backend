"""Populate color_catalog with names from the color.pizza API.

Usage:
    uv run scripts/seed_colors.py                     # name every existing
                                                        # row where name IS NULL
    uv run scripts/seed_colors.py --insert FF5733,00FF00,#123ABC
                                                        # insert new rows
                                                        # (hue/saturation/
                                                        # lightness/luminance
                                                        # computed locally,
                                                        # name from the API)
    uv run scripts/seed_colors.py --random 250         # insert N randomly
                                                        # generated colors not
                                                        # already in the table
"""

import argparse
import asyncio
import colorsys
import random
import sys
from pathlib import Path

import asyncpg
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402

COLOR_PIZZA_URL = "https://api.color.pizza/v1/"
BATCH_SIZE = 50


def to_asyncpg_dsn(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


def hex_to_hsl_luminance(hex_code: str) -> tuple[int, int, int, float]:
    hex_value = hex_code.lstrip("#")
    r, g, b = (int(hex_value[i : i + 2], 16) for i in (0, 2, 4))
    h, lightness, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return round(h * 360), round(s * 100), round(lightness * 100), round(luminance, 2)


async def fetch_names(hex_codes: list[str]) -> dict[str, str]:
    names: dict[str, str] = {}
    async with httpx.AsyncClient(timeout=10) as client:
        for i in range(0, len(hex_codes), BATCH_SIZE):
            batch = hex_codes[i : i + BATCH_SIZE]
            values = ",".join(code.lstrip("#") for code in batch)
            response = await client.get(COLOR_PIZZA_URL, params={"values": values})
            response.raise_for_status()
            payload = response.json()
            for requested, color in zip(batch, payload["colors"], strict=True):
                names[requested] = color["name"]
    return names


async def update_missing_names(conn: asyncpg.Connection) -> None:
    rows = await conn.fetch("SELECT hex_code FROM color_catalog WHERE name IS NULL")
    hex_codes = [row["hex_code"] for row in rows]
    if not hex_codes:
        print("No colors are missing a name.")
        return

    names = await fetch_names(hex_codes)
    async with conn.transaction():
        for hex_code, name in names.items():
            await conn.execute(
                "UPDATE color_catalog SET name = $1 WHERE hex_code = $2", name, hex_code
            )
    print(f"Named {len(names)} color(s).")


async def insert_colors(conn: asyncpg.Connection, hex_codes: list[str]) -> None:
    normalized = [code if code.startswith("#") else f"#{code}" for code in hex_codes]
    names = await fetch_names(normalized)

    async with conn.transaction():
        for hex_code in normalized:
            hue, saturation, lightness, luminance = hex_to_hsl_luminance(hex_code)
            await conn.execute(
                """
                INSERT INTO color_catalog (hex_code, hue, saturation, lightness, luminance, name)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (hex_code) DO UPDATE SET name = EXCLUDED.name
                """,
                hex_code,
                hue,
                saturation,
                lightness,
                luminance,
                names.get(hex_code),
            )
    print(f"Inserted/updated {len(normalized)} color(s).")


async def generate_random_hex_codes(conn: asyncpg.Connection, count: int) -> list[str]:
    rows = await conn.fetch("SELECT hex_code FROM color_catalog")
    existing = {row["hex_code"] for row in rows}

    generated: set[str] = set()
    while len(generated) < count:
        candidate = f"#{random.randint(0, 0xFFFFFF):06X}"
        if candidate not in existing:
            generated.add(candidate)
    return list(generated)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--insert",
        help="Comma-separated hex codes to insert as new color_catalog rows",
    )
    group.add_argument(
        "--random",
        type=int,
        metavar="N",
        help="Generate and insert N random colors not already in the table",
    )
    args = parser.parse_args()

    settings = get_settings()
    conn = await asyncpg.connect(to_asyncpg_dsn(settings.database_url))
    try:
        if args.insert:
            hex_codes = [code.strip() for code in args.insert.split(",") if code.strip()]
            await insert_colors(conn, hex_codes)
        elif args.random:
            hex_codes = await generate_random_hex_codes(conn, args.random)
            await insert_colors(conn, hex_codes)
        else:
            await update_missing_names(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
