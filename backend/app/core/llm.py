import os
from typing import Any
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.core.logging import logger


class LLMResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    mode: str  # REAL_LLM_MODE or DEMO_SIMULATION


class LLMProvider:
    """Abstraction layer supporting REAL_LLM_MODE (OpenAI/Anthropic API) and DEMO_SIMULATION fallback."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = settings.LLM_API_KEY
        self.demo_mode = settings.DEMO_MODE or (self.api_key in {"mock-key-demo", "mock-or-real-api-key-here", ""})

        if not self.demo_mode and self.api_key:
            self.execution_mode = "REAL_LLM_MODE"
        else:
            self.execution_mode = "DEMO_SIMULATION"

        logger.info(f"LLMProvider initialized in [{self.execution_mode}] using provider='{self.provider}', model='{self.model}'")

    def generate(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
        """Generate text completion from real LLM or demo simulation fallback."""
        if self.execution_mode == "REAL_LLM_MODE":
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=self.model,
                    api_key=self.api_key,
                    temperature=settings.LLM_TEMPERATURE,
                )
                messages = []
                if system_prompt:
                    messages.append(("system", system_prompt))
                messages.append(("user", prompt))

                res = llm.invoke(messages)
                content = str(res.content)
                prompt_tokens = len(prompt.split()) * 2
                completion_tokens = len(content.split()) * 2
                cost = (prompt_tokens * 0.000005) + (completion_tokens * 0.000015)

                return LLMResponse(
                    content=content,
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=round(cost, 5),
                    mode="REAL_LLM_MODE",
                )
            except Exception as e:
                logger.warning(f"REAL_LLM_MODE call failed ({e}). Falling back to DEMO_SIMULATION...")

        # DEMO_SIMULATION fallback
        demo_content = f"Simulated autonomous LLM response for prompt: {prompt[:100]}..."
        return LLMResponse(
            content=demo_content,
            model=f"{self.model}-simulated",
            prompt_tokens=150,
            completion_tokens=200,
            cost_usd=0.0015,
            mode="DEMO_SIMULATION",
        )
