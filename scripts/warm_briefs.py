"""Write and store a brief for the focus neighborhood in every scenario, before a demo.

Run: uv run --env-file .env python scripts/warm_briefs.py
With a Gemini key, the model writes each brief and every check must pass. Without one, or when a check or the
call fails, the stored brief is the template and is labeled as one.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    import psycopg

    from api.core.errors import NotFoundError
    from api.core.settings import load_settings
    from api.repositories.briefs import store_brief
    from api.schemas.validation import ValidationResult
    from api.services.brief_input import build_brief_input
    from api.services.brief_writer import write_brief
    from api.services.focus import focus_view
    from api.services.gemini_client import create_client, gemini_call
    from api.services.validation import latest_validation

    settings = load_settings()
    client = create_client(settings)
    call = gemini_call(client, settings.brief_model) if client else None
    print("Model:", settings.brief_model if call else "none, using the template")
    with psycopg.connect(settings.database_url) as conn:
        validation: ValidationResult | None
        try:
            validation = latest_validation(conn)
        except NotFoundError:
            validation = None
        for return_period in settings.return_periods:
            view = focus_view(conn, settings, return_period)
            data = build_brief_input(view, validation)
            written = write_brief(data, settings.banned_terms, settings.resources, call)
            store_brief(conn, view.neighborhood.neighborhood_id, return_period, written.text, written.source)
            print(f"{return_period}-year [{written.source}]: {written.text}")
        conn.commit()


if __name__ == "__main__":
    main()
