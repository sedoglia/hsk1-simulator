# -*- coding: utf-8 -*-
"""Schermata iniziale / home screen."""
import tkinter as tk

from ..i18n import tr
from . import widgets as W


class Welcome(tk.Frame):
    def __init__(self, app):
        super().__init__(app.container, bg=W.COLORS["bg"])
        self.app = app
        app.header(self, tr.t("app_title"), with_home=False)

        body = tk.Frame(self, bg=W.COLORS["bg"])
        body.pack(fill="both", expand=True)

        center = tk.Frame(body, bg=W.COLORS["bg"])
        center.place(relx=0.5, rely=0.45, anchor="center")

        tk.Label(center, text="汉语水平考试 · HSK 1", font=W.f(30, bold=True, cn=True),
                 bg=W.COLORS["bg"], fg=W.COLORS["primary"]).pack(pady=(0, 6))
        tk.Label(center, text=tr.t("subtitle"), font=W.f(14),
                 bg=W.COLORS["bg"], fg=W.COLORS["muted"]).pack(pady=(0, 4))
        tk.Label(center, text=tr.t("info_line"), font=W.f(11),
                 bg=W.COLORS["bg"], fg=W.COLORS["muted"]).pack(pady=(0, 28))

        W.button(center, tr.t("start_test"), app.show_exam, kind="primary",
                 font_size=16, width=26).pack(pady=7)
        W.button(center, tr.t("history_btn"), app.show_history, kind="accent",
                 font_size=13, width=26).pack(pady=7)
        W.button(center, tr.t("settings_btn"), app.show_settings, kind="ghost",
                 font_size=13, width=26).pack(pady=7)
