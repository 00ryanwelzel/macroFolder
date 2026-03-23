"""Fetch flip price data from skyblock.bz and save a structured JSON snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


API_URL = "https://api.skyblock.bz/api/flips"
OUTPUT_PATH = Path(__file__).with_name("prices.json")


def fetch_price_vector(timeout: int = 20) -> list[dict[str, Any]]:
    """Return a normalized vector of flip price records from the public API."""
    response = requests.get(API_URL, timeout=timeout)
    response.raise_for_status()
    raw_items = response.json()

    results: list[dict[str, Any]] = []
    for item in raw_items:
        results.append(
            {
                "product_id": item.get("productId") or item.get("id") or item.get("tag"),
                "buy_price": item.get("buyprice"),
                "sell_price": item.get("sellprice"),
                "one_hour_instabuy": item.get("instabuys"),
                "coins_per_hour": item.get("marginperhour"),
            }
        )

    return results


def update_prices_json(
    output_path: str | Path = OUTPUT_PATH, timeout: int = 20
) -> list[dict[str, Any]]:
    """Fetch price data, write it to JSON, print a preview, and return the vector."""
    results = fetch_price_vector(timeout=timeout)
    destination = Path(output_path)
    destination.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Wrote {len(results)} items to {destination}")
    for row in results[:10]:
        print(json.dumps(row, indent=2))

    return results


if __name__ == "__main__":
    update_prices_json()
