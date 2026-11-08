"""The one settings object for the API. Reads environment variables and the files in config/."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DEFAULT_OVERLAY_DIR = ROOT / "data" / "processed" / "overlays"


class Settings(BaseModel):
    database_url: str
    city: str
    min_count_k: int
    years: list[int]
    return_periods: list[int]
    banned_terms: list[str]
    misuse_notice: str
    limits: list[str]
    overlay_dir: Path

    @property
    def first_year(self) -> int:
        return self.years[0]

    @property
    def last_year(self) -> int:
        return self.years[1]


def read_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_settings(database_url: str | None = None, config_dir: Path = CONFIG_DIR) -> Settings:
    """The database URL comes from the argument, else from DATABASE_URL."""
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    city = yaml.safe_load((config_dir / "city.yaml").read_text(encoding="utf-8"))
    overlay_dir = os.environ.get("OVERLAY_DIR")
    return Settings(
        database_url=url,
        city=city["city"],
        min_count_k=city["min_count_k"],
        years=city["years"],
        return_periods=city["return_periods"],
        banned_terms=read_lines(config_dir / "banned_terms.txt"),
        misuse_notice=(config_dir / "misuse_notice.txt").read_text(encoding="utf-8").strip(),
        limits=read_lines(config_dir / "limits.txt"),
        overlay_dir=Path(overlay_dir) if overlay_dir else DEFAULT_OVERLAY_DIR,
    )
