from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_db
from backend.app.schemas.task import (
    ApprovalRequest,
    RepositoryCreate,
    RepositoryResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskResponse,
)
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.services.task_service import TaskService
from backend.app.services.task_worker import run_agent_task_worker
from mcp_servers.client import MCPClientManager

import asyncio

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new AI engineering task and launch background agent execution worker."""
    service = TaskService(db)
    try:
        task = await service.create_task(task_in)
        # Launch real autonomous background execution worker on active event loop
        asyncio.create_task(run_agent_task_worker(task.id))
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all AI engineering tasks."""
    service = TaskService(db)
    return await service.list_tasks()


@router.get("/stats/summary")
async def get_task_statistics(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get aggregated statistics across engineering tasks."""
    service = TaskService(db)
    return await service.get_dashboard_stats()


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get complete task details including execution trace, review outputs, and diff."""
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

    # Format review output if available
    review_dict = None
    if task.reviews:
        last_rev = task.reviews[-1]
        review_dict = {
            "approved": last_rev.approved,
            "confidence": last_rev.confidence,
            "findings": last_rev.findings_json or [],
            "severity": last_rev.severity,
            "recommendations": last_rev.recommendations_json or [],
            "tests_status": last_rev.tests_status,
        }

    # Format execution result if available
    exec_dict = None
    if task.execution_results:
        last_exec = task.execution_results[-1]
        exec_dict = {
            "command": last_exec.command,
            "exit_code": last_exec.exit_code,
            "stdout": last_exec.stdout,
            "stderr": last_exec.stderr,
            "tests_passed": last_exec.tests_passed,
            "tests_failed": last_exec.tests_failed,
            "duration": last_exec.duration,
        }

    # Format pull request if available
    pr_dict = None
    if task.pull_requests:
        last_pr = task.pull_requests[-1]
        pr_dict = {
            "pr_number": last_pr.pr_number,
            "pr_url": last_pr.pr_url,
            "head_branch": last_pr.branch_name,
            "is_simulated": last_pr.is_simulated,
            "status": last_pr.status,
        }

    # Get actual diff from repository workspace
    workspace = task.repository.local_path if task.repository else "c:/Users/pramu/Downloads/MCP/demo_repository"
    try:
        mcp_client = MCPClientManager(workspace)
        diff_summary = mcp_client.execute_tool("get_diff", {})
    except Exception:
        diff_summary = ""

    return TaskDetailResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        repository_id=task.repository_id,
        status=task.status,
        target_branch=task.target_branch,
        feature_branch=task.feature_branch,
        created_at=task.created_at,
        updated_at=task.updated_at,
        repository=task.repository,
        runs=task.runs,
        review=review_dict,
        diff_summary=str(diff_summary) if diff_summary else None,
        execution_result=exec_dict,
        pull_request=pr_dict,
    )


@router.post("/{task_id}/approve")
async def approve_task(
    task_id: str,
    approval: ApprovalRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Submit human-in-the-loop decision (APPROVE / REJECT). Requires explicit human operator action."""
    service = TaskService(db)
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")

    if task.status != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is in status '{task.status}', but must be 'WAITING_APPROVAL' to submit approval.",
        )

    record = await service.record_approval(task_id, approval)

    if approval.approved:
        # Trigger GitHub MCP PR creation ONLY AFTER HUMAN OPERATOR APPROVAL!
        workspace = task.repository.local_path if task.repository else settings.ALLOWED_HOST_WORKSPACE_ROOT
        mcp_client = MCPClientManager(workspace)

        repo_owner = settings.GITHUB_DEFAULT_OWNER
        repo_name = settings.GITHUB_DEFAULT_REPO
        if task.repository and task.repository.url:
            clean_url = task.repository.url.replace(".git", "").rstrip("/")
            if "github.com/" in clean_url:
                parts = clean_url.split("github.com/")[-1].split("/")
                if len(parts) >= 2:
                    repo_owner, repo_name = parts[0], parts[1]
            elif "github.com:" in clean_url:
                parts = clean_url.split("github.com:")[-1].split("/")
                if len(parts) >= 2:
                    repo_owner, repo_name = parts[0], parts[1]
            elif task.repository.name and "/" in task.repository.name:
                repo_owner, repo_name = task.repository.name.split("/", 1)
            elif task.repository.name:
                repo_name = task.repository.name

        pr_result = mcp_client.execute_tool(
            "create_pull_request",
            {
                "title": task.title,
                "body": f"Automated fix generated by CodePilot-MCP for task {task.id}.\n\nOperator Comments: {approval.comments or 'Approved'}",
                "head_branch": task.feature_branch or f"codepilot/task-{task.id[:8]}",
                "base_branch": task.target_branch or "main",
                "owner": repo_owner,
                "repo": repo_name,
            },
        )

        if isinstance(pr_result, dict) and pr_result.get("error"):
            await service.update_task_status(task_id, "DELIVERY_FAILED")
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub Delivery Failed: {pr_result['error']}",
            )

        if not isinstance(pr_result, dict) or not pr_result.get("pr_url") or not pr_result.get("pr_number"):
            await service.update_task_status(task_id, "DELIVERY_FAILED")
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub Delivery Failed: Invalid response received from GitHub API: {pr_result}",
            )

        await service.record_pull_request(
            task_id=task_id,
            pr_number=pr_result["pr_number"],
            pr_url=pr_result["pr_url"],
            branch_name=task.feature_branch or f"codepilot/task-{task.id[:8]}",
            is_simulated=pr_result.get("is_simulated", False),
        )
        await service.update_task_status(task_id, "DELIVERED")
        await db.commit()
    else:
        await service.update_task_status(task_id, "REJECTED")
        await db.commit()

    return {
        "task_id": task_id,
        "status": "APPROVED" if approval.approved else "REJECTED",
        "delivery_status": "DELIVERED" if approval.approved else "REJECTED",
        "approved_by": record.approved_by,
        "comments": record.comments,
        "timestamp": record.timestamp,
    }
