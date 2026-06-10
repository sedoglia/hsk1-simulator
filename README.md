# HSK1 Exam Simulator · Simulatore d'esame HSK1

A bilingual **Python / Tkinter** desktop application that faithfully replicates the official
**HSK Level 1** Chinese proficiency exam (Hanban / Center for Language Education and
Cooperation syllabus).  
40 randomly-generated questions every run · Listening + Reading · Neural TTS · Real photos ·
Score 200 · Pass ≥ 120.

Un'applicazione desktop Python con GUI bilingue che simula fedelmente l'esame di
certificazione HSK di livello 1. Test completamente diverso a ogni esecuzione.

---

## 🇬🇧 English

### What it does
This simulator reproduces all 8 question types of the official HSK1 paper, verified against
the 考试大纲 (official syllabus), the 样卷 (sample paper) published by CLEC, and the real
exam papers H10901–H11005.

| | Listening 听力 | Reading 阅读 |
|---|---|---|
| **Part 1** | Short phrase → picture True/False | Word + picture True/False |
| **Part 2** | Sentence → pick 1 from 3 pictures | Sentence → pick 1 from 6 pictures (A–F) |
| **Part 3** | Dialogue → pick 1 from 6 pictures (A–F) | Question → match answer from 6 (A–F) |
| **Part 4** | Statement + question → pick answer | Complete the sentence (word bank of 6) |

- **Timing**: Listening ~15 min · +3 min answer sheet · Reading 17 min · Total ~40 min
- **Scoring**: Listening /100 + Reading /100 = **/200** · **Pass ≥ 120**
- **Audio played twice** per question (Listening), just like the real exam
- **Pinyin** shown on all questions (official exam format)
- **Worked example** (例如) at the start of each part

### Key features
- **Faithful exam layout**: one full part (5 questions) per screen; matching parts show a shared
  A–F bank, exactly like the official paper.
- **Always different**: questions, images and dialogues are generated fresh each run from a bank
  of 123 sentences, 64 dialogues and 64 grammar items — all strictly HSK1 vocabulary.
- **Neural TTS**: `edge-tts` (Microsoft Xiaoxiao Neural voice, zh-CN) with automatic offline
  fallback (`pyttsx3`). Speech rate adapts to sentence length so longer phrases are easier to follow.
- **Real photos**: 100+ CC-licensed photos (Openverse) + 32 curated scene pictures. Every
  picturable concept has ≥ 2 different photos, so repeated tests show different images.
  All image credits are logged in `data/image_credits.json`.
- **Official vocabulary**: 150 words from the official HSK1 syllabus
  (`data/official_150.json`), extended set of ~295 words available via config.
- **History & progress**: every attempt saved in SQLite with timestamp, per-part breakdown,
  duration. Score-trend chart with pass-line at 120. Delete individual results or clear all.
- **Bilingual UI** (Italian / English): toggle on the fly without restarting.
- **31 automated tests** covering exam structure, timing, image consistency, grammar bank
  integrity, vocabulary conformity and variety across runs.

### Requirements
- **Windows** (tested on Windows 11, Python 3.14 — Python 3.10+ should work)
- Internet connection **recommended** for high-quality TTS (not required — offline fallback works)

### Installation
```powershell
pip install -r requirements.txt
python run.py
```

### Run tests
```powershell
python -m unittest discover -s tests -v
```

### Project layout
```
run.py                    # launcher
requirements.txt
hsk1sim/
  config.py               # paths, exam constants
  i18n.py                 # bilingual strings (IT/EN)
  tts.py                  # hybrid TTS (edge-tts + pyttsx3 fallback)
  audio.py                # Windows MCI audio player
  emoji_render.py         # photo/emoji → Tkinter PhotoImage
  visual_catalog.py       # sentence/word → image path mapping
  exam.py                 # exam model, scoring, per-part details
  question_gen.py         # generators for all 8 question types
  db.py                   # SQLite history (save, delete, clear, stats)
  assets/
    scenes/               # 32 curated exam scene photos
    words/                # 70+ CC-licensed concept photos
  data/
    vocab_hsk1.json       # 295 HSK1 words (hanzi, pinyin, IT, EN, emoji, category)
    official_150.json     # the 150 official HSK1 words
    sentences.json        # 123 natural HSK1 sentences (keyed to image concepts)
    dialogues.json        # 64 Q&A dialogue pairs
    grammar.json          # 64 fill-in-the-blank grammar items
    word_images.json      # concept → photo file list
    image_credits.json    # license / attribution for CC photos
  ui/
    app.py                # main window, screen routing, language toggle
    welcome.py            # home screen
    exam_view.py          # exam UI (per-part, A–F bank, audio controls)
    results.py            # score screen + answer review
    history.py            # history table + trend chart
    settings_view.py      # settings (timer, pinyin, voice test)
    widgets.py            # shared theme, colors, button helper
tests/
  test_exam_structure.py  # 19 structure/scoring/timing/randomness tests
  test_images.py          # 9 image coverage/consistency/variety tests
  test_audio.py           # 3 audio sequence/cancellation tests
userdata/                 # created at runtime: history.db + audio cache
```

### Notes
- **Official exams**: the `official_exams/` folder (not in this repo) can hold the Hanban
  PDF + MP3 papers (H10901–H11005) for reference. They are excluded from the repo because
  of copyright.
- **Extending vocabulary**: run `python build_vocab.py` to regenerate `vocab_hsk1.json`.
  Set `OFFICIAL_150_ONLY = False` in `config.py` to enable the full ~295-word set.
- **Adding images**: run `python fetch_images.py` to download more CC photos from Openverse.
- **Validating HSK1 conformity**: run `python validate_banks.py` to check that all sentences
  and dialogues use only official HSK1 words.

---

## 🇮🇹 Italiano

### Cosa fa
Questo simulatore riproduce tutti e 8 i tipi di quesito dell'esame ufficiale HSK1, verificati
sul 考试大纲 (syllabus ufficiale), sul 样卷 (prova campione del CLEC) e sugli esami reali
H10901–H11005.

| | Ascolto 听力 | Lettura 阅读 |
|---|---|---|
| **Parte 1** | Frase breve → immagine Vero/Falso | Parola + immagine Vero/Falso |
| **Parte 2** | Frase → scegli 1 tra 3 immagini | Frase → scegli 1 tra 6 immagini (A–F) |
| **Parte 3** | Dialogo → scegli 1 tra 6 immagini (A–F) | Domanda → abbina risposta tra 6 (A–F) |
| **Parte 4** | Enunciato + domanda → scegli risposta | Completa la frase (banco 6 parole) |

- **Tempi**: Ascolto ~15 min · +3 min scheda risposte · Lettura 17 min · Totale ~40 min
- **Punteggio**: Ascolto /100 + Lettura /100 = **/200** · **Sufficienza ≥ 120**
- **Audio riprodotto due volte** (Ascolto), come nell'esame reale
- **Pinyin** su tutte le domande (formato ufficiale)
- **Esempio svolto** (例如) all'inizio di ogni parte

### Caratteristiche principali
- **Layout fedele**: una parte intera (5 quesiti) per schermata; le parti ad abbinamento mostrano
  un banco unico A–F, esattamente come il foglio ufficiale.
- **Sempre diverso**: domande, immagini e dialoghi generati ad ogni esecuzione da una banca di
  123 frasi, 64 dialoghi e 64 item grammaticali — tutto strettamente vocabolario HSK1.
- **TTS neurale**: `edge-tts` (voce Microsoft Xiaoxiao Neural, zh-CN) con fallback offline
  automatico (`pyttsx3`). La velocità si adatta alla lunghezza della frase.
- **Foto reali**: 100+ foto con licenza CC (Openverse) + 32 scene curate. Ogni concetto
  illustrabile ha ≥ 2 foto diverse → test ripetuti mostrano immagini diverse.
  Crediti in `data/image_credits.json`.
- **Vocabolario ufficiale**: 150 parole del syllabus HSK1 ufficiale (`data/official_150.json`),
  set esteso di ~295 voci disponibile via config.
- **Storico e progressi**: ogni tentativo salvato in SQLite con data/ora e dettaglio per-parte,
  grafico con soglia 120, pulsanti per eliminare singoli esiti o azzerare tutto.
- **UI IT/EN** commutabile al volo.
- **31 test automatici** su struttura, punteggio, tempi, immagini, grammatica e varietà.

### Requisiti
- **Windows** (testato su Windows 11, Python 3.14)
- Connessione internet **consigliata** per TTS di alta qualità (non obbligatoria)

### Installazione e avvio
```powershell
pip install -r requirements.txt
python run.py
```

### Test automatici
```powershell
python -m unittest discover -s tests -v
```

---

## Screenshots

| Home | Ascolto P1 | Abbinamento (banco A–F) | Risultati |
|---|---|---|---|
| UI bilingue | Frase + foto + ✓/✗ | 6 opzioni condivise | Punteggi + revisione |

---

## License

Code: **MIT**.  
Photos in `assets/words/`: **CC0 / CC-BY** (see `data/image_credits.json` for individual
attributions).  
Photos in `assets/scenes/`: curated for this project.  
Official Hanban exam papers (not included): © Hanban / Center for Language Education and
Cooperation.
