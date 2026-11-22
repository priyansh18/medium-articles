"""Free-tier LLM text fallback used for this experiment.

Provider chain, first available wins: Gemini (free tier) -> Groq (free tier) ->
Ollama (local, unlimited, needs `ollama serve` + `ollama pull llama3.1:8b`).
Reads GEMINI_API_KEY / GROQ_API_KEY from the environment; Ollama needs neither.

    from llm_client import generate_text
    text, provider_used = generate_text("prompt here")
"""
import os

PROVIDERS_ORDER = ["gemini", "groq", "ollama"]


def _try_gemini(prompt, model="gemini-3.6-flash"):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    from google import genai
    client = genai.Client(api_key=key)
    resp = client.models.generate_content(model=model, contents=prompt)
    return resp.text.strip()


def _try_groq(prompt, model="llama-3.3-70b-versatile"):
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    import requests
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _try_ollama(prompt, model="llama3.1:8b"):
    import requests
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except requests.exceptions.RequestException:
        return None  # server not running, or model not pulled -- just unavailable


PROVIDERS = {"gemini": _try_gemini, "groq": _try_groq, "ollama": _try_ollama}


def generate_text(prompt, provider="auto"):
    """Return (text, provider_name). Raises RuntimeError if every provider fails/is unavailable."""
    order = PROVIDERS_ORDER if provider == "auto" else [provider]
    errors = []
    for name in order:
        try:
            result = PROVIDERS[name](prompt)
            if result:
                return result, name
        except Exception as e:
            errors.append(f"{name}: {e}")
    raise RuntimeError(
        "All providers unavailable/failed.\n" + "\n".join(errors)
        + "\nSet GEMINI_API_KEY or GROQ_API_KEY, or run `ollama serve` with llama3.1:8b pulled."
    )
