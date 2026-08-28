import asyncio
import os
import subprocess
import pytest
from pathlib import Path
from backend.app.database.session import init_db
from backend.app.core.config import settings

@pytest.fixture(autouse=True)
async def setup_test_environment():
    await init_db()
    demo_root = Path(settings.ALLOWED_HOST_WORKSPACE_ROOT)
    if demo_root.exists() and (demo_root / ".git").exists():
        subprocess.run(["git", "checkout", "-B", "main"], cwd=str(demo_root), capture_output=True)
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=str(demo_root), capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=str(demo_root), capture_output=True)
    yield
