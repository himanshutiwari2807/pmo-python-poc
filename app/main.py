from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db import engine
from app.routers import jobs

app = FastAPI(title="PMO Python POC")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/service/status")
async def service_status():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}
