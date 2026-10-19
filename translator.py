import html
import json
import re
import urllib.parse
import urllib.request

_bkrs_cookie: str = ""


def translate_text(text: str, target_lang: str, provider: str = "Google Translate") -> str:
    """Translate text using the selected translation provider."""
    if provider == "BKRS (bkrs.info)":
        return translate_with_bkrs(text)
    return translate_with_google(text, target_lang)


def translate_with_google(text: str, target_lang: str) -> str:
    """Translate text using Google Translate's free endpoint (auto-detect source)."""
    try:
        query = urllib.parse.quote(text)
        url = (
            f"https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=auto&tl={target_lang}&dt=t&q={query}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            translated = "".join(part[0] for part in data[0] if part[0])
            return translated.strip() or "..."
    except Exception:
        return "(Translation unavailable)"


def _fetch_bkrs_html(text: str) -> str:
    """Fetch lookup HTML from bkrs.info, automatically handling its lightweight JS cookie check."""
    global _bkrs_cookie
    url = f"https://bkrs.info/slovo.php?ch={urllib.parse.quote(text.strip())}"
    headers = {"User-Agent": "Mozilla/5.0"}
    if _bkrs_cookie:
        headers["Cookie"] = _bkrs_cookie

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=6) as resp:
        page = resp.read().decode("utf-8", errors="replace")

    # If bkrs.info returns the lightweight cookie challenge page, grab the 'ca=' cookie and retry once
    if "document.cookie" in page and "slovo.php" not in page:
        match = re.search(r"ca=([a-fA-F0-9]+)", page)
        if match:
            _bkrs_cookie = f"ca={match.group(1)}"
            headers["Cookie"] = _bkrs_cookie
            req2 = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req2, timeout=6) as resp2:
                page = resp2.read().decode("utf-8", errors="replace")

    return page


def _extract_balanced_div(html_str: str, start_idx: int) -> str:
    """Extract the inner HTML of a <div> starting at start_idx by balancing nested <div> tags."""
    tag_open = html_str.find(">", start_idx)
    if tag_open == -1:
        return ""
    pos = tag_open + 1
    depth = 1
    tag_pattern = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
    for match in tag_pattern.finditer(html_str, pos):
        token = match.group(0).lower()
        if token.startswith("</div"):
            depth -= 1
            if depth == 0:
                return html_str[pos : match.start()]
        else:
            depth += 1
    return html_str[pos:]


def _clean_bkrs_block(raw_html: str, max_lines: int = 3) -> str:
    """Remove example blocks (<div class='m2/m3/ex'>), strip HTML tags, and format cleanly."""
    cleaned = raw_html
    # Remove nested example divs (class="m2", "m3", "ex")
    for cls in ("ex", "m2", "m3"):
        while True:
            m = re.search(rf"<div[^>]*class=['\"][^'\"]*\b{cls}\b[^'\"]*['\"][^>]*>", cleaned, re.IGNORECASE)
            if not m:
                break
            inner = _extract_balanced_div(cleaned, m.start())
            full_end = cleaned.find("</div>", m.start() + len(inner))
            if full_end == -1:
                break
            cleaned = cleaned[: m.start()] + cleaned[full_end + 6 :]

    # Turn block boundaries into line breaks
    cleaned = re.sub(r"<br\s*/?>|</div>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = html.unescape(cleaned)

    lines = []
    for line in cleaned.splitlines():
        s = " ".join(line.split())
        # Remove leading dictionary sense numbers like "1)", "2)", "1.", "I)"
        s = re.sub(r"^\s*(?:\(\d+\)|\d+[\)\.]|[IVX]+[\)\.])\s*", "", s).strip()
        if s:
            lines.append(s)
        if len(lines) >= max_lines:
            break

    return "; ".join(lines)


def _extract_bkrs_translation_from_page(page: str) -> str:
    """Parse the primary translation string from a fetched bkrs.info HTML page."""
    # Case 1: Direct Chinese -> Russian headword (<div class='py'> + <div class='ru'>)
    ru_match = re.search(r"<div\s+class=['\"]ru['\"][^>]*>", page)
    if ru_match:
        py_text = ""
        py_match = re.search(r"<div\s+class=['\"]py['\"][^>]*>", page)
        if py_match and py_match.start() < ru_match.start():
            py_inner = _extract_balanced_div(page, py_match.start())
            py_clean = " ".join(html.unescape(re.sub(r"<[^>]+>", "", py_inner)).split())
            if py_clean:
                py_text = f"[{py_clean}] "

        ru_inner = _extract_balanced_div(page, ru_match.start())
        meaning = _clean_bkrs_block(ru_inner, max_lines=3)
        if meaning:
            return f"{py_text}{meaning}"

    # Case 2: Direct Russian -> Chinese headword (<div class='ch_ru'>)
    ch_ru_match = re.search(r"<div\s+class=['\"]ch_ru['\"][^>]*>", page)
    if ch_ru_match:
        ch_ru_inner = _extract_balanced_div(page, ch_ru_match.start())
        meaning = _clean_bkrs_block(ch_ru_inner, max_lines=3)
        if meaning:
            return meaning

    # Case 3: Multi-word segmented Chinese lookup (<table class='tbl_bywords'>)
    if "tbl_bywords" in page:
        words = re.findall(
            r"<td[^>]*class=['\"][^'\"]*ch3[^'\"]*['\"][^>]*>.*?<a[^>]*>(.*?)</a>",
            page,
            flags=re.DOTALL,
        )
        trans_cells = re.findall(
            r"<td[^>]*class=['\"][^'\"]*td_trans[^'\"]*['\"][^>]*>(.*?)</td>",
            page,
            flags=re.DOTALL,
        )
        parts = []
        for w, cell in zip(words, trans_cells):
            py_m = re.search(r"<center>(.*?)</center>", cell, flags=re.DOTALL)
            py_str = html.unescape(re.sub(r"<[^>]+>", "", py_m.group(1))).strip() if py_m else ""
            cell_without_py = re.sub(r"<center>.*?</center>", "", cell, flags=re.DOTALL)
            meaning = _clean_bkrs_block(cell_without_py, max_lines=1)
            w_clean = html.unescape(re.sub(r"<[^>]+>", "", w)).strip()
            if py_str:
                parts.append(f"{w_clean} [{py_str}] {meaning}")
            else:
                parts.append(f"{w_clean}: {meaning}")
        if parts:
            return "  |  ".join(parts)

    return "(Not found on BKRS)"


def _extract_bkrs_examples_from_page(page: str, max_examples: int = 12) -> str:
    """Extract dictionary collocations and bilingual sentence examples from a bkrs.info HTML page."""
    collocations: list[str] = []
    sentences: list[tuple[str, str]] = []

    # 1. Extract inline dictionary examples (<div class="ex"> inside the main definition block)
    ru_match = re.search(r"<div\s+class=['\"](?:ru|ch_ru)['\"][^>]*>", page)
    if ru_match:
        def_inner = _extract_balanced_div(page, ru_match.start())
        for ex_m in re.finditer(r"<div[^>]*class=['\"][^'\"]*\bex\b[^'\"]*['\"][^>]*>", def_inner, re.IGNORECASE):
            ex_html = _extract_balanced_div(def_inner, ex_m.start())
            ex_text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", ex_html)).split()).strip()
            if ex_text and ex_text not in collocations:
                collocations.append(ex_text)
            if len(collocations) >= 6:
                break

    # 2. Extract bilingual example sentences from <div id='examples'>
    ex_sec = re.search(r"<div\s+id=['\"]examples['\"][^>]*>", page, re.IGNORECASE)
    if ex_sec:
        ex_block = _extract_balanced_div(page, ex_sec.start())
        for item_m in re.finditer(r"<div\s+exact=['\"][01]['\"][^>]*>", ex_block, re.IGNORECASE):
            item_html = _extract_balanced_div(ex_block, item_m.start())
            sub_divs = re.findall(r"<div[^>]*>(.*?)</div>", item_html, flags=re.DOTALL | re.IGNORECASE)
            if len(sub_divs) >= 2:
                orig = " ".join(html.unescape(re.sub(r"<[^>]+>", "", sub_divs[0])).split()).strip()
                trans = " ".join(html.unescape(re.sub(r"<[^>]+>", "", sub_divs[1])).split()).strip()
                if orig and trans:
                    sentences.append((orig, trans))
            if len(sentences) >= max_examples:
                break

    if not collocations and not sentences:
        return ""

    out_lines: list[str] = []
    if collocations:
        out_lines.append("### Словарь (словосочетания БКРС)")
        for c in collocations:
            out_lines.append(f"• {c}")
        out_lines.append("")

    if sentences:
        out_lines.append("### Примеры предложений (БКРС)")
        for idx, (orig, trans) in enumerate(sentences, 1):
            out_lines.append(f"**{idx}. {orig}**")
            out_lines.append(f"   {trans}")
            out_lines.append("")

    return "\n".join(out_lines).strip()


def translate_with_bkrs(text: str) -> str:
    """Look up Chinese/Russian words directly on bkrs.info."""
    try:
        page = _fetch_bkrs_html(text)
        return _extract_bkrs_translation_from_page(page)
    except Exception:
        return "(BKRS lookup failed)"


def translate_and_examples_with_bkrs(text: str) -> tuple[str, str]:
    """Fetch both the BKRS translation and BKRS examples in a single HTTP request."""
    try:
        page = _fetch_bkrs_html(text)
        translation = _extract_bkrs_translation_from_page(page)
        examples = _extract_bkrs_examples_from_page(page)
        return translation, examples
    except Exception:
        return "(BKRS lookup failed)", ""


def fetch_bkrs_examples(text: str) -> str:
    """Fetch examples for a word from bkrs.info on demand."""
    try:
        page = _fetch_bkrs_html(text)
        examples = _extract_bkrs_examples_from_page(page)
        return examples
    except Exception:
        return ""

