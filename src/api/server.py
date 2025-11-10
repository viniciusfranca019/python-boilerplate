"""FastAPI application server configuration.

This module provides the Server class that encapsulates FastAPI application
setup and lifecycle management following clean architecture principles.

Justification: Using a class-based approach provides better encapsulation,
easier dependency injection, and cleaner testing scenarios while maintaining
single responsibility principle.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter


class Server:
    """FastAPI server with lifecycle management and configuration.

    Justification: Encapsulating server logic in a class enables better
    resource management, dependency injection, and testability compared
    to module-level functions.

    Attributes:
        app: FastAPI application instance
        _title: API title for documentation
        _version: API version
    """

    def __init__(
        self,
        title: str = "template API",
        description: str = "Workflow API for template processing with FastAPI and Celery",
        version: str = "0.1.0",
        debug: bool = False,
    ):
        """Initialize the server with configuration.

        Args:
            title: API title for documentation
            description: API description for documentation
            version: API version
            debug: Enable debug mode
        """
        self._title = title
        self._description = description
        self._version = version
        self._debug = debug

        self.app: FastAPI = FastAPI(
            title=self._title,
            description=self._description,
            version=self._version,
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_url="/api/openapi.json",
            lifespan=self._lifespan,
            debug=self._debug,
        )

        self.root_router = APIRouter(prefix="/api", tags=["API"])

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifespan events.

        Justification: Using lifespan context manager (FastAPI 0.93+) provides
        clean startup/shutdown handling for resources like DB connections,
        message brokers, and background tasks.

        Args:
            app: FastAPI application instance

        Yields:
            None: Control during application lifetime
        """
        # Startup: Initialize resources
        await self._startup()

        yield

        # Shutdown: Cleanup resources
        await self._shutdown()

    async def _startup(self) -> None:
        """Execute startup tasks.

        Justification: Separating startup logic enables easier testing
        and extension of initialization behavior.
        """
        # TODO: Add database connection initialization
        # TODO: Add message broker connection initialization
        # TODO: Add cache connection initialization
        print(f"🚀 {self._title} starting up...")

    async def _shutdown(self) -> None:
        """Execute shutdown tasks.

        Justification: Proper resource cleanup prevents memory leaks
        and ensures graceful degradation.
        """
        # TODO: Close database connections
        # TODO: Close message broker connections
        # TODO: Close cache connections
        print(f"🛑 {self._title} shutting down...")

    def add_router(self, router: APIRouter, path: str, tags: list[str]) -> None:
        """Add a router to the FastAPI application.

        Justification: Encapsulating router addition allows for
        modular route management and cleaner application setup.

        Args:
            router: FastAPI APIRouter instance to add
        """
        if self.app is None:
            raise RuntimeError("Application not created. Call create_app() first.")

        self.root_router.include_router(router, prefix=path, tags=tags)

    def get_root_router(self) -> APIRouter:
        """Get the root API router.

        Justification: Exposing the root router allows external modules
        to register routes before the application starts, promoting modularity.

        Returns:
            APIRouter: The root API router
        """
        return self.root_router

    def get_app(self) -> FastAPI:
        """Create and configure FastAPI application instance.

        Justification: Factory method pattern enables controlled initialization
        and ensures all configuration steps are executed in the correct order.
        Returning the app allows for flexible usage patterns while maintaining
        the internal reference.

        Returns:
            FastAPI: Configured application instance (same reference as self.app)
        """
        if self.app is None:
            raise RuntimeError("Application not created. Call create_app() first.")

        return self.app

    def _setup_routers(self) -> None:
        """Setup initial routers for the application.

        Justification: Centralizing router setup ensures all routes
        are registered before the application starts, maintaining
        a clear structure.
        """
        if self.app is None:
            raise RuntimeError("Application not created. Call create_app() first.")

        self.app.include_router(self.root_router)

    def start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        reload: bool = True,
        log_level: str = "info",
        import_string: str = "api:server.app",
    ) -> None:
        """Start the FastAPI server using Uvicorn.

        Justification: Encapsulating server start logic allows for
        easy configuration changes and testing. Provides flexible
        configuration for different environments (dev/prod).

        Args:
            host: Server host address (default: 0.0.0.0 for all interfaces)
            port: Server port (default: 8000)
            reload: Enable auto-reload for development (default: True)
            log_level: Logging level (default: info)
            import_string: Import string for reload mode (default: "api:server.app")

        Raises:
            RuntimeError: If app is not created before starting server
        """
        import uvicorn

        if self.app is None:
            raise RuntimeError("Application not created. Call create_app() first.")

        self._setup_routers()
        # Use import string when reload is enabled, direct app otherwise
        # Justification: Uvicorn requires import string for hot reload functionality
        if reload:
            uvicorn.run(
                import_string,
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
            )
        else:
            uvicorn.run(
                self.app,
                host=host,
                port=port,
                reload=False,
                log_level=log_level,
            )
