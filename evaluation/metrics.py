from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkMetrics:
    total_tasks: int
    completed_tasks: int
    task_completion_rate: float
    test_pass_rate: float
    tool_selection_accuracy: float
    avg_iterations: float
    avg_latency_sec: float
    avg_cost_usd: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "task_completion_rate": round(self.task_completion_rate, 4),
            "test_pass_rate": round(self.test_pass_rate, 4),
            "tool_selection_accuracy": round(self.tool_selection_accuracy, 4),
            "avg_iterations": round(self.avg_iterations, 2),
            "avg_latency_sec": round(self.avg_latency_sec, 2),
            "avg_cost_usd": round(self.avg_cost_usd, 4),
        }
