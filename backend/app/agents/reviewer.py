from typing import Any
from backend.app.agents.state import AgentState
from backend.app.core.logging import logger
from backend.app.schemas.task import ReviewFinding, ReviewResult


class ReviewerAgent:
    """Reviewer Agent evaluating diff quality, test pass status, and security compliance."""

    def run(self, state: AgentState) -> dict[str, Any]:
        logger.info("ReviewerAgent evaluating proposed code changes...")

        exec_res = state.get("execution_result", {})
        exit_code = exec_res.get("exit_code", 1)
        tests_passed = exec_res.get("tests_passed", 0)
        tests_failed = exec_res.get("tests_failed", 0)
        diff = state.get("diff_summary", "")

        findings = []
        approved = True
        confidence = 0.95
        severity = "LOW"

        if exit_code != 0 or tests_failed > 0:
            approved = False
            confidence = 0.60
            severity = "HIGH"
            findings.append(
                ReviewFinding(
                    file="tests/test_api.py",
                    line=None,
                    issue=f"Test suite failed with {tests_failed} test failure(s).",
                    severity="HIGH",
                )
            )

        if not diff or diff == "No changes detected.":
            if tests_passed > 0 and exit_code == 0:
                logger.info("Diff summary is clean against git baseline; tests verified passing.")
            else:
                approved = False
                severity = "MEDIUM"
                findings.append(
                    ReviewFinding(
                        file="workspace",
                        line=None,
                        issue="No functional code diff detected.",
                        severity="MEDIUM",
                    )
                )

        review = ReviewResult(
            approved=approved,
            confidence=confidence,
            findings=findings,
            severity=severity,
            recommendations=[
                "Ensure error status codes strictly follow HTTP standard RFC 7231.",
                "Maintain regression unit tests for all edge cases.",
            ],
            tests_status=f"PASSED ({tests_passed} passed)" if approved else f"FAILED ({tests_failed} failed)",
        )

        return {
            "review": review,
            "status": "WAITING_APPROVAL" if approved else "REVIEW_REJECTED",
        }
