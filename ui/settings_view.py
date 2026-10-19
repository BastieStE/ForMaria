from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import TYPE_CHECKING

from config import (
    AI_PROVIDERS,
    FONT_OPTIONS,
    HOTKEY_OPTIONS,
    LANGUAGES,
    SAVE_FILE,
    STRINGS,
    THEMES,
    TRANSLATION_SOURCES,
)

if TYPE_CHECKING:
    from ui.app import VocabularyApp


class SettingsView(tk.Frame):
    def __init__(self, parent: tk.Misc, app: "VocabularyApp"):
        super().__init__(parent, bg=app.theme.BG_MAIN)
        self.app = app
        self.api_key_visible: bool = False
        self._build()

    def _build(self) -> None:
        t = self.app.theme

        self.nav_bar = tk.Frame(self, bg=t.BG_HEADER, padx=22, pady=12)
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
            command=self._save_and_close,
        )
        self.btn_back.pack(side=tk.LEFT)

        self.lbl_title = tk.Label(
            self.nav_bar,
            text="",
            font=("Segoe UI", 14, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_HEADER,
        )
        self.lbl_title.pack(side=tk.LEFT, padx=(14, 0))

        self.lbl_save_status = tk.Label(
            self.nav_bar,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_TRANSLATION,
            bg=t.BG_HEADER,
        )
        self.lbl_save_status.pack(side=tk.RIGHT)

        self.nav_border = tk.Frame(self, bg=t.BORDER, height=1)
        self.nav_border.pack(fill=tk.X)

        self.body = tk.Frame(self, bg=t.BG_MAIN, padx=22, pady=12)
        self.body.pack(fill=tk.BOTH, expand=True)

        # --- Section 1: Appearance & Translation ---
        self.lbl_sec_general = tk.Label(
            self.body,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_MAIN,
            anchor="w",
        )
        self.lbl_sec_general.pack(fill=tk.X, pady=(0, 5))

        self.gen_card = tk.Frame(
            self.body,
            bg=t.BG_CARD,
            highlightbackground=t.BORDER,
            highlightthickness=1,
            padx=18,
            pady=10,
        )
        self.gen_card.pack(fill=tk.X, pady=(0, 12))
        self.gen_card.columnconfigure(1, weight=1)

        # Row 0: Appearance Theme (Dark / Light)
        self.lbl_theme = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_theme.grid(row=0, column=0, sticky="w", pady=3, padx=(0, 16))

        self.var_theme = tk.StringVar(value=self.app.settings.get("theme", "Dark"))
        cb_theme = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_theme,
            values=list(THEMES.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_theme.grid(row=0, column=1, sticky="ew", pady=3)
        cb_theme.bind("<<ComboboxSelected>>", self._on_setting_changed)

        # Row 1: App Language
        self.lbl_app_lang = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_app_lang.grid(row=1, column=0, sticky="w", pady=3, padx=(0, 16))

        self.var_app_lang = tk.StringVar(value=self.app.settings.get("app_language", "English"))
        cb_app_lang = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_app_lang,
            values=list(STRINGS.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_app_lang.grid(row=1, column=1, sticky="ew", pady=3)
        cb_app_lang.bind("<<ComboboxSelected>>", self._on_setting_changed)

        # Row 2: Text Font
        self.lbl_font = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_font.grid(row=2, column=0, sticky="w", pady=3, padx=(0, 16))

        font_val = self.app.settings.get("font_family", "Calibri")
        if font_val not in FONT_OPTIONS:
            font_val = "Calibri"
        self.var_font = tk.StringVar(value=font_val)
        cb_font = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_font,
            values=FONT_OPTIONS,
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_font.grid(row=2, column=1, sticky="ew", pady=3)
        cb_font.bind("<<ComboboxSelected>>", self._on_setting_changed)

        # Row 3: Translation Source (Google Translate vs BKRS)
        self.lbl_trans_source = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_trans_source.grid(row=3, column=0, sticky="w", pady=3, padx=(0, 16))

        source_val = self.app.settings.get("translation_source", "Google Translate")
        if source_val not in TRANSLATION_SOURCES:
            source_val = "Google Translate"
        self.var_trans_source = tk.StringVar(value=source_val)
        cb_trans_source = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_trans_source,
            values=TRANSLATION_SOURCES,
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_trans_source.grid(row=3, column=1, sticky="ew", pady=3)
        cb_trans_source.bind("<<ComboboxSelected>>", self._on_trans_source_changed)

        # Row 4: Target Translation Language (for Google Translate)
        self.lbl_target_lang = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_target_lang.grid(row=4, column=0, sticky="w", pady=3, padx=(0, 16))

        self.var_target_lang = tk.StringVar(value=self.app.settings.get("target_language", "French"))
        self.cb_target_lang = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_target_lang,
            values=list(LANGUAGES.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        self.cb_target_lang.grid(row=4, column=1, sticky="ew", pady=3)
        self.cb_target_lang.bind("<<ComboboxSelected>>", self._on_setting_changed)
        self._update_target_lang_state()

        # Row 5: Capture Shortcut
        self.lbl_hotkey = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_hotkey.grid(row=5, column=0, sticky="w", pady=3, padx=(0, 16))

        self.var_hotkey = tk.StringVar(value=self.app.settings.get("hotkey", "Ctrl + Q"))
        cb_hotkey = ttk.Combobox(
            self.gen_card,
            textvariable=self.var_hotkey,
            values=list(HOTKEY_OPTIONS.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_hotkey.grid(row=5, column=1, sticky="ew", pady=3)
        cb_hotkey.bind("<<ComboboxSelected>>", self._on_hotkey_changed)

        # Row 6: Words File (.txt) Location
        self.lbl_save_file = tk.Label(
            self.gen_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_save_file.grid(row=6, column=0, sticky="w", pady=3, padx=(0, 16))

        self.save_file_frame = tk.Frame(self.gen_card, bg=t.BG_CARD)
        self.save_file_frame.grid(row=6, column=1, sticky="ew", pady=3)

        self.var_save_path = tk.StringVar(
            value=self.app.settings.get("save_file_path", str(SAVE_FILE))
        )
        self.entry_save_path = tk.Entry(
            self.save_file_frame,
            textvariable=self.var_save_path,
            font=("Segoe UI", 9),
            fg=t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            highlightbackground=t.BORDER,
            highlightcolor=t.ACCENT,
            highlightthickness=1,
            relief=tk.FLAT,
            bd=5,
        )
        self.entry_save_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_save_path.bind("<Return>", self._on_setting_changed)
        self.entry_save_path.bind("<FocusOut>", self._on_setting_changed)

        self.btn_browse = tk.Button(
            self.save_file_frame,
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
            command=self._browse_save_file,
        )
        self.btn_browse.pack(side=tk.RIGHT, padx=(6, 0))

        # Row 7: Always on top checkbox
        self.var_topmost = tk.BooleanVar(value=bool(self.app.settings.get("always_on_top", False)))
        self.chk_topmost = tk.Checkbutton(
            self.gen_card,
            text="",
            variable=self.var_topmost,
            font=("Segoe UI", 10),
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            selectcolor=t.BG_INPUT,
            activebackground=t.BG_CARD,
            activeforeground=t.FG_WORD,
            cursor="hand2",
            command=self._on_setting_changed,
        )
        self.chk_topmost.grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 2))

        # --- Section 2: AI Configuration ---
        self.lbl_sec_ai = tk.Label(
            self.body,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_MAIN,
            anchor="w",
        )
        self.lbl_sec_ai.pack(fill=tk.X, pady=(0, 5))

        self.ai_card = tk.Frame(
            self.body,
            bg=t.BG_CARD,
            highlightbackground=t.BORDER,
            highlightthickness=1,
            padx=18,
            pady=10,
        )
        self.ai_card.pack(fill=tk.X)
        self.ai_card.columnconfigure(1, weight=1)

        # Row 0: AI Provider
        self.lbl_ai_provider = tk.Label(
            self.ai_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_ai_provider.grid(row=0, column=0, sticky="w", pady=3, padx=(0, 16))

        provider_val = self.app.settings.get("ai_provider", "Google Gemini")
        if provider_val not in AI_PROVIDERS:
            provider_val = "Google Gemini"
        self.var_ai_provider = tk.StringVar(value=provider_val)
        cb_provider = ttk.Combobox(
            self.ai_card,
            textvariable=self.var_ai_provider,
            values=list(AI_PROVIDERS.keys()),
            state="readonly",
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        cb_provider.grid(row=0, column=1, sticky="ew", pady=3)
        cb_provider.bind("<<ComboboxSelected>>", self._on_provider_changed)

        # Row 1: AI Model
        self.lbl_ai_model = tk.Label(
            self.ai_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_ai_model.grid(row=1, column=0, sticky="w", pady=3, padx=(0, 16))

        self.var_ai_model = tk.StringVar(value=self.app.settings.get("ai_model", "gemini-3.8-flash"))
        self.cb_model = ttk.Combobox(
            self.ai_card,
            textvariable=self.var_ai_model,
            values=AI_PROVIDERS[provider_val],
            font=("Segoe UI", 10),
            style="Modern.TCombobox",
        )
        self.cb_model.grid(row=1, column=1, sticky="ew", pady=3)
        self.cb_model.bind("<<ComboboxSelected>>", self._on_setting_changed)

        # Row 2: API Key
        self.lbl_api_key = tk.Label(
            self.ai_card, text="", font=("Segoe UI", 10), fg=t.FG_WORD, bg=t.BG_CARD, anchor="w"
        )
        self.lbl_api_key.grid(row=2, column=0, sticky="w", pady=3, padx=(0, 16))

        self.key_frame = tk.Frame(self.ai_card, bg=t.BG_CARD)
        self.key_frame.grid(row=2, column=1, sticky="ew", pady=3)

        self.var_api_key = tk.StringVar(value=self.app.settings.get("api_key", ""))
        self.entry_api_key = tk.Entry(
            self.key_frame,
            textvariable=self.var_api_key,
            show="•",
            font=("Consolas", 10),
            fg=t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            highlightbackground=t.BORDER,
            highlightcolor=t.ACCENT,
            highlightthickness=1,
            relief=tk.FLAT,
            bd=5,
        )
        self.entry_api_key.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_api_key.bind("<KeyRelease>", self._on_setting_changed)

        self.btn_toggle_key = tk.Button(
            self.key_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=5,
            command=self._toggle_api_key_visibility,
        )
        self.btn_toggle_key.pack(side=tk.RIGHT, padx=(6, 0))

    def sync_vars_from_settings(self) -> None:
        self.var_theme.set(self.app.settings.get("theme", "Dark"))
        self.var_font.set(self.app.settings.get("font_family", "Calibri"))
        self.var_save_path.set(self.app.settings.get("save_file_path", str(SAVE_FILE)))

    def _browse_save_file(self) -> None:
        current = Path(self.var_save_path.get().strip() or str(SAVE_FILE))
        initial_dir = str(current.parent) if current.parent.exists() else str(SAVE_FILE.parent)
        initial_file = current.name if current.suffix.lower() == ".txt" else "saved_words.txt"

        chosen = filedialog.asksaveasfilename(
            parent=self.app.root,
            title=self.app.t("dlg_save_file_title"),
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".txt",
            confirmoverwrite=False,
            filetypes=[("Text Files (*.txt)", "*.txt"), ("All Files (*.*)", "*.*")],
        )
        if chosen:
            self.var_save_path.set(chosen)
            self._on_setting_changed()

    def _update_target_lang_state(self) -> None:
        is_bkrs = self.var_trans_source.get() == "BKRS (bkrs.info)"
        self.cb_target_lang.configure(state="disabled" if is_bkrs else "readonly")

    def _on_trans_source_changed(self, _event=None) -> None:
        self._update_target_lang_state()
        self._on_setting_changed()

    def _toggle_api_key_visibility(self) -> None:
        self.api_key_visible = not self.api_key_visible
        self.entry_api_key.configure(show="" if self.api_key_visible else "•")
        self.btn_toggle_key.configure(
            text=self.app.t("btn_hide") if self.api_key_visible else self.app.t("btn_show")
        )

    def _on_provider_changed(self, _event=None) -> None:
        provider = self.var_ai_provider.get()
        models = AI_PROVIDERS.get(provider, [""])
        self.cb_model.configure(values=models)
        if models:
            self.var_ai_model.set(models[0])
        self._on_setting_changed()

    def _on_hotkey_changed(self, _event=None) -> None:
        self._on_setting_changed()
        self.app.hotkey_listener.reload_hotkey()

    def _on_setting_changed(self, _event=None) -> None:
        save_path = self.var_save_path.get().strip() or str(SAVE_FILE)
        self.var_save_path.set(save_path)
        self.app.update_settings(
            {
                "theme": self.var_theme.get(),
                "app_language": self.var_app_lang.get(),
                "font_family": self.var_font.get(),
                "translation_source": self.var_trans_source.get(),
                "target_language": self.var_target_lang.get(),
                "hotkey": self.var_hotkey.get(),
                "save_file_path": save_path,
                "always_on_top": bool(self.var_topmost.get()),
                "ai_provider": self.var_ai_provider.get(),
                "ai_model": self.var_ai_model.get().strip(),
                "api_key": self.var_api_key.get().strip(),
            }
        )
        self.lbl_save_status.configure(text=self.app.t("status_saved"))
        self.app.root.after(2000, lambda: self.lbl_save_status.configure(text=""))

    def _save_and_close(self) -> None:
        self._on_setting_changed()
        self.app.show_list_view()

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
        self.lbl_title.configure(fg=t.FG_WORD, bg=t.BG_HEADER)
        self.lbl_save_status.configure(fg=t.FG_TRANSLATION, bg=t.BG_HEADER)
        self.nav_border.configure(bg=t.BORDER)
        self.body.configure(bg=t.BG_MAIN)

        self.lbl_sec_general.configure(fg=t.FG_SUBTLE, bg=t.BG_MAIN)
        self.gen_card.configure(bg=t.BG_CARD, highlightbackground=t.BORDER)
        for lbl in (
            self.lbl_theme,
            self.lbl_app_lang,
            self.lbl_font,
            self.lbl_trans_source,
            self.lbl_target_lang,
            self.lbl_hotkey,
            self.lbl_save_file,
        ):
            lbl.configure(fg=t.FG_WORD, bg=t.BG_CARD)
        self.save_file_frame.configure(bg=t.BG_CARD)
        self.entry_save_path.configure(
            fg=t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            highlightbackground=t.BORDER,
            highlightcolor=t.ACCENT,
        )
        self.btn_browse.configure(
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
        )
        self.chk_topmost.configure(
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            selectcolor=t.BG_INPUT,
            activebackground=t.BG_CARD,
            activeforeground=t.FG_WORD,
        )

        self.lbl_sec_ai.configure(fg=t.FG_SUBTLE, bg=t.BG_MAIN)
        self.ai_card.configure(bg=t.BG_CARD, highlightbackground=t.BORDER)
        for lbl in (self.lbl_ai_provider, self.lbl_ai_model, self.lbl_api_key):
            lbl.configure(fg=t.FG_WORD, bg=t.BG_CARD)
        self.key_frame.configure(bg=t.BG_CARD)
        self.entry_api_key.configure(
            fg=t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            highlightbackground=t.BORDER,
            highlightcolor=t.ACCENT,
        )
        self.btn_toggle_key.configure(
            fg=t.FG_SUBTLE,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
        )

    def apply_localization(self) -> None:
        self.btn_back.configure(text=self.app.t("back_to_list"))
        self.lbl_title.configure(text=self.app.t("settings_title"))
        self.lbl_sec_general.configure(text=self.app.t("sec_general"))
        self.lbl_theme.configure(text=self.app.t("lbl_theme"))
        self.lbl_app_lang.configure(text=self.app.t("lbl_app_lang"))
        self.lbl_font.configure(text=self.app.t("lbl_font"))
        self.lbl_trans_source.configure(text=self.app.t("lbl_trans_source"))
        self.lbl_target_lang.configure(text=self.app.t("lbl_target_lang"))
        self.lbl_hotkey.configure(text=self.app.t("lbl_hotkey"))
        self.lbl_save_file.configure(text=self.app.t("lbl_save_file"))
        self.btn_browse.configure(text=self.app.t("btn_browse"))
        self.chk_topmost.configure(text=self.app.t("lbl_always_on_top"))
        self.lbl_sec_ai.configure(text=self.app.t("sec_ai"))
        self.lbl_ai_provider.configure(text=self.app.t("lbl_ai_provider"))
        self.lbl_ai_model.configure(text=self.app.t("lbl_ai_model"))
        self.lbl_api_key.configure(text=self.app.t("lbl_api_key"))
        self.btn_toggle_key.configure(
            text=self.app.t("btn_hide") if self.api_key_visible else self.app.t("btn_show")
        )

