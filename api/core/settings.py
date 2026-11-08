"""The one settings object for the API. Reads environment variables and the files in config/."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import BaseModel

from api.schemas.brief_input import Resource

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DEFAULT_OVERLAY_DIR = ROOT / "data" / "processed" / "overlays"


class Settings(BaseModel):
    database_url: str
    gemini_api_key: str | None
    brief_model: str
    brief_timeout_seconds: float
    resources: list[Resource]
    city: str
    min_count_k: int
    focus_neighborhood: str
    balance_threshold_buildings: float
    signal_noise_multiple: float
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


def read_yaml(path: Path) -> dict[str, object]:
    loaded: dict[str, object] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return loaded


def load_settings(database_url: str | None = None, config_dir: Path = CONFIG_DIR) -> Settings:
    """The database URL comes from the argument, else from DATABASE_URL. The Gemini key is optional."""
    url = database_url or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    city = read_yaml(config_dir / "city.yaml")
    brief = read_yaml(config_dir / "brief.yaml")
    resources = read_yaml(config_dir / "resources.yaml").get("resources") or []
    overlay_dir = os.environ.get("OVERLAY_DIR")
    return Settings.model_validate(
        {
            "database_url": url,
            "gemini_api_key": os.environ.get("GEMINI_API_KEY") or None,
            "brief_model": brief["model"],
            "brief_timeout_seconds": brief["timeout_seconds"],
            "resources": resources,
            "city": city["city"],
            "min_count_k": city["min_count_k"],
            "focus_neighborhood": city["focus_neighborhood"],
            "balance_threshold_buildings": city["balance_threshold_buildings"],
            "signal_noise_multiple": city["signal_noise_multiple"],
            "years": city["years"],
            "return_periods": city["return_periods"],
            "banned_terms": read_lines(config_dir / "banned_terms.txt"),
            "misuse_notice": (config_dir / "misuse_notice.txt").read_text(encoding="utf-8").strip(),
            "limits": read_lines(config_dir / "limits.txt"),
            "overlay_dir": Path(overlay_dir) if overlay_dir else DEFAULT_OVERLAY_DIR,
        }
    )
