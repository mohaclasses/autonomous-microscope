import json
import logging

from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Response

from .schemas import CaptureRequest
from .simulator import render_png

app = FastAPI(title="Autonomous Microscope Simulator")
logger = logging.getLogger("uvicorn.error")

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "mode": "simulation"}

@app.post("/capture", response_class=Response, 
          responses={200: {"content": {"image/png": {}}}
})
def capture(request: CaptureRequest) -> Response:
    capture_id = str(uuid4())
    start = perf_counter()
    png=render_png(request)
    logger.info(json.dumps({
        "event": "capture.completed",
        "capture_id": capture_id,
        **request.model_dump(),
        "duration_ms": round((perf_counter() - start) * 1000, 2),
    }))
    return Response(png, media_type="image/png",
                    headers={"X-Capture-ID": capture_id})