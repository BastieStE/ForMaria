# =====================================================================
# Language-Dependent AI Prompts (English & Русский)
# =====================================================================
# Available placeholders in templates:
#   {word}        -> The selected word or phrase
#   {translation} -> The dictionary/initial translation
#   {question}    -> The user's custom question (for the 4th button)

SYSTEM_PROMPTS: dict[str, str] = {
    "English": (
        "You are an expert, concise language tutor. "
        "Format your answers clearly using clean bullet points and numbered lists. "
        "Avoid markdown tables and unnecessary filler."
    ),
    "Русский": (
        "Ты — опытный и лаконичный преподаватель языков. "
        "Оформляй ответы чётко, используя списки и понятную структуру. "
        "Не используй таблицы markdown и избегай лишней воды."
    ),
}

PROMPTS: dict[str, dict[str, str]] = {
    "English": {
        "btn_explain": (
            'Explain the word or phrase "{word}" (current translation: "{translation}") for a language learner.\n'
            "Respond in English, concisely and clearly using this structure:\n"
            "1. Core Meaning & Part of Speech: What it really means and its grammatical role.\n"
            "2. Breakdown / Literal Meaning: Character-by-character breakdown with Pinyin (if Chinese) or word roots/morphology.\n"
            "3. Register & Usage: When to use it (formal, casual, spoken, written) and 2–3 common collocations."
        ),
        "btn_examples": (
            'Give 4 natural example sentences using the word or phrase "{word}" (meaning: "{translation}") '
            "in different everyday contexts.\n"
            "For each example provide:\n"
            "• The sentence in the original language (include Pinyin if it is Chinese)\n"
            "• The English translation\n"
            '• A brief 1-line note on the nuance or grammar structure of "{word}" in that sentence.'
        ),
        "btn_synonyms": (
            'List the closest synonyms and antonyms for "{word}" (meaning: "{translation}") '
            "and explain the subtle differences in nuance.\n"
            "Respond in English with:\n"
            '1. Close Synonyms (2–3 words): Include Pinyin/pronunciation if applicable, and clearly explain how each differs from "{word}" in meaning, tone, or usage.\n'
            "2. Antonyms (1–2 words): Opposite words with brief translations."
        ),
        "btn_ask": (
            'Regarding the word or phrase "{word}" (translation: "{translation}"):\n'
            "User question: {question}\n\n"
            "Answer clearly and concisely in English."
        ),
    },
    "Русский": {
        "btn_explain": (
            "Объясни слово или фразу «{word}» (текущий перевод: «{translation}») для изучающего язык.\n"
            "Отвечай на русском языке, кратко, наглядно и по делу, по следующей структуре:\n"
            "1. Основное значение и часть речи: суть слова и его грамматическая роль.\n"
            "2. Разбор / Буквальный смысл: посимвольный разбор иероглифов с пиньинем (если это китайский) или корни/структура слова.\n"
            "3. Употребление и стиль: в каких ситуациях используется (разговорная, книжная, официальная речь) и 2–3 частых словосочетания."
        ),
        "btn_examples": (
            "Приведи 4 естественных примера предложений со словом или фразой «{word}» (значение: «{translation}») "
            "в разных жизненных ситуациях.\n"
            "Для каждого примера укажи:\n"
            "• Предложение на языке оригинала (если это китайский — обязательно добавь пиньинь)\n"
            "• Перевод на русский язык\n"
            "• Короткое пояснение (в 1 строку) об оттенке смысла или грамматической конструкции."
        ),
        "btn_synonyms": (
            "Подбери ближайшие синонимы и антонимы к слову «{word}» (значение: «{translation}») "
            "и объясни разницу в оттенках смысла.\n"
            "Отвечай на русском языке по структуре:\n"
            "1. Близкие синонимы (2–3 слова): укажи пиньинь/транскрипцию (если нужно) и чётко объясни, чем каждый синоним отличается от «{word}» по смыслу, стилю или сочетаемости.\n"
            "2. Антонимы (1–2 слова): слова с противоположным значением и их перевод."
        ),
        "btn_ask": (
            "Контекст — изучаемое слово или фраза «{word}» (перевод: «{translation}»).\n"
            "Вопрос пользователя: {question}\n\n"
            "Ответь чётко, понятно и по делу на русском языке."
        ),
    },
}


def build_prompt(app_language: str, action_key: str, word: str, translation: str, question: str = "") -> tuple[str, str]:
    """Return (system_prompt, user_prompt) in the selected app language (English or Русский)."""
    lang = app_language if app_language in PROMPTS else "English"
    system_prompt = SYSTEM_PROMPTS[lang]
    template = PROMPTS[lang].get(action_key, PROMPTS[lang]["btn_explain"])
    user_prompt = template.format(word=word, translation=translation, question=question)
    return system_prompt, user_prompt

