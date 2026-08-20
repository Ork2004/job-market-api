"""Fetch job vacancies from the public hh.ru API and store the raw
payloads in MongoDB, keyed on (source, external_id) so re-running the
script is a no-op for postings that haven't changed.

Usage:
    python -m scripts.ingest_vacancies --query python --pages 2
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from collections.abc import Iterator
from typing import Any

import httpx
from pymongo.collection import Collection

from app.db.mongo import ensure_indexes, get_raw_vacancies_collection

HH_API_URL = "https://api.hh.ru/vacancies"
SOURCE = "hh.ru"


def fetch_vacancies(
    query: str, pages: int, *, client: httpx.Client | None = None
) -> Iterator[dict[str, Any]]:
    """Yield raw vacancy items from the hh.ru search API, page by page."""
    owns_client = client is None
    http_client = client or httpx.Client(timeout=10)
    try:
        for page in range(pages):
            response = http_client.get(
                HH_API_URL,
                params={"text": query, "page": page, "per_page": 50},
                headers={"User-Agent": "job-market-api ingestion script"},
            )
            response.raise_for_status()
            payload = response.json()
            yield from payload.get("items", [])
            if page + 1 >= payload.get("pages", 0):
                break
    finally:
        if owns_client:
            http_client.close()


def ingest(
    query: str,
    pages: int,
    *,
    collection: Collection | None = None,
    client: httpx.Client | None = None,
) -> int:
    """Upsert fetched vacancies into MongoDB, returns the number processed."""
    target_collection = collection if collection is not None else get_raw_vacancies_collection()

    count = 0
    for item in fetch_vacancies(query, pages, client=client):
        target_collection.update_one(
            {"source": SOURCE, "external_id": item["id"]},
            {
                "$set": {
                    "source": SOURCE,
                    "external_id": item["id"],
                    "fetched_at": dt.datetime.now(dt.UTC),
                    "payload": item,
                }
            },
            upsert=True,
        )
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch vacancies from hh.ru into MongoDB")
    parser.add_argument("--query", default="python", help="Search text (hh.ru 'text' param)")
    parser.add_argument("--pages", type=int, default=1, help="Number of result pages to fetch")
    args = parser.parse_args()

    collection = get_raw_vacancies_collection()
    ensure_indexes(collection)

    count = ingest(args.query, args.pages, collection=collection)
    print(f"Upserted {count} raw vacancy documents from {SOURCE}", file=sys.stderr)


if __name__ == "__main__":
    main()
