from fastapi import FastAPI

from backend.routers import auth, location, weather

app = FastAPI(
    title="Weather Dashboard API",
    description="Personalised weather dashboard with alerts and historical data.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(location.router)
app.include_router(weather.router)


@app.get("/health", tags=["Health Check"])
def health():
    return {"status": "ok"}
