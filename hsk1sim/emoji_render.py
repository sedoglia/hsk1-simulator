# -*- coding: utf-8 -*-
"""Rasterizza le emoji a colori in immagini Tk.

Tkinter su Windows non rende le emoji a colori nel testo: usiamo Pillow con il
font 'Segoe UI Emoji' (glifi a colori, embedded_color) per generare PhotoImage.
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageTk

from . import config

_font_cache = {}
_image_cache = {}   # (tipo, valore, size) -> PhotoImage (mantiene il riferimento vivo)


def _emoji_font(px: int):
    if px in _font_cache:
        return _font_cache[px]
    font = None
    for path in config.EMOJI_FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, px)
                break
            except Exception:
                continue
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
    _font_cache[px] = font
    return font


def emoji_to_image(emoji: str, size: int = 72):
    """Restituisce una ImageTk.PhotoImage quadrata `size`x`size` con l'emoji."""
    cache_key = ("emoji", emoji, size)
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = _emoji_font(int(size * 0.82))
    if font is not None:
        try:
            draw.text(
                (size // 2, size // 2), emoji, font=font,
                anchor="mm", embedded_color=True,
            )
        except TypeError:
            # Pillow molto vecchio senza embedded_color
            draw.text((size // 2, size // 2), emoji, font=font, anchor="mm")
        except Exception:
            pass

    photo = ImageTk.PhotoImage(img)
    _image_cache[cache_key] = photo
    return photo


def visual_to_image(emoji=None, image_path=None, size: int = 72):
    """Carica una scena fotografica, con fallback all'emoji."""
    if not image_path or not os.path.exists(image_path):
        return emoji_to_image(emoji or "❓", size)

    cache_key = ("file", image_path, size)
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    with Image.open(image_path) as source:
        image = source.convert("RGB")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (size, size), "white")
        canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
    photo = ImageTk.PhotoImage(canvas)
    _image_cache[cache_key] = photo
    return photo
