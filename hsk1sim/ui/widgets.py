# -*- coding: utf-8 -*-
"""Tema e widget riusabili / shared theme and widgets."""
import tkinter as tk

COLORS = {
    "bg":        "#f4f5f9",
    "card":      "#ffffff",
    "primary":   "#c0392b",   # rosso HSK
    "primary_d": "#922b21",
    "accent":    "#2c6fbb",
    "text":      "#1f2733",
    "muted":     "#6b7280",
    "ok":        "#1e8449",
    "ok_bg":     "#e8f6ee",
    "err":       "#c0392b",
    "err_bg":    "#fdecea",
    "sel":       "#fff3cd",
    "sel_bd":    "#e0a800",
    "border":    "#d9dce3",
}

FONT_UI = "Segoe UI"
FONT_CN = "Microsoft YaHei"


def f(size, bold=False, cn=False):
    return (FONT_CN if cn else FONT_UI, size, "bold" if bold else "normal")


def button(parent, text, command, kind="primary", width=None, font_size=12):
    bg = {"primary": COLORS["primary"], "accent": COLORS["accent"],
          "ghost": COLORS["card"], "ok": COLORS["ok"]}.get(kind, COLORS["primary"])
    fg = COLORS["text"] if kind == "ghost" else "white"
    b = tk.Button(
        parent, text=text, command=command, font=f(font_size, bold=True),
        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2", padx=18, pady=10,
        highlightthickness=1 if kind == "ghost" else 0,
        highlightbackground=COLORS["border"],
    )
    if width:
        b.configure(width=width)
    return b


def card(parent, **kw):
    return tk.Frame(parent, bg=COLORS["card"], highlightthickness=1,
                    highlightbackground=COLORS["border"], **kw)
