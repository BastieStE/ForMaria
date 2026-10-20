import re
import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Callable

from ai_service import query_ai
from prompts import build_prompt
from translator import fetch_bkrs_examples

if TYPE_CHECKING:
    from ui.app import VocabularyApp


class WordDetailView(tk.Frame):
    def __init__(self, parent: tk.Misc, app: "VocabularyApp"):
        super().__init__(parent, bg=app.theme.BG_MAIN)
        self.app = app
        self.current_word: str = ""
        self.current_translation: str = ""
        self.is_archived: bool = False
        self.parent_word: str | None = None
        self.active_tool: str | None = None
        self._pending_show_cb: Callable[[], None] | None = None
        self._pending_gen_cb: Callable[[], None] | None = None
        self.ai_tool_frames: dict[str, tk.Frame] = {}
        self.ai_tool_buttons: dict[str, tk.Button] = {}
        self._build()

    def _build(self) -> None:
        t = self.app.theme
        font_family = self.app.font_family

        # --- Top Navigation Surface ---
        self.nav_bar = tk.Frame(self, bg=t.BG_HEADER, padx=22, pady=14)
        self.nav_bar.pack(fill=tk.X)

        self.btn_back = tk.Button(
            self.nav_bar,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg=t.ACCENT,
            bg=t.ACCENT_SOFT,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=5,
            command=self.app.show_list_view,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.btn_remove = tk.Button(
            self.nav_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.DANGER,
            bg=t.DANGER_SOFT,
            activebackground=t.DANGER,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.app.delete_current_word,
        )
        self.btn_remove.pack(side=tk.RIGHT)

        self.btn_archive_word = tk.Button(
            self.nav_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.app.toggle_archive_current_word,
        )
        self.btn_archive_word.pack(side=tk.RIGHT, padx=(0, 8))

        self.nav_border = tk.Frame(self, bg=t.BORDER, height=1)
        self.nav_border.pack(fill=tk.X)

        # --- Hero Word & Translation Card ---
        self.hero_card = tk.Frame(
            self,
            bg=t.BG_CARD,
            highlightbackground=t.BORDER,
            highlightthickness=1,
            padx=22,
            pady=12,
        )
        self.hero_card.pack(fill=tk.X, padx=20, pady=(12, 8))

        self.lbl_orig_tag = tk.Label(
            self.hero_card,
            text="",
            font=("Segoe UI", 8, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_CARD,
            anchor="w",
        )
        self.lbl_orig_tag.pack(fill=tk.X)

        self.word_label = tk.Label(
            self.hero_card,
            text="",
            font=(font_family, 18, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            anchor="w",
            justify=tk.LEFT,
            wraplength=520,
        )
        self.word_label.pack(fill=tk.X, pady=(2, 6))

        self.hero_divider = tk.Frame(self.hero_card, bg=t.BORDER, height=1)
        self.hero_divider.pack(fill=tk.X, pady=(0, 6))

        self.lbl_trans_tag = tk.Label(
            self.hero_card,
            text="",
            font=("Segoe UI", 8, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_CARD,
            anchor="w",
        )
        self.lbl_trans_tag.pack(fill=tk.X)

        self.translation_label = tk.Label(
            self.hero_card,
            text="",
            font=(font_family, 13),
            fg=t.FG_TRANSLATION,
            bg=t.BG_CARD,
            anchor="w",
            justify=tk.LEFT,
            wraplength=520,
        )
        self.translation_label.pack(fill=tk.X, pady=(2, 0))

        def _on_hero_configure(e):
            avail = max(e.width - 44, 250)
            self.word_label.configure(wraplength=avail)
            self.translation_label.configure(wraplength=avail)

        self.hero_card.bind("<Configure>", _on_hero_configure)

        # --- AI & BKRS Tools Section (Active Buttons) ---
        self.lbl_ai_tools_header = tk.Label(
            self,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_MAIN,
            anchor="w",
        )
        self.lbl_ai_tools_header.pack(fill=tk.X, padx=22, pady=(2, 4))

        self.btn_grid = tk.Frame(self, bg=t.BG_MAIN)
        self.btn_grid.pack(fill=tk.X, padx=16)
        self.btn_grid.columnconfigure(0, weight=1)
        self.btn_grid.columnconfigure(1, weight=1)

        tool_specs = [
            ("btn_explain", 0, 0, 1),
            ("btn_examples", 0, 1, 1),
            ("btn_synonyms", 1, 0, 1),
            ("btn_ask", 1, 1, 1),
            ("btn_bkrs_examples", 2, 0, 2),
        ]
        for key, r, c, colspan in tool_specs:
            frame = tk.Frame(
                self.btn_grid,
                bg=t.BG_CARD,
                highlightbackground=t.BORDER,
                highlightthickness=1,
            )
            frame.grid(row=r, column=c, columnspan=colspan, sticky="ew", padx=4, pady=3)
            self.ai_tool_frames[key] = frame

            btn = tk.Button(
                frame,
                text="",
                font=("Segoe UI", 10, "bold"),
                fg=t.FG_WORD,
                bg=t.BG_CARD,
                activebackground=t.ACCENT_SOFT,
                activeforeground=t.ACCENT,
                relief=tk.FLAT,
                bd=0,
                pady=6,
                cursor="hand2",
                command=lambda k=key: self._on_tool_clicked(k),
            )
            btn.pack(fill=tk.X)
            self.ai_tool_buttons[key] = btn

        # --- Stored Answer Choice Banner (Shown when a cached AI answer exists) ---
        self.choice_bar = tk.Frame(
            self,
            bg=t.BG_CARD,
            highlightbackground=t.ACCENT,
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        self.lbl_choice_prompt = tk.Label(
            self.choice_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            anchor="w",
        )
        self.lbl_choice_prompt.pack(fill=tk.X, pady=(0, 6))

        self.choice_btns_row = tk.Frame(self.choice_bar, bg=t.BG_CARD)
        self.choice_btns_row.pack(fill=tk.X)

        self.btn_show_cached = tk.Button(
            self.choice_btns_row,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.BG_HEADER,
            bg=t.ACCENT,
            activebackground=t.ACCENT_HOVER,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self._on_choose_show_cached,
        )
        self.btn_show_cached.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_generate_new = tk.Button(
            self.choice_btns_row,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self._on_choose_generate_new,
        )
        self.btn_generate_new.pack(side=tk.LEFT)

        # --- Custom Question Bar (Shown when 'Ask AI a Question' is clicked) ---
        self.ask_bar = tk.Frame(
            self,
            bg=t.BG_CARD,
            highlightbackground=t.ACCENT,
            highlightthickness=1,
            padx=8,
            pady=6,
        )
        self.var_question = tk.StringVar()
        self.entry_question = tk.Entry(
            self.ask_bar,
            textvariable=self.var_question,
            font=(font_family, 10),
            fg=t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            relief=tk.FLAT,
            bd=5,
        )
        self.entry_question.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_question.bind("<Return>", lambda _e: self._submit_custom_question())

        self.btn_send_question = tk.Button(
            self.ask_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.BG_HEADER,
            bg=t.ACCENT,
            activebackground=t.ACCENT_HOVER,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=5,
            command=self._submit_custom_question,
        )
        self.btn_send_question.pack(side=tk.RIGHT)

        # --- Scrollable AI Output Panel ---
        self.ai_panel = tk.Frame(
            self,
            bg=t.BG_CARD,
            highlightbackground=t.BORDER,
            highlightthickness=1,
        )
        self.ai_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(8, 16))

        self.ai_scrollbar = ttk.Scrollbar(
            self.ai_panel,
            orient=tk.VERTICAL,
            style="Modern.Vertical.TScrollbar",
        )
        self.ai_text = tk.Text(
            self.ai_panel,
            font=(font_family, 10),
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            insertbackground=t.FG_WORD,
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            padx=18,
            pady=14,
            spacing1=2,
            spacing3=4,
            yscrollcommand=self.ai_scrollbar.set,
            state=tk.DISABLED,
        )
        self.ai_scrollbar.configure(command=self.ai_text.yview)
        self.ai_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=2)
        self.ai_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._configure_text_tags()

    def _configure_text_tags(self) -> None:
        t = self.app.theme
        font_family = self.app.font_family
        scale = self.app.font_scale
        self.ai_text.tag_configure("heading", font=(font_family, scale["ai_heading"], "bold"), foreground=t.ACCENT)
        self.ai_text.tag_configure("bold", font=(font_family, scale["ai_text"], "bold"), foreground=t.FG_WORD)
        self.ai_text.tag_configure("subtle", font=(font_family, scale["ai_text"]), foreground=t.FG_SUBTLE)

    def apply_font(self) -> None:
        font_family = self.app.font_family
        scale = self.app.font_scale
        self.word_label.configure(font=(font_family, scale["detail_title"], "bold"))
        self.translation_label.configure(font=(font_family, scale["detail_trans"]))
        self.entry_question.configure(font=(font_family, scale["ai_text"]))
        self.ai_text.configure(font=(font_family, scale["ai_text"]))
        self._configure_text_tags()

    @staticmethod
    def _format_translation_list(translation: str) -> str:
        """If translation contains multiple lines or '|' segments, format them as a vertical list."""
        parts: list[str] = []
        for line in translation.splitlines():
            for seg in line.split("|"):
                cleaned = seg.strip()
                if cleaned:
                    parts.append(cleaned)
        if len(parts) > 1:
            return "\n".join(p if p.startswith("•") else f"•  {p}" for p in parts)
        return parts[0] if parts else translation

    def set_word(
        self,
        word: str,
        translation: str,
        is_archived: bool = False,
        parent_word: str | None = None,
    ) -> None:
        self.current_word = word
        self.current_translation = translation
        self.is_archived = is_archived
        self.parent_word = parent_word
        self.active_tool = None
        self.word_label.configure(text=word)
        self.translation_label.configure(text=self._format_translation_list(translation))
        self._update_orig_tag()
        self._update_archive_btn_label()
        self.choice_bar.pack_forget()
        self.ask_bar.pack_forget()
        self._update_button_highlights()
        self._set_ai_output(self.app.t("ai_placeholder"), is_subtle=True)

    def _update_orig_tag(self) -> None:
        base = self.app.t("lbl_original")
        if self.parent_word:
            hint = self.app.t("subwords_from").format(parent=self.parent_word)
            self.lbl_orig_tag.configure(text=f"{base} ({hint})")
        else:
            self.lbl_orig_tag.configure(text=base)

    def _update_archive_btn_label(self) -> None:
        key = "unarchive_word" if self.is_archived else "archive_word"
        self.btn_archive_word.configure(text=self.app.t(key))

    def _update_button_highlights(self) -> None:
        t = self.app.theme
        for key, btn in self.ai_tool_buttons.items():
            frame = self.ai_tool_frames[key]
            base_label = self.app.t(key)
            has_cached = bool(self.current_word and self.app.get_cached_ai_answer(self.current_word, key))
            btn.configure(text=f"{base_label}  ✓" if has_cached else base_label)
            if key == self.active_tool:
                btn.configure(fg=t.ACCENT, bg=t.ACCENT_SOFT)
                frame.configure(bg=t.ACCENT_SOFT, highlightbackground=t.ACCENT)
            else:
                btn.configure(fg=t.FG_WORD, bg=t.BG_CARD)
                frame.configure(bg=t.BG_CARD, highlightbackground=t.BORDER)

    def _prompt_cached_or_new(
        self, on_show_cached: Callable[[], None], on_generate_new: Callable[[], None]
    ) -> None:
        self._pending_show_cb = on_show_cached
        self._pending_gen_cb = on_generate_new
        self.choice_bar.pack(fill=tk.X, padx=20, pady=(4, 0), before=self.ai_panel)

    def _on_choose_show_cached(self) -> None:
        self.choice_bar.pack_forget()
        if self._pending_show_cb:
            self._pending_show_cb()

    def _on_choose_generate_new(self) -> None:
        self.choice_bar.pack_forget()
        if self._pending_gen_cb:
            self._pending_gen_cb()

    def _on_tool_clicked(self, key: str) -> None:
        self.active_tool = key
        self._update_button_highlights()
        self.choice_bar.pack_forget()
        self.ask_bar.pack_forget()

        if key == "btn_bkrs_examples":
            self._run_bkrs_examples_request()
            return

        cached = self.app.get_cached_ai_answer(self.current_word, key)

        if key == "btn_ask":
            if cached:
                self._prompt_cached_or_new(
                    on_show_cached=lambda c=cached: self._show_cached_and_ask_bar(c),
                    on_generate_new=self._open_ask_bar_for_new,
                )
            else:
                self._open_ask_bar_for_new()
            return

        if cached:
            self._prompt_cached_or_new(
                on_show_cached=lambda c=cached: self._set_ai_output(c),
                on_generate_new=lambda k=key: self._run_ai_request(k, force_new=True),
            )
        else:
            self._run_ai_request(key, force_new=True)

    def _run_bkrs_examples_request(self) -> None:
        word = self.current_word
        cached = self.app.get_cached_ai_answer(word, "btn_bkrs_examples")
        if cached:
            self._set_ai_output(cached)
            return

        self._set_ai_output(self.app.t("bkrs_loading"), is_subtle=True)

        def worker() -> None:
            examples = fetch_bkrs_examples(word)
            if examples:
                self.app.set_cached_ai_answer(word, "btn_bkrs_examples", examples)
                output = examples
            else:
                output = self.app.t("bkrs_no_examples").format(word=word)
            if self.current_word == word:
                self.app.root.after(0, self._on_ai_response_ready, output)

        threading.Thread(target=worker, daemon=True).start()

    def _show_cached_and_ask_bar(self, cached_text: str) -> None:
        self._set_ai_output(cached_text)
        self.ask_bar.pack(fill=tk.X, padx=20, pady=(4, 0), before=self.ai_panel)

    def _open_ask_bar_for_new(self) -> None:
        self.ask_bar.pack(fill=tk.X, padx=20, pady=(4, 0), before=self.ai_panel)
        self.entry_question.focus_set()

    def _submit_custom_question(self) -> None:
        question = self.var_question.get().strip()
        if not question:
            return
        self.choice_bar.pack_forget()
        q_key = f"btn_ask:{question.lower()}"
        cached = self.app.get_cached_ai_answer(self.current_word, q_key)
        if cached:
            self._prompt_cached_or_new(
                on_show_cached=lambda c=cached: self._set_ai_output(c),
                on_generate_new=lambda q=question: self._run_ai_request(
                    "btn_ask", custom_question=q, force_new=True
                ),
            )
        else:
            self._run_ai_request("btn_ask", custom_question=question, force_new=True)

    def _run_ai_request(
        self, action_key: str, custom_question: str = "", force_new: bool = False
    ) -> None:
        word = self.current_word
        translation = self.current_translation
        app_lang = self.app.settings.get("app_language", "English")
        specific_key = f"btn_ask:{custom_question.lower()}" if custom_question else action_key

        if not force_new:
            cached = self.app.get_cached_ai_answer(word, specific_key)
            if cached:
                self._set_ai_output(cached)
                return

        model = self.app.settings.get("ai_model", "gemini-3.8-flash")
        thinking_msg = self.app.t("ai_thinking").format(model=model)
        self._set_ai_output(thinking_msg, is_subtle=True)

        system_prompt, user_prompt = build_prompt(
            app_language=app_lang,
            action_key=action_key,
            word=word,
            translation=translation,
            question=custom_question,
        )
        provider = self.app.settings.get("ai_provider", "Google Gemini")
        api_key = self.app.settings.get("api_key", "")

        def worker() -> None:
            result = query_ai(
                provider=provider,
                model=model,
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                app_language=app_lang,
            )
            if not result.startswith("⚠"):
                if custom_question:
                    stored_text = f"**Q: {custom_question}**\n\n{result}"
                    self.app.set_cached_ai_answer(word, specific_key, stored_text)
                    self.app.set_cached_ai_answer(word, "btn_ask", stored_text)
                else:
                    self.app.set_cached_ai_answer(word, action_key, result)
            if self.current_word == word:
                self.app.root.after(0, self._on_ai_response_ready, result)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ai_response_ready(self, result: str) -> None:
        self._update_button_highlights()
        self._set_ai_output(result)

    def _set_ai_output(self, text: str, is_subtle: bool = False) -> None:
        """Render markdown-formatted text cleanly inside the scrollable Text widget."""
        self.ai_text.configure(state=tk.NORMAL)
        self.ai_text.delete("1.0", tk.END)

        if is_subtle:
            self.ai_text.insert(tk.END, text, "subtle")
            self.ai_text.configure(state=tk.DISABLED)
            return

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                clean_heading = stripped.lstrip("#").strip().replace("**", "")
                self.ai_text.insert(tk.END, clean_heading + "\n", "heading")
                continue

            parts = re.split(r"(\*\*.*?\*\*)", line)
            for part in parts:
                if part.startswith("**") and part.endswith("**") and len(part) > 4:
                    self.ai_text.insert(tk.END, part[2:-2], "bold")
                else:
                    self.ai_text.insert(tk.END, part)
            self.ai_text.insert(tk.END, "\n")

        self.ai_text.configure(state=tk.DISABLED)

    def apply_theme(self) -> None:
        t = self.app.theme
        self.configure(bg=t.BG_MAIN)
        self.nav_bar.configure(bg=t.BG_HEADER)
        self.btn_back.configure(
            fg=t.ACCENT,
            bg=t.ACCENT_SOFT,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
        )
        self.btn_archive_word.configure(
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
        )
        self.btn_remove.configure(
            fg=t.DANGER,
            bg=t.DANGER_SOFT,
            activebackground=t.DANGER,
            activeforeground=t.BG_HEADER,
        )
        self.nav_border.configure(bg=t.BORDER)
        self.hero_card.configure(bg=t.BG_CARD, highlightbackground=t.BORDER)
        self.lbl_orig_tag.configure(fg=t.FG_SUBTLE, bg=t.BG_CARD)
        self.word_label.configure(fg=t.FG_WORD, bg=t.BG_CARD)
        self.hero_divider.configure(bg=t.BORDER)
        self.lbl_trans_tag.configure(fg=t.FG_SUBTLE, bg=t.BG_CARD)
        self.translation_label.configure(fg=t.FG_TRANSLATION, bg=t.BG_CARD)
        self.lbl_ai_tools_header.configure(fg=t.FG_SUBTLE, bg=t.BG_MAIN)
        self.btn_grid.configure(bg=t.BG_MAIN)

        for btn in self.ai_tool_buttons.values():
            btn.configure(activebackground=t.ACCENT_SOFT, activeforeground=t.ACCENT)
        self._update_button_highlights()

        self.choice_bar.configure(bg=t.BG_CARD, highlightbackground=t.ACCENT)
        self.lbl_choice_prompt.configure(fg=t.FG_WORD, bg=t.BG_CARD)
        self.choice_btns_row.configure(bg=t.BG_CARD)
        self.btn_show_cached.configure(
            fg=t.BG_HEADER,
            bg=t.ACCENT,
            activebackground=t.ACCENT_HOVER,
            activeforeground=t.BG_HEADER,
        )
        self.btn_generate_new.configure(
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
        )

        self.ask_bar.configure(bg=t.BG_CARD, highlightbackground=t.ACCENT)
        self.entry_question.configure(fg=t.FG_WORD, bg=t.BG_INPUT, insertbackground=t.FG_WORD)
        self.btn_send_question.configure(
            fg=t.BG_HEADER,
            bg=t.ACCENT,
            activebackground=t.ACCENT_HOVER,
            activeforeground=t.BG_HEADER,
        )

        self.ai_panel.configure(bg=t.BG_CARD, highlightbackground=t.BORDER)
        self.ai_text.configure(fg=t.FG_WORD, bg=t.BG_CARD, insertbackground=t.FG_WORD)
        self._configure_text_tags()

    def apply_localization(self) -> None:
        self.btn_back.configure(text=self.app.t("back_to_list"))
        self._update_archive_btn_label()
        self.btn_remove.configure(text=self.app.t("remove_word"))
        self._update_orig_tag()
        self.lbl_trans_tag.configure(text=self.app.t("lbl_translated"))
        self.lbl_ai_tools_header.configure(text=self.app.t("ai_tools_header"))
        self.lbl_choice_prompt.configure(text=self.app.t("ai_cached_prompt"))
        self.btn_show_cached.configure(text=self.app.t("btn_show_cached"))
        self.btn_generate_new.configure(text=self.app.t("btn_generate_new"))
        self._update_button_highlights()
        self.btn_send_question.configure(text=self.app.t("btn_send"))
        if self.active_tool is None:
            self._set_ai_output(self.app.t("ai_placeholder"), is_subtle=True)

