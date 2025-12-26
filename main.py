from fastapi import FastAPI
from routes.health import router as health_router
from routes.metrics import router as metrics_router
from routes.inference import router as inference_router
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# import tracing  # just importing initializes tracing
from utils import tracing

app = FastAPI(title="ML Inference Dashboard.",
            version=1.0)
FastAPIInstrumentor.instrument_app(app)

# register routes
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(inference_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)