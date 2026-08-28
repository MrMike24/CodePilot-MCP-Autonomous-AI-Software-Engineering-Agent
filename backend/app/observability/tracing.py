from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from backend.app.core.logging import logger


def setup_tracing() -> trace.Tracer:
    """Initialize OpenTelemetry tracer SDK."""
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    logger.info("OpenTelemetry Tracing Provider initialized successfully.")
    return trace.get_tracer("codepilot-mcp")


tracer = setup_tracing()
