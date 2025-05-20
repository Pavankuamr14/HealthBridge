from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from routers import users, patients, admin
from database import init_db, test_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Management System",
    description="API for managing hospital patients and users",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None  # Disable default redoc
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(admin.router)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Hospital Management System",
        version="1.0.0",
        description="API for managing hospital patients and users",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "users/login",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access"
                    }
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom documentation endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Return the landing page"""
    with open("static/index.html", "r") as f:
        return f.read()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        if not test_db_connection():
            logger.error("Failed to connect to database")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise