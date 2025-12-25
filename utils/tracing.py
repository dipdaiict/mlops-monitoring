from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

resource = Resource.create({
    "service.name": "ml-api"
})

trace.set_tracer_provider(
    TracerProvider(resource=resource)
)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318",
    insecure=True
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
