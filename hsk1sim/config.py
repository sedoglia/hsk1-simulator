# -*- coding: utf-8 -*-
"""Percorsi e costanti dell'applicazione / paths and app constants."""
import os

# --- Percorsi ---
PKG_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PKG_DIR, "data")
ASSET_DIR = os.path.join(PKG_DIR, "assets")
APPDATA_DIR = os.path.join(os.path.dirname(PKG_DIR), "userdata")
CACHE_DIR = os.path.join(APPDATA_DIR, "audio_cache")
DB_PATH = os.path.join(APPDATA_DIR, "history.db")

# Limita le domande alle 150 parole del syllabus ufficiale HSK1 (consigliato).
# False = usa il nucleo esteso ~295 (le 150 + aggiunte comuni HSK 3.0).
OFFICIAL_150_ONLY = True

VOCAB_FILE = os.path.join(DATA_DIR, "vocab_hsk1.json")
SENTENCES_FILE = os.path.join(DATA_DIR, "sentences.json")
DIALOGUES_FILE = os.path.join(DATA_DIR, "dialogues.json")
GRAMMAR_FILE = os.path.join(DATA_DIR, "grammar.json")

for _d in (APPDATA_DIR, CACHE_DIR):
    os.makedirs(_d, exist_ok=True)

# --- Struttura esame HSK1 ---
QUESTIONS_PER_PART = 5
LISTENING_PARTS = 4          # 4 parti x 5 = 20 domande
READING_PARTS = 4            # 4 parti x 5 = 20 domande
TOTAL_QUESTIONS = (LISTENING_PARTS + READING_PARTS) * QUESTIONS_PER_PART  # 40

SECTION_MAX_SCORE = 100      # ogni sezione vale 100
TOTAL_MAX_SCORE = 200        # ascolto + lettura
PASS_SCORE = 120             # soglia di sufficienza

# Tempo per sezione (secondi) - dal SYLLABUS UFFICIALE (HSK 考试大纲 一级) e dal 样卷
#   听力 (20 题): 约 15 分钟 · 填写答题卡: 3 分钟 · 阅读 (20 题): 17 分钟
#   共计 40 题, 约 35 min effettivi · totale ~40 min (incl. 5 min dati personali)
LISTENING_TIME_SEC = 15 * 60     # comprensione orale: ~15 minuti
READING_TIME_SEC = 17 * 60       # comprensione del testo: 17 minuti (syllabus ufficiale)
ANSWER_CARD_TIME_SEC = 3 * 60    # 3 minuti per il foglio risposte (dopo l'ascolto)
PERSONAL_INFO_TIME_SEC = 5 * 60  # 5 minuti per i dati personali (inclusi nel totale)

# Numero di volte in cui l'audio viene riprodotto nell'ascolto reale
LISTENING_PLAYS = 2

# --- TTS ---
EDGE_VOICE = "zh-CN-XiaoxiaoNeural"   # voce online di alta qualita
EDGE_RATE = "-10%"                     # leggermente piu lenta (livello principiante)

# --- UI ---
APP_TITLE = "HSK1 — Simulatore d'esame"
DEFAULT_LANGUAGE = "it"               # "it" oppure "en"
EMOJI_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\seguiemj.ttf",  # Segoe UI Emoji (Windows, a colori)
]
