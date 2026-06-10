# -*- coding: utf-8 -*-
"""Finestra principale e routing delle schermate."""
import tkinter as tk

from .. import config, db
from ..audio import player
from ..i18n import tr
from . import widgets as W


class App:
    def __init__(self):
        db.init_db()
        self.root = tk.Tk()
        self.root.title(config.APP_TITLE)
        self.root.geometry("1000x720")
        self.root.minsize(880, 640)
        self.root.configure(bg=W.COLORS["bg"])

        # stato / impostazioni
        tr.set_language(config.DEFAULT_LANGUAGE)
        self.settings = {"strict_timer": False, "show_pinyin": True, "show_examples": True}
        self.exam = None
        self.index = 0

        self.container = tk.Frame(self.root, bg=W.COLORS["bg"])
        self.container.pack(fill="both", expand=True)

        self._current = (self.show_welcome, {})
        self.show_welcome()

    # ---- utilita ----
    def clear(self):
        player.stop()
        for w in self.container.winfo_children():
            w.destroy()

    def rerender(self):
        func, kw = self._current
        func(**kw)

    def toggle_language(self):
        tr.set_language("en" if tr.lang == "it" else "it")
        self.rerender()

    def header(self, parent, title, with_home=True):
        bar = tk.Frame(parent, bg=W.COLORS["primary"])
        bar.pack(fill="x")
        tk.Label(bar, text=title, font=W.f(18, bold=True),
                 bg=W.COLORS["primary"], fg="white").pack(side="left", padx=20, pady=14)

        lang_btn = tk.Button(
            bar, text="IT" if tr.lang == "en" else "EN",
            command=self.toggle_language, font=W.f(11, bold=True),
            bg="white", fg=W.COLORS["primary"], relief="flat", bd=0,
            cursor="hand2", padx=12, pady=4,
        )
        lang_btn.pack(side="right", padx=16)
        tk.Label(bar, text=tr.t("language"), font=W.f(10),
                 bg=W.COLORS["primary"], fg="white").pack(side="right")

        if with_home:
            tk.Button(bar, text=tr.t("back_home"), command=self.go_home,
                      font=W.f(11, bold=True), bg=W.COLORS["primary_d"], fg="white",
                      relief="flat", bd=0, cursor="hand2", padx=12, pady=6).pack(
                side="right", padx=16)
        return bar

    # ---- navigazione ----
    def go_home(self):
        self.show_welcome()

    def show_welcome(self):
        from .welcome import Welcome
        self._current = (self.show_welcome, {})
        self.clear()
        Welcome(self).pack(fill="both", expand=True)

    def show_settings(self):
        from .settings_view import SettingsView
        self._current = (self.show_settings, {})
        self.clear()
        SettingsView(self).pack(fill="both", expand=True)

    def show_history(self):
        from .history import History
        self._current = (self.show_history, {})
        self.clear()
        History(self).pack(fill="both", expand=True)

    def show_exam(self):
        from .exam_view import ExamView
        self._current = (self.show_exam, {})
        self.clear()
        ExamView(self).pack(fill="both", expand=True)

    def show_results(self, exam):
        from .results import Results
        self._current = (self.show_results, {"exam": exam})
        self.clear()
        Results(self, exam).pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()
