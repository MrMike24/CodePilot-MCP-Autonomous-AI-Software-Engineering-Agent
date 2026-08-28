# Benchmark & Evaluation Framework

CodePilot-MCP includes a real evaluation framework (`evaluation/`) for measuring agent engineering performance across benchmark tasks.

## Benchmark Execution

Run evaluation suite:
```bash
python -m evaluation.runner
```

Outputs `evaluation/results.json` containing metrics:

- **Task Completion Rate**: Percentage of benchmark tasks successfully completed.
- **Test Pass Rate**: Percentage of generated/executed tests passing cleanly.
- **Tool Selection Accuracy**: Percentage of valid MCP tool selections.
- **Average Iterations**: Mean debug loop iterations required per task.
- **Average Execution Latency**: Mean wall-clock duration per task execution.
- **Estimated LLM Cost**: Mean API token cost per task.

## Benchmark Task Categories

1. **Bug Fixing**: Repair runtime exceptions or logic errors.
2. **Test Generation**: Create automated pytest regression unit test suites.
3. **Refactoring**: Extract helpers and improve code maintainability.
