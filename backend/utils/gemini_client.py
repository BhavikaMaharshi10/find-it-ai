"""Google Gemini client wrapper for chat and embeddings."""
import json
import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger("finditai")


def is_gemini_configured() -> bool:
    return bool(getattr(settings, "GEMINI_API_KEY", ""))


@lru_cache(maxsize=1)
def _configure_gemini():
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai


def _get_model_name(model: str | None, default: str) -> str:
    name = model or default
    if not name.startswith("models/"):
        return f"models/{name}"
    return name


def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    response_format: dict | None = None,
) -> str:
    """Send a chat completion request and return the response text."""
    genai = _configure_gemini()
    model_name = _get_model_name(model, settings.GEMINI_CHAT_MODEL)

    system_text = "\n".join(
        m["content"] for m in messages if m.get("role") == "system"
    )
    user_text = "\n".join(
        m["content"] for m in messages if m.get("role") == "user"
    )
    prompt = f"{system_text}\n\n{user_text}".strip() if system_text else user_text

    generation_config: dict = {"temperature": temperature}
    if response_format and response_format.get("type") == "json_object":
        generation_config["response_mime_type"] = "application/json"

    gemini_model = genai.GenerativeModel(model_name.replace("models/", ""))
    response = gemini_model.generate_content(
        prompt,
        generation_config=generation_config,
    )
    return response.text


def chat_completion_json(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
) -> dict:
    """Chat completion with JSON response parsing."""
    content = chat_completion(
        messages,
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    # Strip markdown code fences if present
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def generate_embedding(text: str, task_type: str = "retrieval_document") -> list[float]:
    """Generate a vector embedding using Gemini."""
    genai = _configure_gemini()
    model_name = _get_model_name(None, settings.GEMINI_EMBEDDING_MODEL)

    kwargs: dict = {
        "model": model_name,
        "content": text[:8000],
        "task_type": task_type,
    }
    # gemini-embedding-001 supports configurable output dimensions
    if settings.EMBEDDING_DIMENSIONS:
        kwargs["output_dimensionality"] = settings.EMBEDDING_DIMENSIONS

    result = genai.embed_content(**kwargs)
    return result["embedding"]


def generate_embeddings_batch(
    texts: list[str], task_type: str = "retrieval_document"
) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    return [generate_embedding(t, task_type=task_type) for t in texts]
