"""HTTP downloads. All failures raise, nothing is retried silently."""

from __future__ import annotations

from pathlib import Path

import httpx

TIMEOUT = httpx.Timeout(60.0, read=600.0)
BUCKET_API = "https://storage.googleapis.com/storage/v1/b/open-buildings-temporal-data/o"


def fetch_text(url: str) -> str:
    response = httpx.get(url, timeout=TIMEOUT, follow_redirects=True)
    response.raise_for_status()
    return response.text


def list_bucket_names(prefix: str) -> list[str]:
    """List object names under a prefix in the public Open Buildings Temporal bucket."""
    names: list[str] = []
    token: str | None = None
    while True:
        params = {"prefix": prefix, "fields": "items(name),nextPageToken", "maxResults": "1000"}
        if token:
            params["pageToken"] = token
        response = httpx.get(BUCKET_API, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        body = response.json()
        names.extend(item["name"] for item in body.get("items", []))
        token = body.get("nextPageToken")
        if not token:
            return names


def download_file(url: str, destination: Path) -> bool:
    """Download to destination. Return False when a complete file already exists."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=TIMEOUT, follow_redirects=True) as response:
        response.raise_for_status()
        expected = int(response.headers.get("content-length", "-1"))
        if destination.exists() and destination.stat().st_size == expected:
            return False
        partial = destination.with_suffix(destination.suffix + ".part")
        with partial.open("wb") as handle:
            for chunk in response.iter_bytes(1 << 20):
                handle.write(chunk)
        if expected >= 0 and partial.stat().st_size != expected:
            raise OSError(f"Incomplete download for {url}: got {partial.stat().st_size}, expected {expected}")
        partial.replace(destination)
    return True
