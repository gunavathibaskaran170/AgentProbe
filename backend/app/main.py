from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models  # noqa: F401  (registers tables with Base.metadata)
from app.db import create_tables
from app.errors import ApiError, error_payload
from app.routes import health, runs, tests


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="AgentProbe API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    detail = errors[0].get("msg", "Invalid request") if errors else "Invalid request"
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", f"Validation error: {detail}"),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=error_payload("NOT_FOUND", str(exc.detail)),
        )
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", str(exc.detail)),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", "Internal server error"),
    )


app.include_router(health.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
