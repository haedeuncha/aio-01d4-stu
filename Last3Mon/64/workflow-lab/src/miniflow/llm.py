"""LLM providers: mock (default, no API key), ollama (local), openai, anthropic, gemini.

Select with the MINIFLOW_LLM environment variable.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

from miniflow.template import render


class LLMError(RuntimeError):
    pass


def mock_reply(prompt: str, mock: dict[str, Any] | None, context: dict[str, Any]) -> str:
    """Deterministic reply so the workflow runs without any API key.

    mock.rules: first rule whose keywords appear in the prompt wins.
    mock.template: rendered with the workflow context.
    """
    mock = mock or {}
    lowered = prompt.lower()
    for rule in mock.get("rules", []):
        if any(word.lower() in lowered for word in rule.get("if_contains", [])):
            return str(render(rule["then"], context))
    if "template" in mock:
        return str(render(mock["template"], context))
    if "default" in mock:
        return str(render(mock["default"], context))
    first_line = prompt.strip().splitlines()[0] if prompt.strip() else ""
    return f"[mock-llm] received {len(prompt)} chars. first line: {first_line[:60]}"


def call_ollama(system: str, prompt: str, temperature: float) -> str:
    """Call a local Ollama server through its /api/chat endpoint (no extra package needed)."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    if not host.startswith("http"):
        host = f"http://{host}"
    model = os.getenv("OLLAMA_MODEL", "gemma3:4b")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }).encode("utf-8")
    request = urllib.request.Request(f"{host}/api/chat", data=body, headers={"Content-Type": "application/json"})
    timeout = float(os.getenv("OLLAMA_TIMEOUT", "180"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        if error.code == 404:
            raise LLMError(f"Model '{model}' not found on Ollama. Run: ollama pull {model}") from error
        raise LLMError(f"Ollama returned HTTP {error.code}: {detail[:200]}") from error
    except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
        raise LLMError(f"Cannot reach Ollama at {host}. Is 'ollama serve' running? ({error})") from error
    return data.get("message", {}).get("content", "").strip()


def call_anthropic(system: str, prompt: str) -> str:
    """Call Claude through the Anthropic SDK.

    Current Claude models reject sampling parameters, so temperature is not sent.
    A server-side fallback model answers if the first model declines the request.
    """
    try:
        import anthropic
    except ImportError as error:
        raise LLMError("Install the extra first: uv sync --extra anthropic") from error
    client = anthropic.Anthropic()
    try:
        response = client.beta.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5"),
            max_tokens=16000,
            system=system or anthropic.omit,
            messages=[{"role": "user", "content": prompt}],
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as error:
        raise LLMError("Anthropic credentials are missing or invalid (set ANTHROPIC_API_KEY)") from error
    except anthropic.APIConnectionError as error:
        raise LLMError(f"Cannot reach the Anthropic API ({error})") from error
    except anthropic.APIStatusError as error:
        raise LLMError(f"Anthropic API returned HTTP {error.status_code}: {error.message}") from error
    if response.stop_reason == "refusal":
        raise LLMError("Claude declined this request (stop_reason=refusal)")
    return "".join(block.text for block in response.content if block.type == "text").strip()


def call_gemini(system: str, prompt: str, temperature: float) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as error:
        raise LLMError("Install the extra first: uv sync --extra gemini") from error
    if not os.getenv("GEMINI_API_KEY"):
        raise LLMError("GEMINI_API_KEY is not set")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system or None, temperature=temperature),
    )
    return response.text or ""


def call_openai(system: str, prompt: str, temperature: float) -> str:
    try:
        from openai import OpenAI
    except ImportError as error:
        raise LLMError("Install the extra first: uv sync --extra openai") from error
    if not os.getenv("OPENAI_API_KEY"):
        raise LLMError("OPENAI_API_KEY is not set")
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=system or None,
        input=prompt,
        temperature=temperature,
    )
    return response.output_text


def complete(node: dict[str, Any], prompt: str, system: str, context: dict[str, Any]) -> tuple[str, str]:
    """Return (reply, provider_name)."""
    provider = os.getenv("MINIFLOW_LLM", "mock").lower()
    temperature = float(node.get("temperature", 0.2))
    if provider == "mock":
        return mock_reply(prompt, node.get("mock"), context), "mock"
    if provider == "ollama":
        return call_ollama(system, prompt, temperature), "ollama"
    if provider == "anthropic":
        return call_anthropic(system, prompt), "anthropic"
    if provider == "gemini":
        return call_gemini(system, prompt, temperature), "gemini"
    if provider == "openai":
        return call_openai(system, prompt, temperature), "openai"
    raise LLMError(f"Unknown MINIFLOW_LLM value: {provider} (use mock, ollama, openai, anthropic or gemini)")
