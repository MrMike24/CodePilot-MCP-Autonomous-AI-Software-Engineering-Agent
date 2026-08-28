# Multi-Agent Orchestration & Workflow Design

CodePilot-MCP implements a multi-agent orchestration architecture using LangGraph. Agents are specialized, strongly-typed, and communicate via a shared `AgentState`.

## Agent Roles & Responsibilities

### 1. Planner Agent
- Analyzes user task description and repository context retrieved via Code RAG.
- Produces a structured `TaskPlan` object containing:
  - `summary`: High level technical overview.
  - `subtasks`: Concrete ordered engineering steps.
  - `relevant_files`: Target source files to inspect and edit.
  - `required_tools`: MCP tools needed.
  - `risks`: Architectural or breaking change risks.
  - `test_strategy`: Regression test strategy.

### 2. Coding Agent
- Inspects retrieved source code and files via Filesystem MCP.
- Applies code modifications and generates pytest regression test cases.
- Computes git diff summary.

### 3. Debugger Agent
- Activated when sandboxed unit tests fail.
- Analyzes test output and stack tracebacks.
- Proposes and applies code fixes via Filesystem MCP tools.
- Increments `debug_iterations` counter. Enforces `MAX_DEBUG_ITERATIONS = 5` iteration cap to prevent infinite debugging loops.

### 4. Reviewer Agent
- Evaluates code diff quality, test pass status, and security compliance.
- Returns structured `ReviewResult` containing:
  - `approved`: Boolean approval status.
  - `confidence`: Confidence score (0.0 - 1.0).
  - `findings`: List of specific file findings and severity.
  - `recommendations`: Code quality recommendations.
  - `tests_status`: Pytest pass/fail summary.

## Workflow State Graph

```
START
  │
  ▼
Planner Agent (Generate TaskPlan & Query Code RAG)
  │
  ▼
Coding Agent (Modify Files & Generate Tests via MCP)
  │
  ▼
Execution MCP (Run Pytest in Sandbox)
  │
  ├───────► Tests Failed & Iterations < 5 ───► Debugger Agent
  │                                                  │
  │                                                  ▼
  │                                           Execution MCP
  │
  ├───────► Tests Passed ───► Reviewer Agent
  │                                │
  ▼                                ▼
Tests Failed & Iterations >= 5   Human Approval Gate
  │                                │
  ▼                                ├─► Approved ──► Create PR ──► END
  END (Report Failure)             └─► Rejected ──► END
```
