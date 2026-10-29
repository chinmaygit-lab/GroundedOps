"""LLM adapters; only called when explicitly configured by the user."""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    pass


def _post_json(url: str, data: dict, headers: dict[str, str]) -> dict:
    request = Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with urlopen(request, timeout=75) as response:
            return json.loads(response.read(2_000_000).decode("utf-8"))
    except HTTPError as error:
        raise ProviderError(f"Provider HTTP {error.code}; check API credentials, model and quota") from error
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise ProviderError("Model unavailable. Check model installation, connectivity and provider settings") from error


def generate(provider: str, prompt: str) -> str:
    if provider == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        if not re.fullmatch(r"[A-Za-z0-9_.:/-]{1,90}", model):
            raise ProviderError("Invalid OLLAMA_MODEL value")
        response = _post_json("http://127.0.0.1:11434/api/generate", {
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 320},
        }, {})
        result = response.get("response", "")
    elif provider == "gemini":
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise ProviderError("Set GEMINI_API_KEY in your environment first")
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,90}", model):
            raise ProviderError("Invalid GEMINI_MODEL value")
        response = _post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 400},
        }, {"x-goog-api-key": key})
        try:
            result = "".join(part.get("text", "") for part in response["candidates"][0]["content"]["parts"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("Gemini returned no textual answer") from exc
    else:
        raise ProviderError("Use provider 'retrieval', 'ollama' or 'gemini'")
    if not isinstance(result, str) or not result.strip():
        raise ProviderError("Provider returned an empty answer")
    return result.strip()
