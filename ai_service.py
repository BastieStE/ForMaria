import json
import urllib.error
import urllib.request


def query_ai(
    provider: str,
    model: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    app_language: str = "English",
) -> str:
    """Send a prompt to the configured AI provider and return the response text."""
    key = api_key.strip()
    if not key:
        if app_language == "Русский":
            return "⚠ Пожалуйста, укажите ваш API-ключ в меню «Настройки»."
        return "⚠ Please enter your API Key in the Settings menu first."

    model_name = model.strip()
    try:
        if provider == "DeepSeek":
            return _call_openai_compatible(
                url="https://api.deepseek.com/chat/completions",
                api_key=key,
                model=model_name or "deepseek-chat",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        if provider == "OpenAI":
            return _call_openai_compatible(
                url="https://api.openai.com/v1/chat/completions",
                api_key=key,
                model=model_name or "gpt-4o-mini",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        if provider == "Google Gemini":
            return _call_gemini(
                api_key=key,
                model=model_name or "gemini-3.8-flash",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        if provider == "Anthropic Claude":
            return _call_anthropic(
                api_key=key,
                model=model_name or "claude-3-5-haiku-latest",
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        return f"Unsupported provider: {provider}"

    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            raw = e.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and "error" in parsed:
                err_obj = parsed["error"]
                err_body = err_obj.get("message", str(err_obj)) if isinstance(err_obj, dict) else str(err_obj)
            else:
                err_body = raw[:300]
        except Exception:
            err_body = str(e)
        return f"⚠ API Error ({e.code}): {err_body}"
    except Exception as e:
        return f"⚠ Connection Error: {e}"


def _call_openai_compatible(
    url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Call OpenAI or DeepSeek (/chat/completions) API endpoint."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "WordsToLearn/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        message = body["choices"][0]["message"]
        content = message.get("content") or ""
        return content.strip()


def _call_gemini(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Call Google Gemini Interactions API (/v1beta/interactions)."""
    if model.startswith(("gemini-2.5", "gemini-2.0", "gemini-1.5")):
        model = "gemini-3.8-flash"

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    payload = {
        "model": model,
        "system_instruction": system_prompt,
        "input": user_prompt,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
            "Api-Revision": "2026-05-20",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        if "output_text" in body and body["output_text"]:
            return str(body["output_text"]).strip()

        texts: list[str] = []
        for step in body.get("steps", []):
            if step.get("type") == "model_output":
                for item in step.get("content", []):
                    if item.get("text"):
                        texts.append(item["text"])
        return "".join(texts).strip()


def _call_anthropic(
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """Call Anthropic Messages API endpoint."""
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return "".join(block.get("text", "") for block in body.get("content", [])).strip()
