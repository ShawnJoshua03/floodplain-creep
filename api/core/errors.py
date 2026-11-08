"""Typed API errors and the handlers that turn them into JSON responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """The requested neighborhood, brief, or stored result does not exist."""


class InvalidChoiceError(Exception):
    """A query value is outside the options this city supports."""


def register_error_handlers(app: FastAPI) -> None:
    def not_found(_request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    def invalid_choice(_request: Request, error: Exception) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    app.add_exception_handler(NotFoundError, not_found)
    app.add_exception_handler(InvalidChoiceError, invalid_choice)
