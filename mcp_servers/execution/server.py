import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logging import logger


class ExecutionResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool
    tests_passed: int = 0
    tests_failed: int = 0


class ExecutionMCPServer:
    """Custom MCP Server for sandboxed execution of unit tests, linters, typecheckers, and security scans."""

    def __init__(self, workspace_root: str | None = None):
        self.workspace_root = workspace_root or settings.ALLOWED_HOST_WORKSPACE_ROOT
        logger.info(f"ExecutionMCPServer initialized at workspace: {self.workspace_root}")

    def _execute_command(self, cmd: list[str], timeout: int = 60) -> ExecutionResult:
        """Execute command in sandbox process with timeout and environment protection."""
        start_time = time.time()
        docker_bin = shutil.which("docker")

        # Check if Docker execution should be used
        use_docker = docker_bin is not None and os.environ.get("USE_DOCKER_SANDBOX", "false").lower() == "true"

        if use_docker:
            full_cmd = [
                docker_bin, "run", "--rm",
                "-v", f"{self.workspace_root}:/workspace",
                "-w", "/workspace",
                "--network", "none",
                "--cpus", str(settings.DOCKER_SANDBOX_CPU_LIMIT),
                "--memory", settings.DOCKER_SANDBOX_MEMORY_LIMIT,
                settings.DOCKER_SANDBOX_IMAGE,
            ] + cmd
        else:
            full_cmd = cmd

        logger.info(f"ExecutionMCP running: {' '.join(full_cmd)}")

        timed_out = False
        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        parent_dir = str(Path(self.workspace_root).parent)
        env["PYTHONPATH"] = f"{self.workspace_root}{os.pathsep}{parent_dir}{os.pathsep}{current_pythonpath}".strip(os.pathsep)

        try:
            res = subprocess.run(
                full_cmd,
                cwd=self.workspace_root,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = res.stdout
            stderr = res.stderr
            exit_code = res.returncode
        except subprocess.TimeoutExpired as err:
            timed_out = True
            stdout = err.stdout or "" if isinstance(err.stdout, str) else ""
            stderr = f"Command timed out after {timeout} seconds."
            exit_code = 124

        duration = time.time() - start_time

        # Parse pytest output for pass/fail count
        passed, failed = self._parse_test_summary(stdout + "\n" + stderr)

        return ExecutionResult(
            command=" ".join(cmd),
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration=round(duration, 2),
            timed_out=timed_out,
            tests_passed=passed,
            tests_failed=failed,
        )

    def _parse_test_summary(self, output: str) -> tuple[int, int]:
        """Extract test counts from pytest stdout/stderr using regex."""
        passed, failed = 0, 0
        match_passed = re.search(r"(\d+)\s+passed", output)
        if match_passed:
            passed = int(match_passed.group(1))
        match_failed = re.search(r"(\d+)\s+failed", output)
        if match_failed:
            failed = int(match_failed.group(1))
        return passed, failed

    def run_tests(self, test_path: str = "tests", timeout: int = 120) -> ExecutionResult:
        """Run pytest test suite inside sandbox."""
        cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
        return self._execute_command(cmd, timeout=timeout)

    def run_linter(self, target_path: str = ".") -> ExecutionResult:
        """Run ruff or flake8 linter."""
        cmd = [sys.executable, "-m", "ruff", "check", target_path]
        return self._execute_command(cmd, timeout=60)

    def run_typecheck(self, target_path: str = ".") -> ExecutionResult:
        """Run MyPy static type analysis."""
        cmd = [sys.executable, "-m", "mypy", target_path]
        return self._execute_command(cmd, timeout=60)

    def run_security_scan(self, target_path: str = ".") -> ExecutionResult:
        """Run ruff security scan."""
        cmd = [sys.executable, "-m", "ruff", "check", "--select", "S", target_path]
        return self._execute_command(cmd, timeout=60)
