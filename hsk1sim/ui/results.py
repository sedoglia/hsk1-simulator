# -*- coding: utf-8 -*-
"""Schermata dei risultati / results screen."""
import threading
import tkinter as tk

from .. import config, db
from ..audio import player
from ..emoji_render import emoji_to_image
from ..i18n import tr
from ..tts import tts
from . import widgets as W


class Results(tk.Frame):
    def __init__(self, app, exam):
        super().__init__(app.container, bg=W.COLORS["bg"])
        self.app = app
        self.exam = exam
        self.sc = exam.score()
        self.show_review = False

        # salva il tentativo una sola volta (con data/ora e dettagli per-parte)
        if not getattr(exam, "_saved", False):
            exam._attempt_id = db.save_attempt(
                self.sc["listening_score"], self.sc["reading_score"],
                self.sc["total"], self.sc["passed"],
                exam.duration_seconds(), tr.lang, details=exam.details())
            exam._saved = True
        self.attempt_id = getattr(exam, "_attempt_id", None)

        app.header(self, tr.t("results_title"))
        self._build()

    def _build(self):
        for w in self.winfo_children()[1:]:
            w.destroy()
        sc = self.sc

        banner_color = W.COLORS["ok"] if sc["passed"] else W.COLORS["err"]
        banner = tk.Frame(self, bg=banner_color)
        banner.pack(fill="x")
        tk.Label(banner, text=tr.t("passed") if sc["passed"] else tr.t("failed"),
                 font=W.f(22, bold=True), bg=banner_color, fg="white").pack(pady=14)

        scores = tk.Frame(self, bg=W.COLORS["bg"])
        scores.pack(pady=18)
        self._score_card(scores, tr.t("listening_score"), sc["listening_score"],
                         config.SECTION_MAX_SCORE, W.COLORS["accent"])
        self._score_card(scores, tr.t("reading_score"), sc["reading_score"],
                         config.SECTION_MAX_SCORE, W.COLORS["accent"])
        self._score_card(scores, tr.t("total_score"), sc["total"],
                         config.TOTAL_MAX_SCORE, banner_color, big=True)

        tk.Label(self, text=tr.t("pass_hint", n=config.PASS_SCORE), font=W.f(11),
                 bg=W.COLORS["bg"], fg=W.COLORS["muted"]).pack()
        tk.Label(self, text=tr.t("correct_count",
                                 c=sc["listening_correct"] + sc["reading_correct"],
                                 t=sc["listening_total"] + sc["reading_total"]),
                 font=W.f(12, bold=True), bg=W.COLORS["bg"], fg=W.COLORS["text"]).pack(pady=(4, 12))

        btns = tk.Frame(self, bg=W.COLORS["bg"])
        btns.pack(pady=(0, 8))
        W.button(btns, tr.t("hide_review") if self.show_review else tr.t("review_answers"),
                 self._toggle_review, kind="accent").pack(side="left", padx=8)
        W.button(btns, tr.t("start_test"), self.app.show_exam, kind="primary").pack(side="left", padx=8)
        W.button(btns, tr.t("history_btn"), self.app.show_history, kind="accent").pack(side="left", padx=8)
        W.button(btns, tr.t("back_home"), self.app.go_home, kind="ghost").pack(side="left", padx=8)
        if self.attempt_id is not None:
            W.button(btns, tr.t("delete_result"), self._delete_this, kind="ghost").pack(side="left", padx=8)

        if self.show_review:
            self._build_review()

    def _delete_this(self):
        if self.attempt_id is not None:
            db.delete_attempt(self.attempt_id)
            self.attempt_id = None
            self.exam._saved = False
        self.app.show_history()

    def _score_card(self, parent, title, value, maxv, color, big=False):
        c = W.card(parent)
        c.pack(side="left", padx=12)
        tk.Label(c, text=title, font=W.f(12, bold=True),
                 bg=W.COLORS["card"], fg=W.COLORS["muted"]).pack(padx=28, pady=(14, 2))
        tk.Label(c, text=f"{value}", font=W.f(40 if big else 30, bold=True),
                 bg=W.COLORS["card"], fg=color).pack(padx=28)
        tk.Label(c, text=f"/ {maxv}", font=W.f(12),
                 bg=W.COLORS["card"], fg=W.COLORS["muted"]).pack(padx=28, pady=(0, 14))

    def _toggle_review(self):
        self.show_review = not self.show_review
        self._build()

    # ------------------------------------------------ revisione
    def _build_review(self):
        outer = tk.Frame(self, bg=W.COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        canvas = tk.Canvas(outer, bg=W.COLORS["bg"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=W.COLORS["bg"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=900)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))

        for n, q in enumerate(self.exam.listening + self.exam.reading, 1):
            self._review_row(inner, n, q)

    def _opt_label(self, q, idx):
        if idx is None:
            return tr.t("no_answer")
        opt = q.options[idx]
        if opt["kind"] == "tf":
            return tr.t("true") if opt["value"] else tr.t("false")
        if opt["kind"] == "image":
            meaning = opt.get(tr.lang) or opt.get("en") or ""
            return f"{opt['emoji']}  {meaning}"
        return opt["zh"]

    def _review_row(self, parent, n, q):
        ok = q.is_correct
        row = tk.Frame(parent, bg=W.COLORS["ok_bg"] if ok else W.COLORS["err_bg"],
                       highlightthickness=1, highlightbackground=W.COLORS["border"])
        row.pack(fill="x", pady=4)
        head = tk.Frame(row, bg=row["bg"])
        head.pack(fill="x", padx=14, pady=(8, 2))
        sec = tr.t("section_listening") if q.section == "listening" else tr.t("section_reading")
        tk.Label(head, text=f"#{n}  {sec} · {tr.t('part')} {q.part}",
                 font=W.f(11, bold=True), bg=row["bg"], fg=W.COLORS["muted"]).pack(side="left")
        tk.Label(head, text=tr.t("review_correct") if ok else tr.t("review_wrong"),
                 font=W.f(11, bold=True), bg=row["bg"],
                 fg=W.COLORS["ok"] if ok else W.COLORS["err"]).pack(side="right")

        # contenuto cinese + pinyin + traduzione
        zh = tk.Frame(row, bg=row["bg"])
        zh.pack(fill="x", padx=14)
        tk.Label(zh, text=q.review_zh, font=W.f(16, bold=True, cn=True),
                 bg=row["bg"], fg=W.COLORS["text"], anchor="w").pack(anchor="w")
        if q.review_pinyin and self.app.settings["show_pinyin"]:
            tk.Label(zh, text=q.review_pinyin, font=W.f(10), bg=row["bg"],
                     fg=W.COLORS["muted"], anchor="w").pack(anchor="w")
        tk.Label(zh, text=q.review_it if tr.lang == "it" else q.review_en, font=W.f(11, True),
                 bg=row["bg"], fg=W.COLORS["accent"], anchor="w").pack(anchor="w")
        if q.grammar_point:
            point = q.grammar_point[0] if tr.lang == "it" else q.grammar_point[1]
            tk.Label(zh, text=f"📐 {point}", font=W.f(11), bg=row["bg"],
                     fg=W.COLORS["primary"], anchor="w").pack(anchor="w")

        ans = tk.Frame(row, bg=row["bg"])
        ans.pack(fill="x", padx=14, pady=(2, 4))
        tk.Label(ans, text=f"{tr.t('your_answer')}: {self._opt_label(q, q.user_answer)}",
                 font=W.f(11), bg=row["bg"],
                 fg=W.COLORS["ok"] if ok else W.COLORS["err"]).pack(side="left")
        if not ok:
            tk.Label(ans, text=f"   |   {tr.t('correct_answer')}: {self._opt_label(q, q.correct)}",
                     font=W.f(11, bold=True), bg=row["bg"], fg=W.COLORS["ok"]).pack(side="left")

        if q.section == "listening":
            W.button(row, tr.t("play_again"),
                     lambda q=q: self._replay(q), kind="ghost", font_size=10).pack(
                anchor="w", padx=14, pady=(0, 8))

    def _replay(self, q):
        def work():
            paths = [tts.synth(t) for t in q.audio_texts]
            player.play_sequence([p for p in paths if p])
        threading.Thread(target=work, daemon=True).start()
