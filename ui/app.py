from pathlib import Path
import tkinter as tk
from tkinter import ttk

from config import FONT_SIZES, LANGUAGES, SAVE_FILE, STRINGS, THEMES, ThemePalette
from storage import (
    load_ai_cache,
    load_archived_words,
    load_saved_words,
    load_settings,
    save_ai_cache,
    save_archived_words,
    save_settings,
    save_words_to_file,
)
from translator import translate_and_examples_with_bkrs, translate_text
from ui.detail_view import WordDetailView
from ui.list_view import WordListView
from ui.settings_view import SettingsView
from win32_capture import (
    HotkeyListener,
    close_existing_instance,
    enable_high_dpi,
    set_window_titlebar_theme,
)


class VocabularyApp:
    def __init__(self):
        close_existing_instance()
        enable_high_dpi()

        self.settings: dict = load_settings()
        self.entries: list[tuple[str, str]] = load_saved_words(self.save_file_path)
        self.archived_entries: list[tuple[str, str]] = load_archived_words()
        self.ai_cache: dict[str, str] = load_ai_cache()
        self.showing_archive: bool = False
        self.selected_index: int | None = None
        self.selected_from_archive: bool = False
        self.current_view: str = "list"

        self.root = tk.Tk()
        self.root.geometry("620x580")
        self.root.minsize(500, 440)
        self.root.attributes("-topmost", bool(self.settings.get("always_on_top", False)))

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.list_view = WordListView(self.root, self)
        self.detail_view = WordDetailView(self.root, self)
        self.settings_view = SettingsView(self.root, self)

        self.hotkey_listener = HotkeyListener(
            get_hotkey_name=lambda: self.settings.get("hotkey", "Ctrl + Q"),
            on_text_captured=self._on_hotkey_captured_text,
        )

        self._apply_theme()
        self._apply_localization()
        self.show_list_view()

    @property
    def theme(self) -> ThemePalette:
        theme_name = self.settings.get("theme", "Dark")
        return THEMES.get(theme_name, THEMES["Dark"])

    @property
    def font_family(self) -> str:
        return self.settings.get("font_family", "Calibri")

    @property
    def font_size(self) -> str:
        size_name = self.settings.get("font_size", "Medium")
        return size_name if size_name in FONT_SIZES else "Medium"

    @property
    def font_scale(self) -> dict[str, int]:
        return FONT_SIZES[self.font_size]

    @property
    def save_file_path(self) -> str:
        return str(self.settings.get("save_file_path", str(SAVE_FILE))).strip() or str(SAVE_FILE)

    # -----------------------------------------------------------------
    # Persistent AI Response Cache (Stored in ai_cache.json, not .txt)
    # -----------------------------------------------------------------

    def _ai_cache_key(self, word: str, action_key: str) -> str:
        return f"{word.strip().lower()}||{action_key}"

    def get_cached_ai_answer(self, word: str, action_key: str) -> str | None:
        return self.ai_cache.get(self._ai_cache_key(word, action_key))

    def set_cached_ai_answer(self, word: str, action_key: str, response: str) -> None:
        self.ai_cache[self._ai_cache_key(word, action_key)] = response
        save_ai_cache(self.ai_cache)

    # -----------------------------------------------------------------
    # Theme & Localization
    # -----------------------------------------------------------------

    def toggle_theme(self) -> None:
        next_theme = "Light" if self.theme.is_dark else "Dark"
        self.update_settings({"theme": next_theme})
        self.settings_view.sync_vars_from_settings()

    def _apply_theme(self) -> None:
        t = self.theme
        self.root.configure(bg=t.BG_MAIN)

        self.style.configure(
            "Modern.TCombobox",
            fieldbackground=t.BG_INPUT,
            background=t.BG_INPUT,
            foreground=t.FG_WORD,
            arrowcolor=t.ACCENT,
            bordercolor=t.BORDER,
            lightcolor=t.BORDER,
            darkcolor=t.BORDER,
            borderwidth=1,
            padding=5,
        )
        self.style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", t.BG_INPUT)],
            selectbackground=[("readonly", t.BG_INPUT)],
            selectforeground=[("readonly", t.FG_WORD)],
            bordercolor=[("focus", t.ACCENT)],
        )
        self.root.option_add("*TCombobox*Listbox.background", t.BG_CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", t.FG_WORD)
        self.root.option_add("*TCombobox*Listbox.selectBackground", t.ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", t.BG_HEADER)

        self.style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background=t.SCROLL_THUMB,
            troughcolor=t.BG_MAIN,
            bordercolor=t.BG_MAIN,
            lightcolor=t.SCROLL_THUMB,
            darkcolor=t.SCROLL_THUMB,
            arrowsize=0,
            width=8,
        )
        self.style.map(
            "Modern.Vertical.TScrollbar",
            background=[("active", t.ACCENT)],
        )

        self.list_view.apply_theme()
        self.detail_view.apply_theme()
        self.settings_view.apply_theme()

        self.root.update_idletasks()
        set_window_titlebar_theme(self.root.winfo_id(), t.is_dark)

    def t(self, key: str) -> str:
        """Return localized string for the current app language."""
        lang = self.settings.get("app_language", "English")
        table = STRINGS.get(lang, STRINGS["English"])
        return table.get(key, STRINGS["English"].get(key, key))

    def update_settings(self, new_values: dict) -> None:
        old_theme = self.settings.get("theme", "Dark")
        old_font = self.font_family
        old_font_size = self.font_size
        old_save_path = self.save_file_path

        self.settings.update(new_values)
        self.root.attributes("-topmost", bool(self.settings.get("always_on_top", False)))
        save_settings(self.settings)

        if self.save_file_path != old_save_path:
            target = Path(self.save_file_path)
            existing = load_saved_words(target) if target.exists() else []
            if existing:
                self.entries = existing
            else:
                save_words_to_file(self.entries, target)

        if self.font_family != old_font or self.font_size != old_font_size:
            self.list_view.apply_font()
            self.detail_view.apply_font()

        if self.settings.get("theme", "Dark") != old_theme:
            self._apply_theme()

        self._apply_localization()

    def _apply_localization(self) -> None:
        self.root.title(self.t("app_title"))
        self.list_view.apply_localization()
        self.detail_view.apply_localization()
        self.settings_view.apply_localization()
        if self.current_view == "list":
            self.list_view.refresh()

    # -----------------------------------------------------------------
    # View Switching
    # -----------------------------------------------------------------

    def _hide_all_views(self) -> None:
        self.list_view.pack_forget()
        self.detail_view.pack_forget()
        self.settings_view.pack_forget()

    def toggle_archive_view(self) -> None:
        self.showing_archive = not self.showing_archive
        self.list_view.refresh()

    def show_list_view(self) -> None:
        self.current_view = "list"
        self.selected_index = None
        self._hide_all_views()
        self.list_view.pack(fill=tk.BOTH, expand=True)
        self.list_view.refresh()

    def show_word_view(self, index: int) -> None:
        target_list = self.archived_entries if self.showing_archive else self.entries
        if not (0 <= index < len(target_list)):
            return
        self.current_view = "detail"
        self.selected_index = index
        self.selected_from_archive = self.showing_archive
        word, translation = target_list[index]
        self.detail_view.set_word(word, translation, is_archived=self.selected_from_archive, parent_word=None)

        self._hide_all_views()
        self.detail_view.pack(fill=tk.BOTH, expand=True)

    def show_subword_view(self, parent_index: int, sub_word: str, sub_translation: str) -> None:
        target_list = self.archived_entries if self.showing_archive else self.entries
        if not (0 <= parent_index < len(target_list)):
            return
        self.current_view = "detail"
        self.selected_index = parent_index
        self.selected_from_archive = self.showing_archive
        parent_word = target_list[parent_index][0]
        self.detail_view.set_word(
            sub_word,
            sub_translation,
            is_archived=self.selected_from_archive,
            parent_word=parent_word,
        )
        self._hide_all_views()
        self.detail_view.pack(fill=tk.BOTH, expand=True)

    def show_settings_view(self) -> None:
        self.current_view = "settings"
        self.settings_view.sync_vars_from_settings()
        self._hide_all_views()
        self.settings_view.pack(fill=tk.BOTH, expand=True)

    # -----------------------------------------------------------------
    # Word List, Archive & Reorder Operations
    # -----------------------------------------------------------------

    def _on_hotkey_captured_text(self, captured_text: str) -> None:
        target_lang_name = self.settings.get("target_language", "French")
        lang_code = LANGUAGES.get(target_lang_name, "fr")
        provider = self.settings.get("translation_source", "Google Translate")

        raw_lines = [
            " ".join(line.split())
            for line in captured_text.splitlines()
        ]
        words_to_add = [w for w in raw_lines if w]
        if not words_to_add:
            return

        for word in words_to_add:
            bkrs_examples = ""
            if provider == "BKRS (bkrs.info)":
                translation, bkrs_examples = translate_and_examples_with_bkrs(word)
            else:
                translation = translate_text(word, lang_code, provider=provider)
            self.root.after(0, self.add_entry, word, translation, bkrs_examples)

    def add_entry(self, word: str, translation: str, bkrs_examples: str = "") -> None:
        """Add or update a word in the active list and .txt file."""
        if bkrs_examples:
            self.set_cached_ai_answer(word, "btn_bkrs_examples", bkrs_examples)

        # If the word was previously archived, remove it from archive when re-captured
        self.archived_entries = [
            (w, t) for w, t in self.archived_entries if w.lower() != word.lower()
        ]
        save_archived_words(self.archived_entries)

        for i, (existing_word, _) in enumerate(self.entries):
            if existing_word.lower() == word.lower():
                self.entries[i] = (word, translation)
                save_words_to_file(self.entries, self.save_file_path)
                if self.current_view == "list":
                    self.list_view.refresh()
                return

        self.entries.append((word, translation))
        save_words_to_file(self.entries, self.save_file_path)
        if self.current_view == "list":
            self.list_view.refresh(scroll_to_bottom=True)

    def persist_current_list_order(self) -> None:
        """Persist the current active or archived word list order to disk."""
        if self.showing_archive:
            save_archived_words(self.archived_entries)
        else:
            save_words_to_file(self.entries, self.save_file_path)

    def move_entry(
        self, from_idx: int, to_idx: int, save: bool = True, update_ui_blocks: bool = True
    ) -> bool:
        """Reorder a word in the current list in-place without rebuilding the UI."""
        target_list = self.archived_entries if self.showing_archive else self.entries
        if not (0 <= from_idx < len(target_list) and 0 <= to_idx < len(target_list)):
            return False
        if from_idx == to_idx:
            return False

        item = target_list.pop(from_idx)
        target_list.insert(to_idx, item)

        if save:
            self.persist_current_list_order()

        if update_ui_blocks and self.current_view == "list":
            self.list_view.move_card_block(from_idx, to_idx)
        return True

    def archive_entry(self, index: int) -> None:
        """Move a word from the active list (.txt) to the archive."""
        if not (0 <= index < len(self.entries)):
            return
        word, translation = self.entries.pop(index)
        for i, (w, _) in enumerate(self.archived_entries):
            if w.lower() == word.lower():
                self.archived_entries[i] = (word, translation)
                break
        else:
            self.archived_entries.append((word, translation))

        save_words_to_file(self.entries, self.save_file_path)
        save_archived_words(self.archived_entries)
        self.list_view.refresh()

    def unarchive_entry(self, index: int) -> None:
        """Restore a word from the archive back to the active list and .txt file."""
        if not (0 <= index < len(self.archived_entries)):
            return
        word, translation = self.archived_entries.pop(index)
        for i, (w, _) in enumerate(self.entries):
            if w.lower() == word.lower():
                self.entries[i] = (word, translation)
                break
        else:
            self.entries.append((word, translation))

        save_archived_words(self.archived_entries)
        save_words_to_file(self.entries, self.save_file_path)
        self.list_view.refresh()

    def toggle_archive_current_word(self) -> None:
        if self.selected_index is None:
            return
        idx = self.selected_index
        from_archive = self.selected_from_archive
        self.show_list_view()
        if from_archive:
            self.unarchive_entry(idx)
        else:
            self.archive_entry(idx)

    def delete_entry(self, index: int, from_archive: bool | None = None) -> None:
        is_arch = self.showing_archive if from_archive is None else from_archive
        target_list = self.archived_entries if is_arch else self.entries
        if 0 <= index < len(target_list):
            target_list.pop(index)
            if is_arch:
                save_archived_words(self.archived_entries)
            else:
                save_words_to_file(self.entries, self.save_file_path)
            self.list_view.refresh()

    def delete_current_word(self) -> None:
        if self.selected_index is not None:
            idx = self.selected_index
            from_archive = self.selected_from_archive
            parent_w = getattr(self.detail_view, "parent_word", None)
            target_list = self.archived_entries if from_archive else self.entries
            if parent_w and 0 <= idx < len(target_list) and target_list[idx][0] == parent_w:
                sub_w = self.detail_view.current_word
                parent_word, full_trans = target_list[idx]
                lines = [l for l in full_trans.splitlines() if l.strip()]
                remaining = [l for l in lines if not l.strip().startswith(sub_w)]
                if not remaining:
                    self.show_list_view()
                    self.delete_entry(idx, from_archive=from_archive)
                else:
                    target_list[idx] = (parent_word, "\n".join(remaining))
                    if from_archive:
                        save_archived_words(self.archived_entries)
                    else:
                        save_words_to_file(self.entries, self.save_file_path)
                    self.show_list_view()
                return

            self.show_list_view()
            self.delete_entry(idx, from_archive=from_archive)

    def clear_all(self) -> None:
        if self.showing_archive:
            self.archived_entries.clear()
            save_archived_words(self.archived_entries)
        else:
            self.entries.clear()
            save_words_to_file(self.entries, self.save_file_path)
        self.list_view.refresh()

    def run(self) -> None:
        self.hotkey_listener.start()
        self.root.mainloop()


