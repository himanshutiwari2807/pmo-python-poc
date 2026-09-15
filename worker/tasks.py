import asyncio
import json
import time

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.models import Job
from worker.celery_app import app


async def _publish(job_id: str, payload: dict) -> None:
    client = aioredis.from_url(settings.redis_url)
    try:
        await client.publish(f"job:{job_id}:progress", json.dumps(payload))
    finally:
        await client.aclose()


async def _run_analysis(job_id: str) -> None:
    """Each Celery task runs asyncio.run(), which creates a brand-new event
    loop per task. The FastAPI process's engine/pool is bound to FastAPI's
    long-lived loop and MUST NOT be reused here — a pooled connection handed
    to a second task's new loop raises "Future attached to a different loop".
    So the worker gets its own engine, built fresh and disposed every task,
    with NullPool to guarantee no connection survives across loops."""
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with session_factory() as db:
            job = await db.get(Job, job_id)
            if job is None:
                return

            job.status = "processing"
            await db.commit()

            # Simulate the enrichment -> LLM analysis pipeline described in
            # the architecture doc: a few parallel-ish steps, each reporting
            # progress.
            steps = [
                ("rules_engine", 20),
                ("cache_lookup", 40),
                ("enrichment", 70),
                ("openai_analysis", 100),
            ]
            for step_name, progress in steps:
                time.sleep(1)  # stand-in for real I/O (DB/HTTP/OpenAI calls)
                job.progress = progress
                await db.commit()
                await _publish(
                    job_id,
                    {"status": "processing", "progress": progress, "step": step_name},
                )

            job.status = "done"
            job.result = (
                f"Analyzed {len(job.input_text.split())} word(s): {job.input_text[:80]}"
            )
            await db.commit()
            await _publish(
                job_id, {"status": "done", "progress": 100, "result": job.result}
            )
    finally:
        await engine.dispose()


@app.task(name="worker.tasks.analyze_job")
def analyze_job(job_id: str) -> None:
    asyncio.run(_run_analysis(job_id))
