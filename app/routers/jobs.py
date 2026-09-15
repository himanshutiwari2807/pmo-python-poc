import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Job
from app.schemas import JobCreateRequest, JobResponse
from worker.tasks import analyze_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(body: JobCreateRequest, db: AsyncSession = Depends(get_db)) -> Job:
    job = Job(input_text=body.input_text)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    analyze_job.delay(job.id)

    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> Job:
    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def _job_event_stream(job_id: str):
    client = aioredis.from_url(settings.redis_url)
    pubsub = client.pubsub()
    await pubsub.subscribe(f"job:{job_id}:progress")
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = message["data"]
            yield f"data: {data.decode() if isinstance(data, bytes) else data}\n\n"
            payload = json.loads(data)
            if payload.get("status") == "done":
                break
    finally:
        await pubsub.unsubscribe(f"job:{job_id}:progress")
        await pubsub.aclose()
        await client.aclose()


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(
        _job_event_stream(job_id), media_type="text/event-stream"
    )
