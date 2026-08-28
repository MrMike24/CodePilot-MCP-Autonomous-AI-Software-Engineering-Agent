from datetime import datetime, timezone
import pytest
from backend.app.models.domain import ToolCallModel
from backend.app.schemas.task import ToolCallTrace


def test_tool_call_trace_serialization():
    """Verify ToolCallTrace correctly extracts arguments_json and result_json from ORM model."""
    now = datetime.now(timezone.utc)
    tool_model = ToolCallModel(
        id="tool-12345",
        step_id="step-67890",
        tool_name="read_file",
        arguments_json={"path": "app/main.py"},
        result_json={"status": "SUCCESS", "lines": 42},
        status="SUCCESS",
        duration_ms=18.5,
        timestamp=now,
    )

    # Validate using from_attributes (Pydantic v2)
    trace = ToolCallTrace.model_validate(tool_model)
    assert trace.id == "tool-12345"
    assert trace.tool_name == "read_file"
    assert trace.arguments == {"path": "app/main.py"}
    assert trace.result == {"status": "SUCCESS", "lines": 42}
    assert trace.status == "SUCCESS"
    assert trace.duration_ms == 18.5
