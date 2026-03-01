from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models import registry  # noqa: F401
from app.api.v1.endpoints import reports, alerts, queries, data_sources, users, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(data_sources.router, prefix=f"{settings.API_V1_STR}/data_sources", tags=["data_sources"])
app.include_router(queries.router, prefix=f"{settings.API_V1_STR}/queries", tags=["queries"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["alerts"])

@app.get("/")
def root():
    return {"message": "Welcome to AI Business Analyst API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
