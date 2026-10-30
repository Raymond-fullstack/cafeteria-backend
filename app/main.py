from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, dashboard, debts, orders, products, reports, users, wallet

app = FastAPI(title=settings.app_name, version="1.0.0")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}


@app.get("/")
def root():
    return {"message": "Cafeteria Backend is running"}


@app.exception_handler(Exception)
async def global_exception_handler(_, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


for router in [auth.router, dashboard.router, products.router, users.router, wallet.router, debts.router, orders.router, reports.router]:
    app.include_router(router)
