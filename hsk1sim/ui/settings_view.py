# -*- coding: utf-8 -*-
"""Schermata impostazioni / settings screen."""
import threading
import tkinter as tk

from ..audio import player
from ..i18n import tr
from ..tts import tts
from . import widgets as W


class SettingsView(tk.Frame):
    def __init__(self, app):
        super().__init__(app.container, bg=W.COLORS["bg"])
        self.app = app
        app.header(self, tr.t("settings_title"))

        box = W.card(self)
        box.pack(padx=40, pady=40, fill="x")

        self.var_strict = tk.BooleanVar(value=app.settings["strict_timer"])
        self.var_pinyin = tk.BooleanVar(value=app.settings["show_pinyin"])
        self.var_examples = tk.BooleanVar(value=app.settings["show_examples"])

        for var, key in ((self.var_strict, "strict_timer"),
                         (self.var_pinyin, "show_pinyin"),
                         (self.var_examples, "show_examples")):
            tk.Checkbutton(
                box, text=tr.t(key), variable=var, font=W.f(13),
                bg=W.COLORS["card"], fg=W.COLORS["text"], anchor="w",
                activebackground=W.COLORS["card"], selectcolor="white",
                cursor="hand2",
            ).pack(fill="x", padx=24, pady=14)

        row = tk.Frame(box, bg=W.COLORS["card"])
        row.pack(fill="x", padx=24, pady=18)
        W.button(row, tr.t("voice_test"), self._test_voice, kind="accent").pack(side="left")
        W.button(row, tr.t("save"), self._save, kind="primary").pack(side="right")

    def _save(self):
        self.app.settings["strict_timer"] = self.var_strict.get()
        self.app.settings["show_pinyin"] = self.var_pinyin.get()
        self.app.settings["show_examples"] = self.var_examples.get()
        self.app.go_home()

    def _test_voice(self):
        def work():
            path = tts.synth("你好，欢迎参加 HSK 一级考试。")
            if path:
                player.play(path)
        threading.Thread(target=work, daemon=True).start()
