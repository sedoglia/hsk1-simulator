# -*- coding: utf-8 -*-
"""Schermata storico e grafico dei progressi."""
import tkinter as tk
from tkinter import messagebox, ttk

from .. import config, db
from ..i18n import tr
from . import widgets as W


class History(tk.Frame):
    def __init__(self, app):
        super().__init__(app.container, bg=W.COLORS["bg"])
        self.app = app
        app.header(self, tr.t("history_title"))

        attempts = db.get_attempts()
        if not attempts:
            tk.Label(self, text=tr.t("no_history"), font=W.f(14),
                     bg=W.COLORS["bg"], fg=W.COLORS["muted"]).pack(pady=60)
            return

        stats = db.get_stats()
        tk.Label(self, text=tr.t("attempts_count", n=stats["count"],
                                 best=stats["best"], p=stats["passed"]),
                 font=W.f(13, bold=True), bg=W.COLORS["bg"], fg=W.COLORS["text"]).pack(pady=(14, 6))

        self._chart(list(reversed(attempts)))
        self._table(attempts)
        self._buttons()

    # ------------------------------------------------ grafico
    def _chart(self, attempts):
        tk.Label(self, text=tr.t("progress_chart"), font=W.f(12, bold=True),
                 bg=W.COLORS["bg"], fg=W.COLORS["muted"]).pack(pady=(8, 0))
        w, h, pad = 880, 210, 40
        cv = tk.Canvas(self, width=w, height=h, bg=W.COLORS["card"],
                       highlightthickness=1, highlightbackground=W.COLORS["border"])
        cv.pack(pady=8)

        def x(i, n):
            return pad + (i * (w - 2 * pad) / max(1, n - 1)) if n > 1 else w / 2

        def y(v):
            return h - pad - (v / config.TOTAL_MAX_SCORE) * (h - 2 * pad)

        cv.create_line(pad, h - pad, w - pad, h - pad, fill=W.COLORS["border"])
        cv.create_line(pad, pad, pad, h - pad, fill=W.COLORS["border"])
        for v in (0, config.PASS_SCORE, config.TOTAL_MAX_SCORE):
            yy = y(v)
            color = W.COLORS["err"] if v == config.PASS_SCORE else W.COLORS["muted"]
            cv.create_line(pad, yy, w - pad, yy, fill=color,
                           dash=(4, 3) if v == config.PASS_SCORE else (1, 4))
            cv.create_text(pad - 8, yy, text=str(v), anchor="e", font=W.f(9), fill=color)

        n = len(attempts)
        pts = [(x(i, n), y(a["total"])) for i, a in enumerate(attempts)]
        for i in range(1, len(pts)):
            cv.create_line(*pts[i - 1], *pts[i], fill=W.COLORS["accent"], width=2)
        for i, (px, py) in enumerate(pts):
            col = W.COLORS["ok"] if attempts[i]["passed"] else W.COLORS["err"]
            cv.create_oval(px - 4, py - 4, px + 4, py + 4, fill=col, outline="")

    # ------------------------------------------------ tabella
    def _table(self, attempts):
        frame = tk.Frame(self, bg=W.COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=24, pady=10)

        cols = ("date", "listening", "reading", "total", "result", "duration")
        heads = (tr.t("col_date"), tr.t("col_listening"), tr.t("col_reading"),
                 tr.t("col_total"), tr.t("col_result"), tr.t("col_duration"))
        widths = (150, 90, 90, 80, 130, 90)
        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=W.f(11))
        style.configure("Treeview.Heading", font=W.f(11, bold=True))

        self.tv = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c, hd, wd in zip(cols, heads, widths):
            self.tv.heading(c, text=hd)
            self.tv.column(c, anchor="center", width=wd)
        for a in attempts:
            res = tr.t("passed") if a["passed"] else tr.t("failed")
            dur = a.get("duration_s") or 0
            dur_s = f"{dur // 60:02d}:{dur % 60:02d}"
            # iid = id del tentativo, per poterlo eliminare
            self.tv.insert("", "end", iid=str(a["id"]),
                           values=(a["datetime"], a["listening"], a["reading"],
                                   a["total"], res, dur_s))
        self.tv.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

    def _buttons(self):
        row = tk.Frame(self, bg=W.COLORS["bg"])
        row.pack(pady=(0, 16))
        W.button(row, tr.t("delete_selected"), self._delete_selected, kind="ghost").pack(side="left", padx=8)
        W.button(row, tr.t("delete_all"), self._delete_all, kind="primary").pack(side="left", padx=8)

    def _delete_selected(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo(tr.t("history_title"), tr.t("no_selection"))
            return
        if messagebox.askyesno(tr.t("history_title"), tr.t("confirm_delete")):
            for iid in sel:
                db.delete_attempt(int(iid))
            self.app.show_history()

    def _delete_all(self):
        if messagebox.askyesno(tr.t("history_title"), tr.t("confirm_delete_all")):
            db.clear_attempts()
            self.app.show_history()
