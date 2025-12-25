import time
import random
from datetime import datetime
from opentelemetry import trace
from fastapi import APIRouter, Request
from utils.logs_collector import logger
from config.prom_metrics import REQUEST_COUNT, REQUEST_LATENCY

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/heavy")
def heavy_task(request: Request):
    endpoint = "/heavy"

    with tracer.start_as_current_span(
        "heavy_task",
        attributes={
            "http.method": request.method,
            "http.route": endpoint
        }
    ):
        logger.info("heavy_task_started", extra={"endpoint": endpoint})

        with tracer.start_as_current_span("simulate_heavy_work"):
            with REQUEST_LATENCY.labels(endpoint=endpoint).time():
                delay = random.uniform(0, 5)
                time.sleep(delay)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=200
        ).inc()

        logger.info(
            "heavy_task_completed",
            extra={
                "endpoint": endpoint,
                "delay_seconds": round(delay, 2),
                "method": request.method
            }
        )

        return {
            "status": "done",
            "delay_seconds": round(delay, 2)
        }
