import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from jhub_apps.service.japps_routes import router as japps_router
from jhub_apps.service.logging_utils import setup_logging
from jhub_apps.service.middlewares import create_middlewares
from jhub_apps.service.routes import router
from jhub_apps.version import get_version
import structlog

logger = structlog.get_logger(__name__)
setup_logging()

### When managed by Jupyterhub, the actual endpoints
### will be served out prefixed by /services/:name.
### One way to handle this with FastAPI is to use an APIRouter.
### All routes are defined in routes.py

STATIC_DIR = Path(__file__).parent.parent / "static"

logger.info("Starting jhub-apps service initialization", version=str(get_version()), static_dir=str(STATIC_DIR))

# Log critical environment variables
logger.info("Loading environment variables",
            jupyterhub_api_url=os.environ.get("JUPYTERHUB_API_URL"),
            jupyterhub_service_prefix=os.environ.get("JUPYTERHUB_SERVICE_PREFIX"),
            jupyterhub_client_id=os.environ.get("JUPYTERHUB_CLIENT_ID"),
            public_host=os.environ.get("PUBLIC_HOST"))

try:
    logger.info("Creating FastAPI application")
    app = FastAPI(
        title="JApps Service",
        version=str(get_version()),
        ### Serve out Swagger from the service prefix (<hub>/services/:name/docs)
        openapi_url=router.prefix + "/openapi.json",
        docs_url=router.prefix + "/docs",
        redoc_url=router.prefix + "/redoc",
        ### Add our service client id to the /docs Authorize form automatically
        swagger_ui_init_oauth={"clientId": os.environ["JUPYTERHUB_CLIENT_ID"]},
        swagger_ui_parameters={"persistAuthorization": True},
        ### Default /docs/oauth2 redirect will cause Hub
        ### to raise oauth2 redirect uri mismatch errors
        # swagger_ui_oauth2_redirect_url=os.environ["JUPYTERHUB_OAUTH_CALLBACK_URL"],
    )
    logger.info("FastAPI application created successfully")

    # Configure CORS (optional, disabled by default to avoid WebSocket issues)
    # Set ENABLE_CORS=true environment variable to enable
    enable_cors = os.environ.get("ENABLE_CORS", "false").lower() == "true"

    if enable_cors:
        public_host = os.environ.get("PUBLIC_HOST", "http://localhost:8000")
        allowed_origins = [public_host]

        # Allow additional origins from environment variable if specified
        additional_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
        if additional_origins:
            allowed_origins.extend([origin.strip() for origin in additional_origins.split(",")])

        logger.info("Configuring CORS", allowed_origins=allowed_origins)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
        logger.info("CORS middleware enabled")
    else:
        logger.info("CORS middleware disabled (set ENABLE_CORS=true to enable)")

    logger.info("Mounting static files", static_dir=str(STATIC_DIR), prefix=f"{router.prefix}/static")
    static_files = StaticFiles(directory=STATIC_DIR)
    app.mount(f"{router.prefix}/static", static_files, name="static")
    logger.info("Static files mounted successfully")

    logger.info("Including main router", prefix=router.prefix)
    app.include_router(router)
    logger.info("Main router included successfully")

    logger.info("Including japps router")
    app.include_router(japps_router)
    logger.info("Japps router included successfully")

    logger.info("Creating middlewares")
    create_middlewares(app)
    logger.info("Middlewares created successfully")

    logger.info("jhub-apps service started successfully", version=str(get_version()))

    @app.on_event("startup")
    async def startup_event():
        logger.info("FastAPI startup event triggered - application is ready to serve requests")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("FastAPI shutdown event triggered - application is stopping")

except Exception as e:
    logger.error("Failed to start jhub-apps service", error=str(e), error_type=type(e).__name__)
    raise
