import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from storage import parse_sub_words

if TYPE_CHECKING:
    from ui.app import VocabularyApp


class WordListView(tk.Frame):
    def __init__(self, parent: tk.Misc, app: "VocabularyApp"):
        super().__init__(parent, bg=app.theme.BG_MAIN)
        self.app = app
        self.search_var = tk.StringVar()
        self.search_placeholder_active: bool = True
        self._dragged_card: tk.Frame | None = None
        self._pressed_card: tk.Frame | None = None
        self._press_y: int = 0
        self._did_drag: bool = False
        self.expanded_words: set[str] = set()
        self.row_cards: list[tk.Frame] = []
        self._build()

    def _build(self) -> None:
        t = self.app.theme
        font_family = self.app.font_family

        # --- Top Header Surface (Title, Controls, Subtitle & Search Bar) ---
        self.header = tk.Frame(self, bg=t.BG_HEADER, padx=22, pady=14)
        self.header.pack(fill=tk.X)

        self.top_row = tk.Frame(self.header, bg=t.BG_HEADER)
        self.top_row.pack(fill=tk.X)

        self.brand_dot = tk.Label(
            self.top_row,
            text="◆",
            font=("Segoe UI", 12),
            fg=t.ACCENT,
            bg=t.BG_HEADER,
        )
        self.brand_dot.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_main_title = tk.Label(
            self.top_row,
            text="",
            font=("Segoe UI", 15, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_HEADER,
        )
        self.lbl_main_title.pack(side=tk.LEFT)

        self.count_badge = tk.Label(
            self.top_row,
            text="0",
            font=("Segoe UI", 9, "bold"),
            fg=t.ACCENT,
            bg=t.ACCENT_SOFT,
            padx=9,
            pady=2,
        )
        self.count_badge.pack(side=tk.LEFT, padx=(10, 0))

        self.btn_clear = tk.Button(
            self.top_row,
            text="",
            font=("Segoe UI", 9),
            fg=t.FG_SUBTLE,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.DANGER_SOFT,
            activeforeground=t.DANGER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.app.clear_all,
        )
        self.btn_clear.pack(side=tk.RIGHT)

        self.btn_settings = tk.Button(
            self.top_row,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.app.show_settings_view,
        )
        self.btn_settings.pack(side=tk.RIGHT, padx=(0, 6))

        self.btn_archive = tk.Button(
            self.top_row,
            text="",
            font=("Segoe UI", 9, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.ACCENT_SOFT,
            activeforeground=t.ACCENT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self.app.toggle_archive_view,
        )
        self.btn_archive.pack(side=tk.RIGHT, padx=(0, 6))

        self.btn_theme_toggle = tk.Button(
            self.top_row,
            text="☀" if t.is_dark else "☾",
            font=("Segoe UI", 10),
            fg=t.ACCENT,
            bg=t.ACCENT_SOFT,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=9,
            pady=3,
            command=self.app.toggle_theme,
        )
        self.btn_theme_toggle.pack(side=tk.RIGHT, padx=(0, 6))

        self.lbl_header_hint = tk.Label(
            self.header,
            text="",
            font=("Segoe UI", 9),
            fg=t.FG_SUBTLE,
            bg=t.BG_HEADER,
        )
        self.lbl_header_hint.pack(anchor="w", pady=(6, 0))

        # --- Dual-Side Search Bar inside Top Header ---
        self.search_box = tk.Frame(
            self.header,
            bg=t.BG_INPUT,
            highlightbackground=t.BORDER,
            highlightcolor=t.ACCENT,
            highlightthickness=1,
            padx=12,
            pady=6,
        )
        self.search_box.pack(fill=tk.X, pady=(10, 2))

        self.lbl_search_icon = tk.Label(
            self.search_box,
            text="🔍",
            font=("Segoe UI", 10),
            fg=t.FG_SUBTLE,
            bg=t.BG_INPUT,
        )
        self.lbl_search_icon.pack(side=tk.LEFT, padx=(0, 8))

        self.entry_search = tk.Entry(
            self.search_box,
            textvariable=self.search_var,
            font=(font_family, 10),
            fg=t.FG_SUBTLE,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
            relief=tk.FLAT,
            bd=0,
        )
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_search.bind("<FocusIn>", self._on_search_focus_in)
        self.entry_search.bind("<FocusOut>", self._on_search_focus_out)
        self.entry_search.bind("<KeyRelease>", self._on_search_changed)
        self.entry_search.bind("<Escape>", lambda _e: self._clear_search())

        self.btn_clear_search = tk.Button(
            self.search_box,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg=t.FG_SUBTLE,
            bg=t.BG_INPUT,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            command=self._clear_search,
        )

        self.header_border = tk.Frame(self, bg=t.BORDER, height=1)
        self.header_border.pack(fill=tk.X)

        # --- Scrollable Word List Area ---
        self.container = tk.Frame(self, bg=t.BG_MAIN)
        self.container.pack(fill=tk.BOTH, expand=True, padx=18, pady=(10, 14))

        self.canvas = tk.Canvas(
            self.container,
            bg=t.BG_MAIN,
            highlightthickness=0,
            bd=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self.container,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            style="Modern.Vertical.TScrollbar",
        )
        self.rows_frame = tk.Frame(self.canvas, bg=t.BG_MAIN)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.rows_frame,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.rows_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.app.root.bind_all("<MouseWheel>", self._on_mousewheel)

    # --- Search Bar Logic ---

    def _on_search_focus_in(self, _event=None) -> None:
        t = self.app.theme
        self.search_box.configure(highlightbackground=t.ACCENT)
        if self.search_placeholder_active:
            self.search_placeholder_active = False
            self.search_var.set("")
            self.entry_search.configure(fg=t.FG_WORD)

    def _on_search_focus_out(self, _event=None) -> None:
        t = self.app.theme
        self.search_box.configure(highlightbackground=t.BORDER)
        if not self.search_var.get().strip():
            self._set_search_placeholder()

    def _set_search_placeholder(self) -> None:
        self.search_placeholder_active = True
        self.search_var.set(self.app.t("search_placeholder"))
        self.entry_search.configure(fg=self.app.theme.FG_SUBTLE)
        self.btn_clear_search.pack_forget()

    def _clear_search(self) -> None:
        self.search_var.set("")
        self.search_placeholder_active = False
        self.entry_search.configure(fg=self.app.theme.FG_WORD)
        self.btn_clear_search.pack_forget()
        self.entry_search.focus_set()
        self.refresh()

    def _on_search_changed(self, _event=None) -> None:
        query = self.get_search_query()
        if query:
            if not self.btn_clear_search.winfo_ismapped():
                self.btn_clear_search.pack(side=tk.RIGHT)
        else:
            self.btn_clear_search.pack_forget()
        self.refresh()

    def get_search_query(self) -> str:
        if self.search_placeholder_active:
            return ""
        return self.search_var.get().strip().lower()

    # --- Scroll & Layout Helpers ---

    def _on_frame_configure(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._update_scrollbar_visibility()

    def _update_scrollbar_visibility(self) -> None:
        if self.rows_frame.winfo_reqheight() > self.canvas.winfo_height():
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))
        else:
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()

    def _on_mousewheel(self, event) -> None:
        if self.app.current_view == "list" and self.rows_frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def apply_font(self) -> None:
        self.entry_search.configure(font=(self.app.font_family, 10))
        self.refresh()

    def _update_header_state(self) -> None:
        t = self.app.theme
        in_archive = self.app.showing_archive
        active_count = len(self.app.entries)
        archive_count = len(self.app.archived_entries)

        if in_archive:
            self.lbl_main_title.configure(text=self.app.t("archive_title"))
            self.count_badge.configure(text=str(archive_count))
            self.btn_archive.configure(
                text=self.app.t("active_words_btn").format(count=active_count),
                fg=t.ACCENT,
                bg=t.ACCENT_SOFT,
                activebackground=t.ACCENT,
                activeforeground=t.BG_HEADER,
            )
            self.lbl_header_hint.configure(text=self.app.t("header_hint_archive"))
        else:
            self.lbl_main_title.configure(text=self.app.t("app_title"))
            self.count_badge.configure(text=str(active_count))
            self.btn_archive.configure(
                text=self.app.t("archive_btn").format(count=archive_count),
                fg=t.FG_WORD,
                bg=t.BG_BTN_SECONDARY,
                activebackground=t.BG_BTN_HOVER,
                activeforeground=t.FG_WORD,
            )
            hotkey = self.app.settings.get("hotkey", "Ctrl + Q")
            source = self.app.settings.get("translation_source", "Google Translate")
            if source == "BKRS (bkrs.info)":
                hint_text = self.app.t("header_hint_bkrs").format(hotkey=hotkey)
            else:
                hint_text = self.app.t("header_hint_google").format(
                    hotkey=hotkey,
                    lang=self.app.settings.get("target_language", "French"),
                )
            self.lbl_header_hint.configure(text=hint_text)

    def apply_theme(self) -> None:
        t = self.app.theme
        self.configure(bg=t.BG_MAIN)
        self.header.configure(bg=t.BG_HEADER)
        self.top_row.configure(bg=t.BG_HEADER)
        self.brand_dot.configure(fg=t.ACCENT, bg=t.BG_HEADER)
        self.lbl_main_title.configure(fg=t.FG_WORD, bg=t.BG_HEADER)
        self.count_badge.configure(fg=t.ACCENT, bg=t.ACCENT_SOFT)
        self.btn_clear.configure(
            fg=t.FG_SUBTLE,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.DANGER_SOFT,
            activeforeground=t.DANGER,
        )
        self.btn_settings.configure(
            fg=t.FG_WORD,
            bg=t.BG_BTN_SECONDARY,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
        )
        self.btn_theme_toggle.configure(
            text="☀" if t.is_dark else "☾",
            fg=t.ACCENT,
            bg=t.ACCENT_SOFT,
            activebackground=t.ACCENT,
            activeforeground=t.BG_HEADER,
        )
        self.lbl_header_hint.configure(fg=t.FG_SUBTLE, bg=t.BG_HEADER)
        self.header_border.configure(bg=t.BORDER)

        self.search_box.configure(bg=t.BG_INPUT, highlightbackground=t.BORDER, highlightcolor=t.ACCENT)
        self.lbl_search_icon.configure(fg=t.FG_SUBTLE, bg=t.BG_INPUT)
        self.entry_search.configure(
            fg=t.FG_SUBTLE if self.search_placeholder_active else t.FG_WORD,
            bg=t.BG_INPUT,
            insertbackground=t.FG_WORD,
        )
        self.btn_clear_search.configure(
            fg=t.FG_SUBTLE,
            bg=t.BG_INPUT,
            activebackground=t.BG_BTN_HOVER,
            activeforeground=t.FG_WORD,
        )

        self.container.configure(bg=t.BG_MAIN)
        self.canvas.configure(bg=t.BG_MAIN)
        self.rows_frame.configure(bg=t.BG_MAIN)
        self._update_header_state()
        self.refresh()

    def apply_localization(self) -> None:
        self.btn_settings.configure(text=self.app.t("settings_btn"))
        self.btn_clear.configure(text=self.app.t("clear_btn"))
        self._update_header_state()
        if self.search_placeholder_active:
            self._set_search_placeholder()

    def refresh(self, scroll_to_bottom: bool = False) -> None:
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        self.row_cards.clear()

        t = self.app.theme
        self._update_header_state()

        current_list = self.app.archived_entries if self.app.showing_archive else self.app.entries

        if not current_list:
            empty_card = tk.Frame(
                self.rows_frame,
                bg=t.BG_CARD,
                highlightbackground=t.BORDER,
                highlightthickness=1,
                padx=30,
                pady=44,
            )
            empty_card.pack(fill=tk.X, pady=20)

            tk.Label(
                empty_card,
                text="📦" if self.app.showing_archive else "✦",
                font=("Segoe UI", 22),
                fg=t.ACCENT,
                bg=t.BG_CARD,
            ).pack(pady=(0, 8))

            title_key = "empty_archive_title" if self.app.showing_archive else "empty_title"
            tk.Label(
                empty_card,
                text=self.app.t(title_key),
                font=("Segoe UI", 12, "bold"),
                fg=t.FG_WORD,
                bg=t.BG_CARD,
            ).pack(pady=(0, 4))

            if self.app.showing_archive:
                empty_text = self.app.t("empty_archive_list")
            else:
                empty_text = self.app.t("empty_list").format(
                    hotkey=self.app.settings.get("hotkey", "Ctrl + Q")
                )
            tk.Label(
                empty_card,
                text=empty_text,
                font=("Segoe UI", 10),
                fg=t.FG_SUBTLE,
                bg=t.BG_CARD,
                justify=tk.CENTER,
                wraplength=380,
            ).pack()
            self.app.root.update_idletasks()
            self._update_scrollbar_visibility()
            return

        query = self.get_search_query()
        filtered = [
            (real_idx, word, translation)
            for real_idx, (word, translation) in enumerate(current_list)
            if not query or query in word.lower() or query in translation.lower()
        ]

        if not filtered:
            tk.Label(
                self.rows_frame,
                text=self.app.t("no_search_results"),
                font=("Segoe UI", 11),
                fg=t.FG_SUBTLE,
                bg=t.BG_MAIN,
                pady=40,
            ).pack(fill=tk.X)
            self.app.root.update_idletasks()
            self._update_scrollbar_visibility()
            return

        total_len = len(current_list)
        can_reorder = not bool(query) and total_len > 1
        for real_idx, word, translation in filtered:
            self._create_row(real_idx, word, translation, total_len, can_reorder)

        self.app.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar_visibility()
        if scroll_to_bottom and not query:
            self.canvas.yview_moveto(1.0)

    def _create_row(
        self, index: int, word: str, translation: str, total_len: int, can_reorder: bool
    ) -> None:
        t = self.app.theme
        font_family = self.app.font_family

        sub_words = parse_sub_words(translation)
        has_sub_words = len(sub_words) > 1
        is_expanded = word in self.expanded_words

        block_container = tk.Frame(self.rows_frame, bg=t.BG_MAIN)
        block_container.pack(fill=tk.X, pady=4)
        block_container.real_index = index  # type: ignore[attr-defined]
        block_container.btn_up = None  # type: ignore[attr-defined]
        block_container.btn_down = None  # type: ignore[attr-defined]
        self.row_cards.append(block_container)

        card = tk.Frame(
            block_container,
            bg=t.BG_CARD,
            highlightbackground=t.BORDER,
            highlightthickness=1,
            padx=12,
            pady=10,
            cursor="hand2",
        )
        card.pack(fill=tk.X)
        block_container.card = card  # type: ignore[attr-defined]

        hover_widgets: list[tk.Widget] = []
        hover_buttons: list[tk.Button] = []

        # --- Left Reorder Controls (Drag Grip ⠿ + ▲/▼ Buttons) ---
        if can_reorder:
            grip_lbl = tk.Label(
                card,
                text="⠿",
                font=("Segoe UI", 12),
                fg=t.FG_SUBTLE,
                bg=t.BG_CARD,
                padx=4,
                cursor="fleur",
            )
            grip_lbl.pack(side=tk.LEFT)
            grip_lbl.bind("<ButtonPress-1>", lambda e, c=block_container: self._on_block_press(e, c, immediate_drag=True))
            grip_lbl.bind("<B1-Motion>", self._on_block_motion)
            grip_lbl.bind("<ButtonRelease-1>", lambda e, c=block_container: self._on_block_release(e, c))
            hover_widgets.append(grip_lbl)

            order_box = tk.Frame(card, bg=t.BG_CARD)
            order_box.pack(side=tk.LEFT, padx=(0, 8))
            hover_widgets.append(order_box)

            btn_up = tk.Button(
                order_box,
                text="▲",
                font=("Segoe UI", 6),
                fg=t.FG_DISABLED if index == 0 else t.FG_SUBTLE,
                bg=t.BG_CARD,
                activebackground=t.ACCENT_SOFT,
                activeforeground=t.ACCENT,
                relief=tk.FLAT,
                bd=0,
                padx=3,
                pady=0,
                cursor="arrow" if index == 0 else "hand2",
                state=tk.DISABLED if index == 0 else tk.NORMAL,
                command=lambda c=block_container: self.app.move_entry(c.real_index, c.real_index - 1),
            )
            btn_up.pack(side=tk.TOP)
            block_container.btn_up = btn_up  # type: ignore[attr-defined]
            hover_buttons.append(btn_up)

            btn_down = tk.Button(
                order_box,
                text="▼",
                font=("Segoe UI", 6),
                fg=t.FG_DISABLED if index >= total_len - 1 else t.FG_SUBTLE,
                bg=t.BG_CARD,
                activebackground=t.ACCENT_SOFT,
                activeforeground=t.ACCENT,
                relief=tk.FLAT,
                bd=0,
                padx=3,
                pady=0,
                cursor="arrow" if index >= total_len - 1 else "hand2",
                state=tk.DISABLED if index >= total_len - 1 else tk.NORMAL,
                command=lambda c=block_container: self.app.move_entry(c.real_index, c.real_index + 1),
            )
            btn_down.pack(side=tk.BOTTOM)
            block_container.btn_down = btn_down  # type: ignore[attr-defined]
            hover_buttons.append(btn_down)

        scale = self.app.font_scale
        word_sz = scale.get("list_word", 12)
        trans_sz = scale.get("list_trans", 11)

        word_lbl = tk.Label(
            card,
            text=word,
            font=(font_family, word_sz, "bold"),
            fg=t.FG_WORD,
            bg=t.BG_CARD,
            anchor="w",
            justify=tk.LEFT,
            cursor="hand2",
        )
        word_lbl.pack(side=tk.LEFT)

        arrow_lbl = tk.Label(
            card,
            text="→",
            font=("Segoe UI", max(9, word_sz - 2)),
            fg=t.FG_SUBTLE,
            bg=t.BG_CARD,
            padx=8,
            cursor="hand2",
        )
        arrow_lbl.pack(side=tk.LEFT)

        # --- Right Side Actions (packed before trans_lbl so middle expands cleanly) ---
        del_btn = tk.Button(
            card,
            text="✕",
            font=("Segoe UI", 9),
            fg=t.FG_SUBTLE,
            bg=t.BG_CARD,
            activebackground=t.DANGER_SOFT,
            activeforeground=t.DANGER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            pady=2,
            command=lambda c=block_container: self.app.delete_entry(c.real_index),
        )
        del_btn.pack(side=tk.RIGHT, padx=(2, 0))
        hover_buttons.append(del_btn)

        arch_btn = tk.Button(
            card,
            text="↩" if self.app.showing_archive else "📥",
            font=("Segoe UI", 9),
            fg=t.ACCENT if self.app.showing_archive else t.FG_SUBTLE,
            bg=t.BG_CARD,
            activebackground=t.ACCENT_SOFT,
            activeforeground=t.ACCENT,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            pady=2,
            command=lambda c=block_container: (
                self.app.unarchive_entry(c.real_index)
                if self.app.showing_archive
                else self.app.archive_entry(c.real_index)
            ),
        )
        arch_btn.pack(side=tk.RIGHT, padx=(4, 0))
        hover_buttons.append(arch_btn)

        btn_dropdown: tk.Button | None = None
        chevron_lbl: tk.Label | None = None

        if has_sub_words:
            dropdown_frame = tk.Frame(block_container, bg=t.BG_MAIN)
            block_container.dropdown_frame = dropdown_frame  # type: ignore[attr-defined]

            btn_dropdown = tk.Button(
                card,
                text="▲" if is_expanded else "▼",
                font=("Segoe UI", 16, "bold"),
                fg=t.ACCENT if is_expanded else t.FG_WORD,
                bg=t.BG_CARD,
                activebackground=t.ACCENT_SOFT,
                activeforeground=t.ACCENT,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=8,
                pady=0,
            )
            btn_dropdown.pack(side=tk.RIGHT, padx=(4, 0))
            hover_buttons.append(btn_dropdown)

            def _toggle(w=word, df=dropdown_frame, btn=btn_dropdown):
                if w in self.expanded_words:
                    self.expanded_words.remove(w)
                    df.pack_forget()
                    btn.configure(text="▼", fg=t.FG_WORD)
                else:
                    self.expanded_words.add(w)
                    df.pack(fill=tk.X, pady=(2, 6))
                    btn.configure(text="▲", fg=t.ACCENT)
                self.app.root.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                self._update_scrollbar_visibility()

            btn_dropdown.configure(command=_toggle)
        else:
            chevron_lbl = tk.Label(
                card,
                text="›",
                font=("Segoe UI", 13),
                fg=t.FG_SUBTLE,
                bg=t.BG_CARD,
                padx=4,
                cursor="hand2",
            )
            chevron_lbl.pack(side=tk.RIGHT)

        # Initial wrap calculation based on canvas width
        canvas_w = self.canvas.winfo_width()
        fixed_right = 115 if has_sub_words else 95
        fixed_left = (word_sz * len(word)) + (65 if can_reorder else 45)
        init_avail = max(150, (canvas_w if canvas_w > 200 else 600) - fixed_left - fixed_right)

        if has_sub_words:
            sub_names = " • ".join(w for w, _ in sub_words)
            summary = self.app.t("subwords_count").format(n=len(sub_words), words=sub_names)
            trans_lbl = tk.Label(
                card,
                text=summary,
                font=(font_family, trans_sz, "italic"),
                fg=t.ACCENT,
                bg=t.BG_CARD,
                anchor="w",
                justify=tk.LEFT,
                wraplength=init_avail,
                cursor="hand2",
            )
        else:
            display_translation = (
                "; ".join(
                    p.strip()
                    for line in translation.splitlines()
                    for p in line.split("|")
                    if p.strip()
                )
                or translation
            )
            trans_lbl = tk.Label(
                card,
                text=display_translation,
                font=(font_family, trans_sz),
                fg=t.FG_TRANSLATION,
                bg=t.BG_CARD,
                anchor="w",
                justify=tk.LEFT,
                wraplength=init_avail,
                cursor="hand2",
            )
        trans_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        def _on_card_configure(event, c=card, lbl=trans_lbl, wlbl=word_lbl):
            if event.widget != c:
                return
            fr = 115 if has_sub_words else 95
            fl = wlbl.winfo_reqwidth() + (65 if can_reorder else 45)
            avail = max(150, event.width - fl - fr)
            if abs(lbl.cget("wraplength") - avail) > 8:
                lbl.configure(wraplength=avail)

        card.bind("<Configure>", _on_card_configure)

        clickable_widgets = [word_lbl, arrow_lbl, trans_lbl]
        if chevron_lbl is not None:
            clickable_widgets.append(chevron_lbl)

        if has_sub_words:
            for sw, st in sub_words:
                sub_card = tk.Frame(
                    dropdown_frame,
                    bg=t.BG_CARD,
                    highlightbackground=t.BORDER,
                    highlightthickness=1,
                    padx=14,
                    pady=8,
                    cursor="hand2",
                )
                sub_card.pack(fill=tk.X, padx=(22, 0), pady=2)

                sub_widgets: list[tk.Widget] = []

                sub_branch = tk.Label(
                    sub_card,
                    text="↳",
                    font=("Segoe UI", max(10, word_sz - 1), "bold"),
                    fg=t.ACCENT,
                    bg=t.BG_CARD,
                )
                sub_branch.pack(side=tk.LEFT, padx=(0, 6))
                sub_widgets.append(sub_branch)

                sub_w_lbl = tk.Label(
                    sub_card,
                    text=sw,
                    font=(font_family, max(10, word_sz - 1), "bold"),
                    fg=t.FG_WORD,
                    bg=t.BG_CARD,
                    anchor="w",
                    justify=tk.LEFT,
                    cursor="hand2",
                )
                sub_w_lbl.pack(side=tk.LEFT)
                sub_widgets.append(sub_w_lbl)

                sub_arrow = tk.Label(
                    sub_card,
                    text="→",
                    font=("Segoe UI", max(9, word_sz - 3)),
                    fg=t.FG_SUBTLE,
                    bg=t.BG_CARD,
                    padx=8,
                    cursor="hand2",
                )
                sub_arrow.pack(side=tk.LEFT)
                sub_widgets.append(sub_arrow)

                sub_chev = tk.Label(
                    sub_card,
                    text="›",
                    font=("Segoe UI", 12),
                    fg=t.FG_SUBTLE,
                    bg=t.BG_CARD,
                    padx=4,
                    cursor="hand2",
                )
                sub_chev.pack(side=tk.RIGHT)
                sub_widgets.append(sub_chev)

                sub_init_avail = max(120, (canvas_w if canvas_w > 200 else 580) - (word_sz * len(sw)) - 100)
                sub_t_lbl = tk.Label(
                    sub_card,
                    text=st,
                    font=(font_family, max(10, trans_sz - 1)),
                    fg=t.FG_TRANSLATION,
                    bg=t.BG_CARD,
                    anchor="w",
                    justify=tk.LEFT,
                    wraplength=sub_init_avail,
                    cursor="hand2",
                )
                sub_t_lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
                sub_widgets.append(sub_t_lbl)

                def _on_subcard_configure(event, sc=sub_card, lbl=sub_t_lbl, wlbl=sub_w_lbl):
                    if event.widget != sc:
                        return
                    fl = wlbl.winfo_reqwidth() + 60
                    avail = max(120, event.width - fl - 35)
                    if abs(lbl.cget("wraplength") - avail) > 8:
                        lbl.configure(wraplength=avail)

                sub_card.bind("<Configure>", _on_subcard_configure)

                sub_card.sub_widgets = tuple(sub_widgets)  # type: ignore[attr-defined]

                for w_item in (sub_card, *sub_widgets):
                    w_item.bind(
                        "<Enter>",
                        lambda _e, sc=sub_card: self._apply_subcard_surface(sc, True),
                    )
                    w_item.bind(
                        "<Leave>",
                        lambda _e, sc=sub_card: self._apply_subcard_surface(sc, False),
                    )
                    w_item.bind(
                        "<ButtonRelease-1>",
                        lambda _e, p_idx=index, cw=sw, ct=st: self.app.show_subword_view(p_idx, cw, ct),
                    )

            if is_expanded:
                dropdown_frame.pack(fill=tk.X, pady=(2, 6))

        hover_widgets.extend(clickable_widgets)
        block_container.hover_widgets = tuple(hover_widgets)  # type: ignore[attr-defined]
        block_container.hover_buttons = tuple(hover_buttons)  # type: ignore[attr-defined]

        for widget in (card, *clickable_widgets):
            widget.bind(
                "<ButtonPress-1>",
                lambda e, c=block_container, ro=can_reorder: self._on_block_press(e, c, immediate_drag=False, can_reorder=ro),
            )
            widget.bind("<B1-Motion>", self._on_block_motion)
            widget.bind("<ButtonRelease-1>", lambda e, c=block_container: self._on_block_release(e, c))

        for widget in (card, *hover_widgets, *hover_buttons):
            widget.bind(
                "<Enter>",
                lambda _e, c=block_container: self._on_card_hover(c, True),
            )
            widget.bind(
                "<Leave>",
                lambda _e, c=block_container: self._on_card_hover(c, False),
            )

    # --- In-Place Block Movement & Smooth Drag-and-Drop ---

    def move_card_block(self, from_idx: int, to_idx: int) -> None:
        """Move a card widget block in-place without destroying or recreating any widgets."""
        if not (0 <= from_idx < len(self.row_cards) and 0 <= to_idx < len(self.row_cards)):
            return
        if from_idx == to_idx:
            return

        moving_card = self.row_cards.pop(from_idx)
        if to_idx < from_idx:
            target_card = self.row_cards[to_idx]
            moving_card.pack(fill=tk.X, pady=4, before=target_card)
        else:
            target_card = self.row_cards[to_idx - 1]
            moving_card.pack(fill=tk.X, pady=4, after=target_card)

        self.row_cards.insert(to_idx, moving_card)
        self._sync_card_indices_and_arrows()
        self.app.root.update_idletasks()

    def _sync_card_indices_and_arrows(self) -> None:
        """Update real_index and ▲/▼ button states on existing card widgets in-place."""
        t = self.app.theme
        total = len(self.row_cards)
        for idx, card in enumerate(self.row_cards):
            card.real_index = idx  # type: ignore[attr-defined]
            btn_up = getattr(card, "btn_up", None)
            btn_down = getattr(card, "btn_down", None)
            if btn_up is not None and btn_up.winfo_exists():
                is_first = idx == 0
                btn_up.configure(
                    state=tk.DISABLED if is_first else tk.NORMAL,
                    fg=t.FG_DISABLED if is_first else t.FG_SUBTLE,
                    cursor="arrow" if is_first else "hand2",
                )
            if btn_down is not None and btn_down.winfo_exists():
                is_last = idx >= total - 1
                btn_down.configure(
                    state=tk.DISABLED if is_last else tk.NORMAL,
                    fg=t.FG_DISABLED if is_last else t.FG_SUBTLE,
                    cursor="arrow" if is_last else "hand2",
                )

    def _on_block_press(
        self, event, card: tk.Frame, immediate_drag: bool = False, can_reorder: bool = True
    ) -> None:
        self._pressed_card = card
        self._press_y = event.y_root
        self._did_drag = immediate_drag and can_reorder
        if can_reorder:
            self._dragged_card = card
            if immediate_drag:
                self._apply_card_surface(card, hovered=True, dragging=True)
        else:
            self._dragged_card = None

    def _on_block_motion(self, event) -> None:
        card = self._dragged_card
        if card is None or not card.winfo_exists():
            return

        if not self._did_drag:
            if abs(event.y_root - self._press_y) < 8:
                return
            self._did_drag = True
            self._apply_card_surface(card, hovered=True, dragging=True)

        cur_idx = getattr(card, "real_index", -1)
        if not (0 <= cur_idx < len(self.row_cards)):
            return

        y_root = event.y_root

        # Check upward swap against predecessor's midpoint
        if cur_idx > 0:
            prev_card = self.row_cards[cur_idx - 1]
            if prev_card.winfo_exists():
                prev_mid = prev_card.winfo_rooty() + prev_card.winfo_height() // 2
                if y_root < prev_mid:
                    self.app.move_entry(cur_idx, cur_idx - 1, save=False, update_ui_blocks=True)
                    return

        # Check downward swap against successor's midpoint
        if cur_idx < len(self.row_cards) - 1:
            next_card = self.row_cards[cur_idx + 1]
            if next_card.winfo_exists():
                next_mid = next_card.winfo_rooty() + next_card.winfo_height() // 2
                if y_root > next_mid:
                    self.app.move_entry(cur_idx, cur_idx + 1, save=False, update_ui_blocks=True)
                    return

    def _on_block_release(self, _event, clicked_card: tk.Frame | None = None) -> None:
        drag_card = self._dragged_card
        press_card = self._pressed_card or clicked_card
        was_drag = self._did_drag
        self._dragged_card = None
        self._pressed_card = None
        self._did_drag = False

        if was_drag:
            if drag_card is not None and drag_card.winfo_exists():
                self._apply_card_surface(drag_card, hovered=True, dragging=False)
            self.app.persist_current_list_order()
        elif press_card is not None and press_card.winfo_exists():
            self.app.show_word_view(getattr(press_card, "real_index", 0))

    def _on_card_hover(self, card_or_container: tk.Frame, hovered: bool) -> None:
        if self._dragged_card is not None:
            return
        self._apply_card_surface(card_or_container, hovered=hovered, dragging=False)

    def _apply_card_surface(self, target: tk.Frame, hovered: bool, dragging: bool) -> None:
        if not target.winfo_exists():
            return
        card = getattr(target, "card", target)
        if not card.winfo_exists():
            return
        t = self.app.theme
        bg = t.BG_CARD_HOVER if (hovered or dragging) else t.BG_CARD
        border = t.ACCENT if dragging else (t.BORDER_HOVER if hovered else t.BORDER)
        card.configure(bg=bg, highlightbackground=border)
        for w in getattr(target, "hover_widgets", getattr(card, "hover_widgets", ())):
            if w.winfo_exists():
                w.configure(bg=bg)
        for b in getattr(target, "hover_buttons", getattr(card, "hover_buttons", ())):
            if b.winfo_exists():
                b.configure(bg=bg)

    def _apply_subcard_surface(self, sub_card: tk.Frame, hovered: bool) -> None:
        if not sub_card.winfo_exists():
            return
        t = self.app.theme
        bg = t.BG_CARD_HOVER if hovered else t.BG_CARD
        border = t.ACCENT if hovered else t.BORDER
        sub_card.configure(bg=bg, highlightbackground=border)
        for w in getattr(sub_card, "sub_widgets", ()):
            if w.winfo_exists():
                w.configure(bg=bg)

