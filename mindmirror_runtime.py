"""
MindMirror AI Runtime Layer
---------------------------

Keeps MindMirror's AI logic separate from the model/runtime used to execute it.

Development default:
    Ollama + Qwen3.5 2B

Snapdragon deployment:
    GenieX (OpenAI-compatible server/API) with a Qualcomm-backed model/runtime.

Environment variables:
    MINDMIRROR_AI_BACKEND=ollama
    MINDMIRROR_AI_MODEL=qwen3.5:2b

For Snapdragon later:
    MINDMIRROR_AI_BACKEND=geniex
    MINDMIRROR_GENIEX_URL=<OpenAI-compatible chat-completions URL>
    MINDMIRROR_AI_MODEL=<model exposed by GenieX>

The Qualcomm endpoint is deliberately configurable. We will set it only after
testing the actual GenieX installation on the target Snapdragon HP PC.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RuntimeConfig:
    backend: str = os.getenv("MINDMIRROR_AI_BACKEND", "ollama").strip().lower()
    model: str = os.getenv("MINDMIRROR_AI_MODEL", "qwen3.5:2b").strip()

    ollama_host: str = os.getenv(
        "MINDMIRROR_OLLAMA_HOST", "http://127.0.0.1:11434"
    ).rstrip("/")

    # Set this to the actual OpenAI-compatible GenieX chat endpoint on the
    # Snapdragon PC. It is intentionally not assumed here.
    geniex_url: str = os.getenv("MINDMIRROR_GENIEX_URL", "").strip()


class RuntimeErrorBase(RuntimeError):
    """Base exception for MindMirror runtime failures."""


class RuntimeUnavailableError(RuntimeErrorBase):
    """Raised when the selected runtime cannot be reached."""


class RuntimeResponseError(RuntimeErrorBase):
    """Raised when a runtime returns an unusable response."""


class MindMirrorRuntime:
    """Small adapter that exposes one interface to MindMirror's AI engine."""

    def __init__(self, config: Optional[RuntimeConfig] = None) -> None:
        self.config = config or RuntimeConfig()

    @property
    def backend(self) -> str:
        return self.config.backend

    @property
    def model(self) -> str:
        return self.config.model

    def describe(self) -> Dict[str, str]:
        """Return a UI-safe description of the selected runtime."""
        if self.backend == "ollama":
            execution = "Development / fallback runtime"
        elif self.backend == "geniex":
            execution = "Snapdragon deployment runtime"
        else:
            execution = "Unknown runtime"

        return {
            "backend": self.backend,
            "model": self.model,
            "execution": execution,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check whether the selected runtime is reachable.

        This does not run a model inference.
        """
        if self.backend == "ollama":
            return self._ollama_health_check()

        if self.backend == "geniex":
            return self._geniex_health_check()

        return {
            "ok": False,
            "backend": self.backend,
            "message": f"Unsupported MindMirror AI backend: {self.backend}",
        }

    def chat_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        *,
        temperature: float = 0.0,
        num_predict: int = 1200,
        think: bool = False,
    ) -> Dict[str, Any]:
        """
        Run one structured-output inference.

        Returns a normalized dictionary:
            {
                "content": "<JSON string>",
                "backend": "...",
                "model": "..."
            }

        The AI engine can therefore remain independent of the execution runtime.
        """
        if self.backend == "ollama":
            return self._ollama_chat_structured(
                messages,
                schema,
                temperature=temperature,
                num_predict=num_predict,
                think=think,
            )

        if self.backend == "geniex":
            return self._geniex_chat_structured(
                messages,
                schema,
                temperature=temperature,
                num_predict=num_predict,
                think=think,
            )

        raise RuntimeUnavailableError(
            f"Unsupported MindMirror AI backend: {self.backend}"
        )

    # ------------------------------------------------------------------
    # Ollama
    # ------------------------------------------------------------------

    def _ollama_health_check(self) -> Dict[str, Any]:
        try:
            from ollama import Client

            client = Client(host=self.config.ollama_host)
            tags = client.list()

            models = []
            for item in getattr(tags, "models", []) or []:
                name = getattr(item, "model", None) or getattr(item, "name", None)
                if name:
                    models.append(name)

            return {
                "ok": True,
                "backend": "ollama",
                "model": self.model,
                "models": models,
                "message": "Ollama is reachable.",
            }

        except Exception as exc:
            return {
                "ok": False,
                "backend": "ollama",
                "model": self.model,
                "message": f"Ollama is unavailable: {exc}",
            }

    def _ollama_chat_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        *,
        temperature: float,
        num_predict: int,
        think: bool,
    ) -> Dict[str, Any]:
        try:
            from ollama import Client

            client = Client(host=self.config.ollama_host)

            response = client.chat(
                model=self.model,
                messages=messages,
                format=schema,
                think=think,
                options={
                    "temperature": temperature,
                    "num_predict": num_predict,
                },
            )

            content = getattr(getattr(response, "message", None), "content", None)
            if not content:
                raise RuntimeResponseError(
                    "Ollama returned an empty response."
                )

            return {
                "content": content,
                "backend": "ollama",
                "model": self.model,
            }

        except RuntimeResponseError:
            raise
        except Exception as exc:
            raise RuntimeUnavailableError(
                f"Ollama inference failed: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # GenieX / OpenAI-compatible endpoint
    # ------------------------------------------------------------------

    def _geniex_health_check(self) -> Dict[str, Any]:
        if not self.config.geniex_url:
            return {
                "ok": False,
                "backend": "geniex",
                "model": self.model,
                "message": (
                    "GenieX URL is not configured yet. "
                    "Set MINDMIRROR_GENIEX_URL on the Snapdragon PC."
                ),
            }

        # A health check is intentionally lightweight. We only verify that
        # the configured endpoint can be reached; model inference is separate.
        request = urllib.request.Request(
            self.config.geniex_url,
            method="GET",
            headers={"Accept": "application/json"},
        )

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return {
                    "ok": 200 <= response.status < 300,
                    "backend": "geniex",
                    "model": self.model,
                    "status_code": response.status,
                    "message": "GenieX endpoint is reachable.",
                }
        except urllib.error.HTTPError as exc:
            return {
                "ok": False,
                "backend": "geniex",
                "model": self.model,
                "status_code": exc.code,
                "message": (
                    "GenieX endpoint responded to the health check, "
                    f"but returned HTTP {exc.code}."
                ),
            }
        except Exception as exc:
            return {
                "ok": False,
                "backend": "geniex",
                "model": self.model,
                "message": f"GenieX endpoint is unavailable: {exc}",
            }

    def _geniex_chat_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        *,
        temperature: float,
        num_predict: int,
        think: bool,
    ) -> Dict[str, Any]:
        """
        Call a GenieX OpenAI-compatible chat-completions endpoint.

        The exact URL and model name are configured on the target Snapdragon
        machine after GenieX is installed and tested.

        We request JSON output in a provider-neutral way. If the installed
        GenieX server exposes a different structured-output contract, this
        adapter is the only layer that needs to change.
        """
        if not self.config.geniex_url:
            raise RuntimeUnavailableError(
                "MINDMIRROR_GENIEX_URL is not configured."
            )

        # Include the schema in the request so the model receives the exact
        # output contract even when provider-specific JSON-schema support is
        # unavailable.
        system_schema = (
            "\n\nReturn ONLY valid JSON matching this schema:\n"
            + json.dumps(schema, ensure_ascii=False)
        )

        normalized_messages = list(messages)
        if normalized_messages:
            normalized_messages[0] = {
                "role": normalized_messages[0].get("role", "system"),
                "content": normalized_messages[0].get("content", "") + system_schema,
            }
        else:
            normalized_messages = [
                {"role": "system", "content": system_schema}
            ]

        payload = {
            "model": self.model,
            "messages": normalized_messages,
            "temperature": temperature,
            "max_tokens": num_predict,
        }

        # OpenAI-compatible servers commonly accept this flag. If a particular
        # GenieX build does not, this adapter can be adjusted without touching
        # MindMirror's AI analysis code.
        payload["response_format"] = {"type": "json_object"}

        request = urllib.request.Request(
            self.config.geniex_url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeResponseError(
                f"GenieX returned HTTP {exc.code}: {body[:500]}"
            ) from exc
        except Exception as exc:
            raise RuntimeUnavailableError(
                f"GenieX inference failed: {exc}"
            ) from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeResponseError(
                "GenieX returned an unexpected OpenAI-compatible response."
            ) from exc

        if not content:
            raise RuntimeResponseError("GenieX returned an empty response.")

        return {
            "content": content,
            "backend": "geniex",
            "model": self.model,
        }


def get_runtime() -> MindMirrorRuntime:
    """Convenience factory used by MindMirror's AI engine."""
    return MindMirrorRuntime()


if __name__ == "__main__":
    runtime = get_runtime()
    print(json.dumps(runtime.describe(), indent=2))
    print(json.dumps(runtime.health_check(), indent=2))
