# CodePilot-MCP Architecture Overview

CodePilot-MCP is an autonomous AI software engineering agent designed with clean architecture principles, leveraging LangGraph for multi-agent orchestration, the Model Context Protocol (MCP) for tool interactions, Qdrant for code-aware RAG, Docker for sandboxed execution, and OpenTelemetry/Prometheus for full observability.

## High Level Architecture Diagram

```mermaid
graph TD
    User[Developer / User] -->|Web UI| FE[React + TypeScript Frontend]
    FE -->|REST API / Async Task| API[FastAPI Backend Server]
    API -->|Persist Audit & Task Records| DB[(PostgreSQL Database)]
    API -->|Orchestrate Agent Graph| LG[LangGraph Engine]
    
    subgraph Multi-Agent System
        LG --> Planner[Planner Agent]
        LG --> Coder[Coding Agent]
        LG --> Debugger[Debugger Agent]
        LG --> Reviewer[Reviewer Agent]
    end
    
    Coder -->|Hybrid Vector Search| RAG[Code RAG Store]
    RAG -->|Vector Embeddings| QD[(Qdrant Vector DB)]
    
    subgraph Custom MCP Layer
        LG --> MCP_Manager[MCP Client Manager]
        MCP_Manager --> FS_MCP[Filesystem MCP Server]
        MCP_Manager --> GH_MCP[GitHub MCP Server]
        MCP_Manager --> EXEC_MCP[Execution MCP Server]
    end
    
    FS_MCP -->|Restricted Path I/O| Workspace[Isolated Git Workspace]
    GH_MCP -->|Branch / PR Ops| GitHub[GitHub API / Demo Simulation]
    EXEC_MCP -->|Container Sandbox| Docker[Docker Engine]
    
    LG -->|Pause before PR| Gate[Human Approval Gate]
    Gate -->|Approve / Reject| User
```

## Core Architectural Layers

1. **API & Interface Layer (FastAPI & React)**: REST API serving agent execution control, status polling, trace monitoring, and human approval gates.
2. **Orchestration Layer (LangGraph)**: Strongly-typed `AgentState` transition graph linking Planner -> Coder -> Test -> (Debug Loop) -> Reviewer -> Human Approval -> PR Creation.
3. **Model Context Protocol (MCP) Layer**: Decoupled custom servers for Filesystem, GitHub, and Execution isolation.
4. **Retrieval-Augmented Generation (RAG)**: AST-aware Python code splitter, local L2-normalized embeddings, and Qdrant vector database hybrid keyword search.
5. **Execution & Security Sandbox**: Isolated Docker sandbox execution preventing host execution risks.
6. **Observability & Telemetry**: Prometheus metrics exporter and OpenTelemetry tracing.
