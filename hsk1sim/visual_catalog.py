# -*- coding: utf-8 -*-
"""Catalogo delle immagini usate nelle domande con figure.

Combina:
  - le SCENE curate (assets/scenes/sNN.jpg) mappate a frasi/dialoghi/parole;
  - le FOTO scaricate (assets/words/, licenza CC, vedi data/image_credits.json),
    elencate in data/word_images.json come { hanzi: ["words/xxx.jpg", ...] }.

Ogni concetto può avere PIÙ immagini: la scelta è casuale a ogni domanda, così
ripetendo il test compaiono figure diverse (difficoltà più realistica).
"""
import json
import os
import random

from . import config


def _scene(number):
    return os.path.join(config.ASSET_DIR, "scenes", f"s{number:02}.jpg")


SENTENCE_SCENES = {
    "我喜欢喝茶。": _scene(1),
    "这是我的书。": _scene(2),
    "他在学校工作。": _scene(3),
    "我有一只猫。": _scene(4),
    "妈妈在做菜。": _scene(5),
    "今天天气很好。": _scene(6),
    "他喜欢看电视。": _scene(7),
    "这个苹果很好吃。": _scene(8),
    "我的狗很大。": _scene(9),
    "老师在教室里。": _scene(10),
    "我每天喝牛奶。": _scene(11),
    "请坐这把椅子。": _scene(12),
    "我爸爸是医生。": _scene(13),
    "外面在下雨。": _scene(14),
    "她有很多衣服。": _scene(15),
    "我坐飞机去中国。": _scene(16),
    "桌子上有一杯水。": _scene(17),
    "他在打电话。": _scene(18),
    "学生在看书。": _scene(19),
    "我要一杯茶。": _scene(20),
    "他坐出租车去机场。": _scene(21),
    "医院在前面。": _scene(22),
    "我喜欢吃米饭。": _scene(23),
    "弟弟在睡觉。": _scene(24),
    "这本书很新。": _scene(25),
    "妈妈买了很多水果。": _scene(26),
    "我们一起去商店。": _scene(27),
    "桌子上有三本书。": _scene(28),
    "这里很热。": _scene(29),
    "我没有钱。": _scene(30),
    "他在医院工作。": _scene(31),
}

DIALOGUE_SCENES = {
    "我是中国人。": _scene(16),
    "现在三点。": _scene(32),
    "这是一本书。": _scene(2),
    "我去学校。": _scene(3),
    "二十块。": _scene(30),
    "她在家。": _scene(4),
    "我喝茶。": _scene(1),
    "他是我的老师。": _scene(10),
    "我坐飞机去。": _scene(16),
    "明天有雨。": _scene(14),
    "我想买衣服。": _scene(15),
    "它叫小白。": _scene(4),
    "在桌子上。": _scene(17),
    "他是医生。": _scene(13),
}

# Parola-chiave -> scena curata (per le domande parola-immagine).
WORD_SCENES = {
    "老师": _scene(10), "医生": _scene(13), "学生": _scene(19),
    "吃": _scene(23), "喝": _scene(1), "看": _scene(7), "读": _scene(19),
    "工作": _scene(31), "买": _scene(26), "坐": _scene(12),
    "打电话": _scene(18), "睡觉": _scene(24), "下雨": _scene(14),
    "热": _scene(29), "茶": _scene(1), "水": _scene(17),
    "米饭": _scene(23), "菜": _scene(5), "苹果": _scene(8),
    "水果": _scene(26), "杯子": _scene(17), "书": _scene(2),
    "电视": _scene(7), "钱": _scene(30), "衣服": _scene(15),
    "椅子": _scene(12), "学校": _scene(3), "家": _scene(4),
    "商店": _scene(27), "医院": _scene(22), "中国": _scene(16),
    "飞机": _scene(16), "出租车": _scene(21), "狗": _scene(9),
    "猫": _scene(4), "天气": _scene(6), "点": _scene(32),
}

# Foto scaricate (CC) per concetto.
_DL = {}
_dl_path = os.path.join(config.DATA_DIR, "word_images.json")
if os.path.exists(_dl_path):
    with open(_dl_path, encoding="utf-8") as f:
        _raw = json.load(f)
    for hanzi, rels in _raw.items():
        abs_paths = [os.path.join(config.ASSET_DIR, *p.split("/")) for p in rels]
        _DL[hanzi] = [p for p in abs_paths if os.path.exists(p)]

# Immagini per concetto = scena curata (se presente) + foto scaricate (dedup).
WORD_IMAGES = {}
for _h in set(WORD_SCENES) | set(_DL):
    imgs = []
    if _h in WORD_SCENES:
        imgs.append(WORD_SCENES[_h])
    imgs.extend(_DL.get(_h, []))
    seen, uniq = set(), []
    for p in imgs:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    if uniq:
        WORD_IMAGES[_h] = uniq


def word_images(hanzi):
    """Tutte le immagini disponibili per un concetto (lista, eventualmente vuota)."""
    return WORD_IMAGES.get(hanzi, [])


def has_word_image(hanzi):
    return bool(WORD_IMAGES.get(hanzi))


def word_scene(hanzi):
    """Un'immagine (casuale) per il concetto, o None. Casuale = varietà tra test."""
    imgs = WORD_IMAGES.get(hanzi)
    return random.choice(imgs) if imgs else None


def sentence_image(sentence_zh, key=None):
    """Immagine per una frase: scena curata se c'è, altrimenti foto della parola-chiave."""
    if sentence_zh in SENTENCE_SCENES:
        return SENTENCE_SCENES[sentence_zh]
    if key:
        return word_scene(key)
    return None


def sentence_has_image(sentence_zh, key=None):
    return sentence_zh in SENTENCE_SCENES or (key is not None and has_word_image(key))


def dialogue_scene(answer):
    return DIALOGUE_SCENES.get(answer)
