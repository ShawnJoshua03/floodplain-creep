"""Run the API: uv run --env-file .env python -m api.serve"""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
