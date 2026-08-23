from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict

def standard_error_response(code: str, message: str, status_code: int = 500) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    status_code = exc.status_code
    
    # Map HTTP status codes to string codes for frontend clarity
    code_map = {
        400: "INVALID_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = code_map.get(status_code, "UNKNOWN_ERROR")
    
    return standard_error_response(
        code=error_code,
        message=str(exc.detail),
        status_code=status_code
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Build a readable message from validation errors
    errors = exc.errors()
    msg = "Validation failed"
    if errors:
        first_err = errors[0]
        field = ".".join(str(loc) for loc in first_err.get("loc", []))
        msg = f"Validation error at '{field}': {first_err.get('msg')}"
        
    return standard_error_response(
        code="VALIDATION_ERROR",
        message=msg,
        status_code=422
    )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log unexpected errors but don't leak details
    import logging
    logging.getLogger("app").exception("Unhandled exception:")
    return standard_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred.",
        status_code=500
    )
