from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Callable

from .schemas import CaptureRequest
from .simulator import render_png

@dataclass
class CaptureJob:
    request: CaptureRequest
    result: asyncio.Future[bytes]
def create_capture_queue() -> asyncio.Queue[CaptureJob | None]:
    return asyncio.Queue(maxsize=2)

async def instrument_worker(queue: asyncio.Queue[CaptureJob | None],
                            renderer: Callable[[CaptureRequest], bytes] = render_png) -> None:
    while True:
        job = await queue.get()

        try:
            if job is None:
                return
            png = await asyncio.to_thread(renderer, job.request)

            if not job.result.done():
                job.result.set_result(png)
        except Exception as exc:
            if job is not None and not job.result.done():
                job.result.set_exception(exc)
        finally:
            queue.tesk_done()
    