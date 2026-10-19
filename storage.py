import json
from pathlib import Path
from config import (
    AI_CACHE_FILE,
    ARCHIVED_FILE,
    DEFAULT_SETTINGS,
    HEADER_LINE,
    SAVE_FILE,
    SETTINGS_FILE,
)


def load_settings() -> dict:
    """Load user settings from settings.json, falling back to defaults."""
    settings = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        try:
            loaded = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                settings.update(loaded)
        except Exception:
            pass
    if not str(settings.get("save_file_path", "")).strip():
        settings["save_file_path"] = str(SAVE_FILE)
    return settings


def save_settings(settings: dict) -> None:
    """Persist user settings to settings.json."""
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def resolve_save_file(file_path: str | Path | None = None) -> Path:
    """Resolve the target .txt file path from argument, settings, or default."""
    if file_path and str(file_path).strip():
        return Path(str(file_path).strip())
    settings = load_settings()
    custom = str(settings.get("save_file_path", "")).strip()
    return Path(custom) if custom else SAVE_FILE


def format_words_for_file(entries: list[tuple[str, str]]) -> str:
    """Format the vocabulary list into a clean, human-readable .txt file."""
    if not entries:
        return "No words saved yet.\n"

    lines = [
        HEADER_LINE,
        f"  WORDS TO LEARN ({len(entries)})",
        HEADER_LINE,
        "",
    ]
    for word, translation in entries:
        lines.append(f"  • {word}  ➔  {translation}")

    return "\n".join(lines) + "\n"


def load_saved_words(file_path: str | Path | None = None) -> list[tuple[str, str]]:
    """Load saved (word, translation) pairs from the configured .txt file."""
    target = resolve_save_file(file_path)
    if not target.exists():
        return []
    entries: list[tuple[str, str]] = []
    try:
        for line in target.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("•") and "➔" in stripped:
                left, right = stripped[1:].split("➔", 1)
                word, translation = left.strip(), right.strip()
                if word:
                    entries.append((word, translation))
    except Exception:
        pass
    return entries


def save_words_to_file(
    entries: list[tuple[str, str]], file_path: str | Path | None = None
) -> None:
    """Save the formatted vocabulary list to the configured .txt file."""
    target = resolve_save_file(file_path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(format_words_for_file(entries), encoding="utf-8")
    except Exception:
        pass


def load_archived_words() -> list[tuple[str, str]]:
    """Load archived (word, translation) pairs from archived_words.json."""
    if not ARCHIVED_FILE.exists():
        return []
    try:
        data = json.loads(ARCHIVED_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [
                (str(item[0]), str(item[1]))
                for item in data
                if isinstance(item, (list, tuple)) and len(item) >= 2 and str(item[0]).strip()
            ]
    except Exception:
        pass
    return []


def save_archived_words(entries: list[tuple[str, str]]) -> None:
    """Persist archived words to archived_words.json (never written to .txt)."""
    try:
        ARCHIVED_FILE.write_text(
            json.dumps([[w, t] for w, t in entries], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


def load_ai_cache() -> dict[str, str]:
    """Load stored AI responses from ai_cache.json."""
    if not AI_CACHE_FILE.exists():
        return {}
    try:
        data = json.loads(AI_CACHE_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items() if v}
    except Exception:
        pass
    return {}


def save_ai_cache(cache: dict[str, str]) -> None:
    """Persist stored AI responses to ai_cache.json (never written to .txt)."""
    try:
        AI_CACHE_FILE.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass



