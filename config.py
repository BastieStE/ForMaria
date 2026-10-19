from dataclasses import dataclass
from pathlib import Path
import sys

# =====================================================================
# Paths & Formatting Constants
# =====================================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
SAVE_FILE = BASE_DIR / "saved_words.txt"
SETTINGS_FILE = BASE_DIR / "settings.json"
AI_CACHE_FILE = BASE_DIR / "ai_cache.json"
ARCHIVED_FILE = BASE_DIR / "archived_words.json"
HEADER_LINE = "=" * 56

WINDOW_TITLES = ("Words to Learn", "Словарь", "Слова для изучения", "Selected Text Viewer")

FONT_WORD = "Microsoft YaHei UI"
FONT_TRANSLATION = "Calibri"

FONT_OPTIONS: list[str] = [
    "Calibri",
    "Microsoft YaHei UI",
    "Segoe UI",
    "Arial",
    "Verdana",
    "Tahoma",
    "Georgia",
    "Consolas",
]

# =====================================================================
# Hotkey & Language Options
# =====================================================================

MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000

HOTKEY_OPTIONS: dict[str, tuple[int, int]] = {
    "Ctrl + Q": (MOD_CONTROL | MOD_NOREPEAT, ord("Q")),
    "Ctrl + B": (MOD_CONTROL | MOD_NOREPEAT, ord("B")),
    "Ctrl + Space": (MOD_CONTROL | MOD_NOREPEAT, 0x20),
    "F8": (MOD_NOREPEAT, 0x77),
    "F9": (MOD_NOREPEAT, 0x78),
}

LANGUAGES: dict[str, str] = {
    "Russian": "ru",
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Dutch": "nl",
    "Polish": "pl",
    "Arabic": "ar",
    "Japanese": "ja",
    "Chinese": "zh-CN",
}

AI_PROVIDERS: dict[str, list[str]] = {
    "Google Gemini": [
        "gemini-3.8-flash",
        "gemini-4-argon",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
    ],
    "OpenAI": ["gpt-4o-mini", "gpt-4o"],
    "Anthropic Claude": ["claude-3-5-haiku-latest", "claude-3-7-sonnet-latest"],
    "DeepSeek": ["deepseek-chat", "deepseek-reasoner"],
}

TRANSLATION_SOURCES: list[str] = [
    "Google Translate",
    "BKRS (bkrs.info)",
]

DEFAULT_SETTINGS: dict = {
    "app_language": "English",
    "translation_source": "Google Translate",
    "target_language": "French",
    "hotkey": "Ctrl + Q",
    "theme": "Dark",
    "font_family": "Calibri",
    "save_file_path": str(SAVE_FILE),
    "always_on_top": False,
    "ai_provider": "Google Gemini",
    "ai_model": "gemini-3.8-flash",
    "api_key": "",
}

# =====================================================================
# Modern Dual-Theme Palette (Dark & Light)
# =====================================================================

@dataclass(frozen=True)
class ThemePalette:
    name: str
    is_dark: bool
    BG_MAIN: str
    BG_HEADER: str
    BG_CARD: str
    BG_CARD_HOVER: str
    BORDER: str
    BORDER_HOVER: str
    BG_INPUT: str
    BG_BTN_SECONDARY: str
    BG_BTN_HOVER: str
    BG_BTN_DISABLED: str
    FG_WORD: str
    FG_TRANSLATION: str
    FG_SUBTLE: str
    FG_DISABLED: str
    ACCENT: str
    ACCENT_HOVER: str
    ACCENT_SOFT: str
    DANGER: str
    DANGER_SOFT: str
    SCROLL_THUMB: str


THEMES: dict[str, ThemePalette] = {
    "Dark": ThemePalette(
        name="Dark",
        is_dark=True,
        BG_MAIN="#0F111A",
        BG_HEADER="#151824",
        BG_CARD="#181C2A",
        BG_CARD_HOVER="#21263A",
        BORDER="#252B42",
        BORDER_HOVER="#3B4468",
        BG_INPUT="#202538",
        BG_BTN_SECONDARY="#202538",
        BG_BTN_HOVER="#2C334D",
        BG_BTN_DISABLED="#161926",
        FG_WORD="#F3F4F6",
        FG_TRANSLATION="#34D399",
        FG_SUBTLE="#8E96B5",
        FG_DISABLED="#4A516D",
        ACCENT="#818CF8",
        ACCENT_HOVER="#6366F1",
        ACCENT_SOFT="#222647",
        DANGER="#F43F5E",
        DANGER_SOFT="#331A26",
        SCROLL_THUMB="#2A3047",
    ),
    "Light": ThemePalette(
        name="Light",
        is_dark=False,
        BG_MAIN="#F4F6FB",
        BG_HEADER="#FFFFFF",
        BG_CARD="#FFFFFF",
        BG_CARD_HOVER="#EEF2FF",
        BORDER="#E2E8F0",
        BORDER_HOVER="#C7D2FE",
        BG_INPUT="#F1F5F9",
        BG_BTN_SECONDARY="#F1F5F9",
        BG_BTN_HOVER="#E2E8F0",
        BG_BTN_DISABLED="#EDF1F7",
        FG_WORD="#0F172A",
        FG_TRANSLATION="#059669",
        FG_SUBTLE="#64748B",
        FG_DISABLED="#94A3B8",
        ACCENT="#4F46E5",
        ACCENT_HOVER="#4338CA",
        ACCENT_SOFT="#EEF2FF",
        DANGER="#E11D48",
        DANGER_SOFT="#FFE4E6",
        SCROLL_THUMB="#CBD5E1",
    ),
}

# =====================================================================
# UI Localization (English & Russian)
# =====================================================================

STRINGS: dict[str, dict[str, str]] = {
    "English": {
        "app_title": "Words to Learn",
        "archive_title": "Archived Words",
        "archive_btn": "📦 Archive ({count})",
        "active_words_btn": "← Active ({count})",
        "settings_btn": "Settings",
        "clear_btn": "Clear",
        "header_hint_google": "Press {hotkey} on any selected text  •  Google Translate → {lang}  •  Drag ⠿ or ▲▼ to reorder",
        "header_hint_bkrs": "Press {hotkey} on any selected text  •  BKRS (ZH ↔ RU)  •  Drag ⠿ or ▲▼ to reorder",
        "header_hint_archive": "Archived words are hidden from your main list and .txt file.",
        "search_placeholder": "Search original words or translations...",
        "no_search_results": "No matching words found.",
        "empty_title": "No words saved yet",
        "empty_list": "Highlight any unfamiliar word while reading and press {hotkey} to add it here.",
        "empty_archive_title": "No archived words",
        "empty_archive_list": "Archive words you have already learned to hide them from your main list and .txt file.",
        "back_to_list": "← Back",
        "archive_word": "📥 Archive",
        "unarchive_word": "↩ Restore",
        "remove_word": "Delete",
        "lbl_original": "ORIGINAL",
        "lbl_translated": "TRANSLATION",
        "ai_tools_header": "AI & DICTIONARY TOOLS",
        "btn_explain": "✨  Explain Meaning",
        "btn_examples": "📖  Context Examples",
        "btn_synonyms": "🔤  Synonyms & Nuances",
        "btn_ask": "💬  Ask AI a Question",
        "btn_bkrs_examples": "📚  BKRS Examples (bkrs.info)",
        "bkrs_loading": "⏳ Fetching examples from bkrs.info...",
        "bkrs_no_examples": "No examples found on BKRS for «{word}».",
        "ai_cached_prompt": "A saved AI answer already exists for this tool:",
        "btn_show_cached": "📂 Show Saved Answer",
        "btn_generate_new": "🔄 Generate New",
        "ai_placeholder": "Click any tool above to get AI explanations, usage examples, or BKRS dictionary examples.",
        "ai_thinking": "⏳ Generating response with {model}...",
        "ask_placeholder": "Ask anything about this word...",
        "btn_send": "Ask",
        "settings_title": "Settings",
        "sec_general": "APPEARANCE & TRANSLATION",
        "lbl_theme": "Appearance Theme",
        "lbl_app_lang": "Interface Language",
        "lbl_font": "Text Font",
        "lbl_trans_source": "Translation Source",
        "lbl_target_lang": "Target Language (Google)",
        "lbl_hotkey": "Capture Shortcut",
        "lbl_save_file": "Words File (.txt)",
        "btn_browse": "Browse...",
        "dlg_save_file_title": "Select or Create Words (.txt) File",
        "lbl_always_on_top": "Keep window pinned on top of other apps",
        "sec_ai": "AI ASSISTANT CONFIGURATION",
        "lbl_ai_provider": "AI Provider",
        "lbl_ai_model": "Model",
        "lbl_api_key": "API Key",
        "btn_show": "Show",
        "btn_hide": "Hide",
        "status_saved": "✓ Saved",
    },
    "Русский": {
        "app_title": "Словарь",
        "archive_title": "Архив слов",
        "archive_btn": "📦 Архив ({count})",
        "active_words_btn": "← Активные ({count})",
        "settings_btn": "Настройки",
        "clear_btn": "Очистить",
        "header_hint_google": "Нажмите {hotkey} на слове  •  Google → {lang}  •  Тяните ⠿ или ▲▼ для сортировки",
        "header_hint_bkrs": "Нажмите {hotkey} на слове  •  БКРС (ZH ↔ RU)  •  Тяните ⠿ или ▲▼ для сортировки",
        "header_hint_archive": "Архивные слова скрыты из основного списка и .txt файла.",
        "search_placeholder": "Поиск по словам или переводу...",
        "no_search_results": "Совпадений не найдено.",
        "empty_title": "Список слов пока пуст",
        "empty_list": "Выделите незнакомое слово при чтении и нажмите {hotkey}, чтобы добавить его.",
        "empty_archive_title": "Архив пуст",
        "empty_archive_list": "Отправляйте выученные слова в архив, чтобы скрыть их из основного списка и .txt файла.",
        "back_to_list": "← Назад",
        "archive_word": "📥 В архив",
        "unarchive_word": "↩ Вернуть",
        "remove_word": "Удалить",
        "lbl_original": "ОРИГИНАЛ",
        "lbl_translated": "ПЕРЕВОД",
        "ai_tools_header": "ИНСТРУМЕНТЫ ИИ И БКРС",
        "btn_explain": "✨  Объяснить значение",
        "btn_examples": "📖  Примеры в контексте",
        "btn_synonyms": "🔤  Синонимы и оттенки",
        "btn_ask": "💬  Задать вопрос ИИ",
        "btn_bkrs_examples": "📚  Примеры из БКРС (bkrs.info)",
        "bkrs_loading": "⏳ Загрузка примеров с bkrs.info...",
        "bkrs_no_examples": "На БКРС не найдено примеров для «{word}».",
        "ai_cached_prompt": "Для этого инструмента уже есть сохранённый ответ ИИ:",
        "btn_show_cached": "📂 Показать сохранённый",
        "btn_generate_new": "🔄 Сгенерировать новый",
        "ai_placeholder": "Нажмите на любой инструмент выше, чтобы получить разбор от ИИ или примеры из БКРС.",
        "ai_thinking": "⏳ ИИ ({model}) формирует ответ...",
        "ask_placeholder": "Задайте любой вопрос об этом слове...",
        "btn_send": "Спросить",
        "settings_title": "Настройки",
        "sec_general": "ОФОРМЛЕНИЕ И ПЕРЕВОД",
        "lbl_theme": "Тема оформления",
        "lbl_app_lang": "Язык интерфейса",
        "lbl_font": "Шрифт текста",
        "lbl_trans_source": "Источник перевода",
        "lbl_target_lang": "Язык перевода (Google)",
        "lbl_hotkey": "Горячая клавиша",
        "lbl_save_file": "Файл словаря (.txt)",
        "btn_browse": "Обзор...",
        "dlg_save_file_title": "Выберите или создайте файл словаря (.txt)",
        "lbl_always_on_top": "Закрепить окно поверх всех приложений",
        "sec_ai": "НАСТРОЙКИ ИИ (AI)",
        "lbl_ai_provider": "Провайдер ИИ",
        "lbl_ai_model": "Модель",
        "lbl_api_key": "API-ключ",
        "btn_show": "Показать",
        "btn_hide": "Скрыть",
        "status_saved": "✓ Сохранено",
    },
}
