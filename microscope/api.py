import asyncio
import json
import logging
from contextlib import asynccontextmanager
from time import perf_counter
from typing import AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response, status

from .instrument import (
    CaptureJob,
    create_capture_queue,
    instrument_worker,
)
from .schemas import CaptureRequest


logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    queue = create_capture_queue()
    worker_task = asyncio.create_task(instrument_worker(queue))

    app.state.capture_queue = queue
    app.state.worker_task = worker_task

    yield

    await queue.join()
    await queue.put(None)
    await worker_task


app = FastAPI(
    title="Autonomous Microscope Simulator",
    lifespan=lifespan,
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "mode": "simulation"}


@app.post(
    "/capture",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
async def capture(request: CaptureRequest) -> Response:
    capture_id = str(uuid4())
    start = perf_counter()
    loop = asyncio.get_running_loop()
    result: asyncio.Future[bytes] = loop.create_future()

    job = CaptureJob(request=request, result=result)
    queue = app.state.capture_queue

    try:
        queue.put_nowait(job)
    except asyncio.QueueFull as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Capture queue is full. Try again shortly.",
        ) from exc

    png = await result

    logger.info(
        json.dumps(
            {
                "event": "capture.completed",
                "capture_id": capture_id,
                **request.model_dump(),
                "duration_ms": round((perf_counter() - start) * 1000, 2),
            }
        )
    )

    return Response(
        png,
        media_type="image/png",
        headers={"X-Capture-ID": capture_id},
    )