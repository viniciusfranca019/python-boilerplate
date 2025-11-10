"""FastAPI application entry point.

This module initializes the FastAPI application using the Server class
and registers all routes, middleware, and exception handlers.

Justification: Separating server configuration (server.py) from API
initialization and routing (api.py) follows separation of concerns principle.
"""

import argparse

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server import Server


# Create server instance and initialize app
server = Server()
server.get_app()


server.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@server.app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError) -> JSONResponse:
    """Handle validation errors with 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "type": "ValueError",
        },
    )


@server.app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors with 500 Internal Server Error."""
    # TODO: Add proper logging here
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "type": type(exc).__name__,
        },
    )


root_router = server.get_root_router()


@root_router.get("/")
async def root() -> dict[str, str]:
    """Root API endpoint.

    Returns:
        dict: Simple status message with service information
    """
    return {
        "service": server._title,
        "status": "operational",
        "version": server._version,
    }


@root_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration.

    Justification: Essential for Kubernetes/Docker health probes
    and load balancer configuration.

    Returns:
        dict: Health status information
    """
    # TODO: Add actual health checks (DB, message broker, etc.)
    return {
        "status": "healthy",
        "service": "template-api",
        "version": server._version,
    }


if __name__ == "__main__":
    # Parse command-line arguments
    # Justification: CLI arguments provide flexible server configuration
    # without modifying code, enabling different environments and deployments
    parser = argparse.ArgumentParser(
        description="Template API - FastAPI application server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host address",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="Enable auto-reload for development (default: True)",
    )

    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for production",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Logging level",
    )

    parser.add_argument(
        "--import-string",
        type=str,
        default="api:server.app",
        help="Import string for reload mode",
    )

    args = parser.parse_args()

    # Determine reload setting (--no-reload overrides --reload)
    reload = not args.no_reload if args.no_reload else args.reload

    # Start server with parsed arguments
    # Justification: Encapsulated server start with configurable options
    server.start_server(
        host=args.host,
        port=args.port,
        reload=reload,
        log_level=args.log_level,
        import_string=args.import_string,
    )
