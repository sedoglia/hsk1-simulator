# -*- coding: utf-8 -*-
"""Schermata di svolgimento dell'esame.

Ogni PARTE (5 quesiti) è mostrata su un'unica schermata, come nel foglio d'esame
ufficiale. Le parti ad abbinamento (Ascolto P3, Lettura P2/P3/P4) presentano un
unico banco di 6 opzioni (A–F) e i 5 quesiti vi si abbinano scegliendo la lettera.
"""
import queue
import threading
import time
import tkinter as tk

from .. import config
from ..audio import player
from ..emoji_render import visual_to_image
from ..exam import Exam
from ..i18n import tr
from ..question_gen import EXAMPLES
from ..tts import tts
from . import widgets as W

# parti ad abbinamento: banco condiviso di 6 opzioni (A-F) per 5 quesiti
MATCHING = {("listening", 3), ("reading", 2), ("reading", 3), ("reading", 4)}


class ExamView(tk.Frame):
    def __init__(self, app):
        super().__init__(app.container, bg=W.COLORS["bg"])
        self.app = app
        self.exam = Exam.generate()
        app.exam = self.exam
        # 8 parti da 5 quesiti: L1..L4, R1..R4
        self.parts = ([self.exam.listening[i * 5:(i + 1) * 5] for i in range(4)] +
                      [self.exam.reading[i * 5:(i + 1) * 5] for i in range(4)])
        self.part_index = 0
        self.listening_remaining = config.LISTENING_TIME_SEC
        self.reading_remaining = config.READING_TIME_SEC
        self._timer_job = None
        self._scroll_canvas = None

        for q in self.exam.listening + self.exam.reading:
            q._plays_used = 0

        app.header(self, tr.t("app_title"))
        self.body = tk.Frame(self, bg=W.COLORS["bg"])
        self.body.pack(fill="both", expand=True)
        self._show_loading()

    # ------------------------------------------------ caricamento audio
    def _show_loading(self):
        self._loading = tk.Frame(self.body, bg=W.COLORS["bg"])
        self._loading.place(relx=0.5, rely=0.5, anchor="center")
        self._load_lbl = tk.Label(self._loading, text=tr.t("loading_audio", p=0),
                                   font=W.f(15), bg=W.COLORS["bg"], fg=W.COLORS["text"])
        self._load_lbl.pack(pady=10)
        self._bar_bg = tk.Frame(self._loading, bg=W.COLORS["border"], width=360, height=14)
        self._bar_bg.pack()
        self._bar_bg.pack_propagate(False)
        self._bar = tk.Frame(self._bar_bg, bg=W.COLORS["primary"], width=0, height=14)
        self._bar.place(x=0, y=0)

        texts = self.exam.listening_audio_texts()
        self._load_q = queue.Queue()

        def work():
            tts.prefetch(texts, progress=lambda p: self._load_q.put(("progress", p)))
            self._load_q.put(("done", None))

        threading.Thread(target=work, daemon=True).start()
        self._poll_loading()

    def _poll_loading(self):
        done = False
        try:
            while True:
                kind, val = self._load_q.get_nowait()
                if kind == "progress":
                    self._update_loading(val)
                elif kind == "done":
                    done = True
        except queue.Empty:
            pass
        if done:
            self._begin()
        else:
            self.app.root.after(80, self._poll_loading)

    def _update_loading(self, p):
        if self._load_lbl.winfo_exists():
            self._load_lbl.configure(text=tr.t("loading_audio", p=p))
            self._bar.configure(width=int(360 * p / 100))

    def _begin(self):
        self._loading.destroy()
        player.warmup()  # sveglia una volta la scheda audio (anti-troncamento)
        if tts.last_offline:
            tk.Label(self.body, text=tr.t("offline_warn"), font=W.f(10, bold=True),
                     bg="#fff3cd", fg="#7a5c00").pack(fill="x")
        self.exam.start_ts = time.time()

        self.topbar = tk.Frame(self.body, bg=W.COLORS["bg"])
        self.topbar.pack(fill="x", padx=24, pady=(12, 0))
        self.lbl_pos = tk.Label(self.topbar, font=W.f(14, bold=True),
                                bg=W.COLORS["bg"], fg=W.COLORS["primary"])
        self.lbl_pos.pack(side="left")
        self.lbl_timer = tk.Label(self.topbar, font=W.f(14, bold=True),
                                  bg=W.COLORS["bg"], fg=W.COLORS["accent"])
        self.lbl_timer.pack(side="right")
        self.lbl_answered = tk.Label(self.topbar, font=W.f(11),
                                     bg=W.COLORS["bg"], fg=W.COLORS["muted"])
        self.lbl_answered.pack(side="right", padx=18)

        self.qframe = W.card(self.body)
        self.qframe.pack(fill="both", expand=True, padx=24, pady=10)
        self.nav = tk.Frame(self.body, bg=W.COLORS["bg"])
        self.nav.pack(fill="x", padx=24, pady=(0, 14))

        self._tick()
        self._render_part()

    # ------------------------------------------------ timer
    @property
    def section(self):
        return "listening" if self.part_index < 4 else "reading"

    def _tick(self):
        if self.section == "listening":
            self.listening_remaining = max(0, self.listening_remaining - 1)
            rem = self.listening_remaining
        else:
            self.reading_remaining = max(0, self.reading_remaining - 1)
            rem = self.reading_remaining
        if hasattr(self, "lbl_timer") and self.lbl_timer.winfo_exists():
            self.lbl_timer.configure(text=tr.t("time_left", t=f"{rem // 60:02d}:{rem % 60:02d}"))
        if rem == 0 and self.app.settings["strict_timer"]:
            self._time_up()
            return
        self._timer_job = self.app.root.after(1000, self._tick)

    def _time_up(self):
        if self.section == "listening":
            self.part_index = 4
            self._render_part()
            self._timer_job = self.app.root.after(1000, self._tick)
        else:
            self._finish()

    # ------------------------------------------------ helper scroll
    def _scrollable(self, parent):
        canvas = tk.Canvas(parent, bg=W.COLORS["card"], highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=W.COLORS["card"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=890)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._scroll_canvas = canvas

        def _wheel(e):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-e.delta / 120), "units")
        canvas.bind_all("<MouseWheel>", _wheel)
        return inner

    # ------------------------------------------------ rendering parte
    def _render_part(self, preserve_scroll=False):
        pos = self._scroll_canvas.yview()[0] if (preserve_scroll and self._scroll_canvas) else 0.0
        player.stop()
        for w in self.qframe.winfo_children():
            w.destroy()

        part = self.parts[self.part_index]
        q0 = part[0]
        sec_name = tr.t("section_listening") if self.section == "listening" else tr.t("section_reading")
        base = (0 if self.section == "listening" else 20) + (q0.part - 1) * 5
        self.lbl_pos.configure(
            text=f"{sec_name} · {tr.t('part')} {q0.part} — {tr.t('question')} {base + 1}–{base + 5} {tr.t('of')} 40")
        self._update_answered()

        head = tk.Frame(self.qframe, bg=W.COLORS["card"])
        head.pack(fill="x", padx=24, pady=(14, 4))
        tk.Label(head, text=tr.t(q0.instr_key), font=W.f(13, bold=True), wraplength=850,
                 justify="left", bg=W.COLORS["card"], fg=W.COLORS["text"]).pack(anchor="w")
        if self.app.settings.get("show_examples"):
            self._render_example(head, q0)

        inner = self._scrollable(self.qframe)

        if (self.section, q0.part) in MATCHING:
            self._render_bank(inner, part[0].options)
            for j, q in enumerate(part):
                self._render_match_row(inner, q, base + j + 1)
        else:
            for j, q in enumerate(part):
                self._render_question_row(inner, q, base + j + 1)

        self._render_nav()
        if preserve_scroll and self._scroll_canvas:
            self.app.root.after_idle(lambda: self._scroll_canvas.yview_moveto(pos))

    def _update_answered(self):
        answered = sum(1 for x in self.exam.listening + self.exam.reading
                       if x.user_answer is not None)
        self.lbl_answered.configure(text=tr.t("answered_of", a=answered, t=40))

    # ---- esempio (例如) ----
    def _render_example(self, parent, q):
        ex = EXAMPLES.get((q.section, q.part))
        if not ex:
            return
        box = tk.Frame(parent, bg="#eef3fb", highlightthickness=1, highlightbackground="#c7d6ea")
        box.pack(fill="x", pady=(8, 2))
        tk.Label(box, text=tr.t("example_label"), font=W.f(10, bold=True),
                 bg="#eef3fb", fg=W.COLORS["accent"]).pack(anchor="w", padx=12, pady=(4, 0))
        row = tk.Frame(box, bg="#eef3fb")
        row.pack(anchor="w", padx=12, pady=(2, 6), fill="x")
        if ex["kind"] == "tf" and ex.get("emoji"):
            img = visual_to_image(ex["emoji"], ex.get("image"), 52)
            il = tk.Label(row, image=img, bg="#eef3fb")
            il.image = img
            il.pack(side="left", padx=(0, 6))
        stim = tk.Frame(row, bg="#eef3fb")
        stim.pack(side="left")
        tk.Label(stim, text=ex["zh"], font=W.f(13, bold=True, cn=True),
                 bg="#eef3fb", fg=W.COLORS["text"]).pack(anchor="w")
        if self.app.settings["show_pinyin"] and ex.get("pinyin"):
            tk.Label(stim, text=ex["pinyin"], font=W.f(9),
                     bg="#eef3fb", fg=W.COLORS["muted"]).pack(anchor="w")
        tk.Label(row, text="  →  ", font=W.f(13, bold=True),
                 bg="#eef3fb", fg=W.COLORS["muted"]).pack(side="left")
        if ex["kind"] == "image":
            img = visual_to_image(ex["answer_emoji"], ex.get("answer_image"), 52)
            al = tk.Label(row, image=img, bg="#eef3fb")
            al.image = img
            al.pack(side="left")
        elif ex["kind"] == "tf":
            tk.Label(row, text=ex["answer"], font=W.f(16, bold=True),
                     bg="#eef3fb", fg=W.COLORS["ok"]).pack(side="left")
        else:
            tk.Label(row, text=ex["answer_zh"], font=W.f(13, bold=True, cn=True),
                     bg="#eef3fb", fg=W.COLORS["ok"]).pack(side="left")

    # ---- audio per quesito ----
    def _audio_control(self, parent, q):
        row = tk.Frame(parent, bg=W.COLORS["card"])
        left = config.LISTENING_PLAYS - q._plays_used

        def play():
            if q._plays_used >= config.LISTENING_PLAYS:
                return
            q._plays_used += 1
            paths = [tts.synth(t) for t in q.audio_texts]
            q._play_btn.configure(state="disabled", cursor="arrow")
            self._refresh_play(q)

            def finished():
                if self.winfo_exists():
                    self.app.root.after(0, lambda: self._audio_done(q))
            player.play_sequence([p for p in paths if p], on_done=finished)

        q._play_btn = W.button(row, tr.t("play_audio") if q._plays_used == 0 else tr.t("play_again"),
                               play, kind="accent", font_size=11)
        q._play_btn.pack(side="left")
        if left <= 0:
            q._play_btn.configure(state="disabled", cursor="arrow")
        q._plays_lbl = tk.Label(row, text=tr.t("plays_left", n=max(0, left)),
                                font=W.f(9), bg=W.COLORS["card"], fg=W.COLORS["muted"])
        q._plays_lbl.pack(side="left", padx=8)
        return row

    def _refresh_play(self, q):
        left = config.LISTENING_PLAYS - q._plays_used
        if q._plays_lbl.winfo_exists():
            q._plays_lbl.configure(text=tr.t("plays_left", n=max(0, left)))
        if q._play_btn.winfo_exists():
            q._play_btn.configure(text=tr.t("play_again"))

    def _audio_done(self, q):
        if not q._play_btn.winfo_exists():
            return
        if config.LISTENING_PLAYS - q._plays_used > 0:
            q._play_btn.configure(state="normal", cursor="hand2")

    # ---- banco condiviso A-F ----
    def _render_bank(self, parent, options):
        bank = tk.Frame(parent, bg="#f7f8fb", highlightthickness=1,
                        highlightbackground=W.COLORS["border"])
        bank.pack(fill="x", padx=16, pady=(10, 12))
        is_img = options[0]["kind"] == "image"
        if is_img:
            grid = tk.Frame(bank, bg="#f7f8fb")
            grid.pack(padx=8, pady=8)
            for i, opt in enumerate(options):
                cell = tk.Frame(grid, bg="#f7f8fb")
                cell.grid(row=i // 3, column=i % 3, padx=8, pady=6)
                img = visual_to_image(opt.get("emoji"), opt.get("image"), 110)
                lab = tk.Label(cell, image=img, bg="#f7f8fb")
                lab.image = img
                lab.pack()
                tk.Label(cell, text=chr(65 + i), font=W.f(12, bold=True),
                         bg="#f7f8fb", fg=W.COLORS["primary"]).pack()
        else:
            for i, opt in enumerate(options):
                line = tk.Frame(bank, bg="#f7f8fb")
                line.pack(fill="x", padx=12, pady=3)
                tk.Label(line, text=f"{chr(65 + i)}.", font=W.f(13, bold=True),
                         bg="#f7f8fb", fg=W.COLORS["primary"]).pack(side="left", padx=(0, 10))
                tk.Label(line, text=opt["zh"], font=W.f(15, bold=True, cn=True),
                         bg="#f7f8fb", fg=W.COLORS["text"]).pack(side="left")
                if opt.get("pinyin") and self.app.settings["show_pinyin"]:
                    tk.Label(line, text=f"  {opt['pinyin']}", font=W.f(10),
                             bg="#f7f8fb", fg=W.COLORS["muted"]).pack(side="left")

    def _render_match_row(self, parent, q, num):
        rowf = tk.Frame(parent, bg=W.COLORS["card"])
        rowf.pack(fill="x", padx=16, pady=4)
        tk.Label(rowf, text=f"{num}.", font=W.f(13, bold=True),
                 bg=W.COLORS["card"], fg=W.COLORS["primary"]).pack(side="left", padx=(0, 10))
        if q.section == "listening":
            self._audio_control(rowf, q).pack(side="left", padx=(0, 12))
        else:
            txt = tk.Frame(rowf, bg=W.COLORS["card"])
            txt.pack(side="left", padx=(0, 12))
            tk.Label(txt, text=q.display_zh, font=W.f(15, bold=True, cn=True),
                     bg=W.COLORS["card"], fg=W.COLORS["text"]).pack(anchor="w")
            if q.display_pinyin and self.app.settings["show_pinyin"]:
                tk.Label(txt, text=q.display_pinyin, font=W.f(10),
                         bg=W.COLORS["card"], fg=W.COLORS["muted"]).pack(anchor="w")
        # selettore A-F
        sel = tk.Frame(rowf, bg=W.COLORS["card"])
        sel.pack(side="right")
        btns = []
        for i in range(len(q.options)):
            chosen = q.user_answer == i
            b = tk.Button(sel, text=chr(65 + i), font=W.f(12, bold=True), width=2,
                          bg=W.COLORS["sel_bd"] if chosen else "white",
                          fg="white" if chosen else W.COLORS["text"], relief="flat",
                          highlightthickness=1, highlightbackground=W.COLORS["border"],
                          cursor="hand2", command=lambda i=i: self._select(q, i))
            b.pack(side="left", padx=2)
            btns.append(b)

        def refresh(q=q, btns=btns):
            for idx, b in enumerate(btns):
                ch = q.user_answer == idx
                b.configure(bg=W.COLORS["sel_bd"] if ch else "white",
                            fg="white" if ch else W.COLORS["text"])
        q._refresh = refresh

    # ---- quesiti non-abbinamento (opzioni proprie) ----
    def _render_question_row(self, parent, q, num):
        rowf = tk.Frame(parent, bg=W.COLORS["card"], highlightthickness=1,
                        highlightbackground=W.COLORS["border"])
        rowf.pack(fill="x", padx=16, pady=5)
        top = tk.Frame(rowf, bg=W.COLORS["card"])
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text=f"{num}.", font=W.f(13, bold=True),
                 bg=W.COLORS["card"], fg=W.COLORS["primary"]).pack(side="left", padx=(0, 10))
        if q.section == "listening":
            self._audio_control(top, q).pack(side="left")

        # stimolo (immagine/parola) per le parti V/F
        if q.qtype == "tf":
            mid = tk.Frame(rowf, bg=W.COLORS["card"])
            mid.pack(padx=12, pady=(0, 6))
            if q.display_image:
                img = visual_to_image(q.display_image, q.display_image_path, 120)
                il = tk.Label(mid, image=img, bg=W.COLORS["card"])
                il.image = img
                il.pack(side="left", padx=10)
            if q.display_zh:
                wf = tk.Frame(mid, bg=W.COLORS["card"])
                wf.pack(side="left", padx=10)
                tk.Label(wf, text=q.display_zh, font=W.f(22, bold=True, cn=True),
                         bg=W.COLORS["card"], fg=W.COLORS["text"]).pack()
                if q.display_pinyin and self.app.settings["show_pinyin"]:
                    tk.Label(wf, text=q.display_pinyin, font=W.f(12),
                             bg=W.COLORS["card"], fg=W.COLORS["muted"]).pack()
            self._tf_buttons(rowf, q)
        else:
            # L2: scelta tra immagini proprie / L4: scelta tra testi propri
            if q.qtype == "image":
                self._image_choices(rowf, q)
            else:
                self._text_choices(rowf, q)

    def _tf_buttons(self, parent, q):
        bar = tk.Frame(parent, bg=W.COLORS["card"])
        bar.pack(pady=(0, 10))
        btns = []
        for i, opt in enumerate(q.options):
            sel = q.user_answer == i
            text = tr.t("true") if opt["value"] else tr.t("false")
            b = tk.Button(bar, text=text, font=W.f(14, bold=True),
                          bg=W.COLORS["sel"] if sel else "white", fg=W.COLORS["text"],
                          relief="flat", cursor="hand2", padx=26, pady=10,
                          highlightthickness=2,
                          highlightbackground=W.COLORS["sel_bd"] if sel else W.COLORS["border"],
                          command=lambda i=i: self._select(q, i))
            b.pack(side="left", padx=14)
            btns.append(b)

        def refresh(q=q, btns=btns):
            for idx, b in enumerate(btns):
                ch = q.user_answer == idx
                b.configure(bg=W.COLORS["sel"] if ch else "white",
                            highlightbackground=W.COLORS["sel_bd"] if ch else W.COLORS["border"])
        q._refresh = refresh

    def _image_choices(self, parent, q):
        grid = tk.Frame(parent, bg=W.COLORS["card"])
        grid.pack(pady=(0, 10))
        cells = []
        for i, opt in enumerate(q.options):
            sel = q.user_answer == i
            cell = tk.Frame(grid, bg=W.COLORS["sel"] if sel else "white",
                            highlightthickness=2,
                            highlightbackground=W.COLORS["sel_bd"] if sel else W.COLORS["border"],
                            cursor="hand2")
            cell.grid(row=0, column=i, padx=10)
            img = visual_to_image(opt.get("emoji"), opt.get("image"), 110)
            lab = tk.Label(cell, image=img, bg=cell["bg"])
            lab.image = img
            lab.pack(padx=8, pady=(8, 2))
            tk.Label(cell, text=chr(65 + i), font=W.f(11, bold=True),
                     bg=cell["bg"], fg=W.COLORS["muted"]).pack(pady=(0, 6))
            self._bind(cell, lambda e, i=i: self._select(q, i))
            cells.append(cell)

        def refresh(q=q, cells=cells):
            for idx, c in enumerate(cells):
                self._set_cell_selected(c, q.user_answer == idx)
        q._refresh = refresh

    def _text_choices(self, parent, q):
        box = tk.Frame(parent, bg=W.COLORS["card"])
        box.pack(fill="x", pady=(0, 10), padx=12)
        cells = []
        for i, opt in enumerate(q.options):
            sel = q.user_answer == i
            cell = tk.Frame(box, bg=W.COLORS["sel"] if sel else "white",
                            highlightthickness=2,
                            highlightbackground=W.COLORS["sel_bd"] if sel else W.COLORS["border"],
                            cursor="hand2")
            cell.pack(fill="x", pady=3)
            r = tk.Frame(cell, bg=cell["bg"])
            r.pack(fill="x", padx=12, pady=6)
            tk.Label(r, text=f"{chr(65 + i)}.", font=W.f(13, bold=True),
                     bg=cell["bg"], fg=W.COLORS["primary"]).pack(side="left", padx=(0, 10))
            tk.Label(r, text=opt["zh"], font=W.f(16, bold=True, cn=True),
                     bg=cell["bg"], fg=W.COLORS["text"]).pack(side="left")
            if opt.get("pinyin") and self.app.settings["show_pinyin"]:
                tk.Label(r, text=f"  {opt['pinyin']}", font=W.f(10),
                         bg=cell["bg"], fg=W.COLORS["muted"]).pack(side="left")
            self._bind(cell, lambda e, i=i: self._select(q, i))
            cells.append(cell)

        def refresh(q=q, cells=cells):
            for idx, c in enumerate(cells):
                self._set_cell_selected(c, q.user_answer == idx)
        q._refresh = refresh

    def _bind(self, widget, command):
        widget.bind("<Button-1>", command)
        widget.configure(cursor="hand2")
        for child in widget.winfo_children():
            self._bind(child, command)

    def _select(self, q, i):
        # aggiorna solo l'evidenziazione in loco (niente re-render -> nessun salto a inizio pagina)
        q.user_answer = i
        if getattr(q, "_refresh", None):
            q._refresh()
        self._update_answered()

    def _recolor_bg(self, widget, bg):
        try:
            widget.configure(bg=bg)
        except tk.TclError:
            pass
        for ch in widget.winfo_children():
            self._recolor_bg(ch, bg)

    def _set_cell_selected(self, cell, chosen):
        bg = W.COLORS["sel"] if chosen else "white"
        cell.configure(bg=bg, highlightbackground=W.COLORS["sel_bd"] if chosen else W.COLORS["border"])
        for ch in cell.winfo_children():
            self._recolor_bg(ch, bg)

    # ------------------------------------------------ navigazione
    def _render_nav(self):
        for w in self.nav.winfo_children():
            w.destroy()
        if self.part_index not in (0, 4):
            W.button(self.nav, tr.t("previous"), self._prev, kind="ghost").pack(side="left")
        if self.part_index == 7:
            W.button(self.nav, tr.t("finish_exam"), self._finish, kind="primary",
                     font_size=13).pack(side="right")
        elif self.part_index == 3:
            W.button(self.nav, tr.t("next_section"), self._next, kind="primary",
                     font_size=13).pack(side="right")
        else:
            W.button(self.nav, tr.t("next"), self._next, kind="accent").pack(side="right")

    def _next(self):
        if self.part_index < 7:
            self.part_index += 1
            self._render_part()

    def _prev(self):
        if self.part_index not in (0, 4):
            self.part_index -= 1
            self._render_part()

    def _finish(self):
        if self._timer_job:
            self.app.root.after_cancel(self._timer_job)
            self._timer_job = None
        player.stop()
        self.exam.end_ts = time.time()
        self.app.show_results(self.exam)
