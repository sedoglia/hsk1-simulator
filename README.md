# HSK1 Exam Simulator

> **Versione italiana → [README.it.md](README.it.md)**

A **Python / Tkinter** desktop application that faithfully replicates the official
**HSK Level 1** Chinese proficiency exam, based on the 考试大纲 (official syllabus) and the
样卷 (sample paper) published by the Center for Language Education and Cooperation (CLEC /
教育部中外语言交流合作中心), and verified against the real exam papers H10901–H11005.

Every run generates a **completely different** 40-question test. The app runs entirely on
Windows, works offline (with degraded TTS), and requires no account or subscription.

---

## Table of Contents

1. [Exam structure](#exam-structure)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Running the app](#running-the-app)
6. [Running the tests](#running-the-tests)
7. [Project layout](#project-layout)
8. [Data files](#data-files)
9. [Extending the app](#extending-the-app)
10. [Technical notes](#technical-notes)
11. [License](#license)

---

## Exam structure

The HSK1 exam has two sections and 40 questions in total, each worth 5 points.

| | Listening 听力 (~15 min) | Reading 阅读 (17 min) |
|---|---|---|
| **Part 1** | Short phrase → picture **True / False** | Word + picture **True / False** |
| **Part 2** | Sentence → pick **1 of 3** pictures (A/B/C) | Sentence → pick **1 of 6** pictures (A–F) |
| **Part 3** | Dialogue → pick **1 of 6** pictures (A–F) | Question → match **1 of 6** answers (A–F) |
| **Part 4** | Statement + question → pick **1 of 3** text answers | Complete the blank (word bank of **6**) |

**Timing**: ~15 min Listening · +3 min to fill in the answer sheet · 17 min Reading ·
~40 min total (including 5 min for personal details).

**Score**: Listening / 100 + Reading / 100 = **/ 200** · **Pass ≥ 120 / 200**.

Each Listening question is **played twice**, like the real exam.
All questions show **pinyin**, as stated in the official syllabus (*"试卷上的试题都有拼音"*).
Each part opens with a **worked example** (例如), identical to the official paper.

---

## Features

### Faithful exam reproduction
- One full part (5 questions) per screen, navigated with Prev / Next.
- Matching parts (L3, R2, R3, R4) show a **shared A–F bank** at the top of the screen; students
  pick the matching letter for each item — exactly as in the official printed paper.
- Answer selection is in-place (no page reload), so the scroll position never jumps.

### Randomised question generation
Questions are generated fresh every run from curated banks:

| Bank | Items | Used in |
|---|---|---|
| `sentences.json` | 123 natural HSK1 sentences | L2, R2 |
| `dialogues.json` | 64 Q&A dialogue pairs | L3, R3 |
| `grammar.json` | 64 fill-in-the-blank items | R4 |
| `vocab_hsk1.json` | 295 HSK1 words | L1, R1, L4, distractors |

All content uses **only official HSK1 vocabulary** (150-word syllabus). The difficulty of
generated sentences, dialogues and fill-in-the-blank items has been compared statistically
against the real exam papers and is at the same level.

### Text-to-speech
- **Online (high quality)**: `edge-tts` with the Microsoft Xiaoxiao Neural voice (`zh-CN-XiaoxiaoNeural`).
- **Offline fallback**: `pyttsx3` with a Windows SAPI Chinese voice (if installed).
- **Adaptive speed**: speech rate slows down for longer sentences so each word is easier to
  follow (−10 % for ≤ 4 chars, up to −38 % for > 10 chars).
- All audio is **cached on disk** by content hash so it is only synthesised once.
- A silent warm-up clip is played at exam start to prevent the first word from being clipped.

### Images
- **32 curated scene photos** (`assets/scenes/`) hand-matched to specific sentences.
- **70+ CC-licensed photos** (`assets/words/`) sourced from [Openverse](https://openverse.org),
  covering all 53 picturable HSK1 concepts.
- Every concept has **at least 2 different photos**, so repeated runs show different images.
- Inside a question, all options are always photos (never a mix of photos and emoji), so the
  image type cannot reveal the answer.
- Attribution for CC photos is stored in `data/image_credits.json`.

### Scoring and history
- Score calculation follows the official linear model: each correct answer = 5 points per section.
- Every attempt is saved in a local **SQLite database** with:
  - Date and time
  - Listening / Reading / Total scores
  - Per-part breakdown (correct / total for each of the 8 parts)
  - Duration in seconds
  - UI language used
- The **History screen** shows a scrollable table (with duration column) and a line chart of
  total scores over time, with a dashed pass-line at 120.
- Individual results can be **deleted** from both the Results screen and the History screen;
  a **Clear all** button wipes the entire history (with confirmation).

### User interface
- **Bilingual** Italian / English: toggle on the fly with the EN / IT button in the header.
- **Per-section countdown timer**: strict mode auto-advances when time runs out; relaxed mode
  lets you take as long as you want.
- **Answer review**: after the exam, expand a scrollable list showing every question with the
  correct answer, your answer, pinyin, Italian / English translation, and a Replay button for
  Listening questions.
- **Settings screen**: strict timer on/off · show/hide pinyin · voice test button ·
  show/hide worked examples (例如).

---

## Requirements

| Dependency | Purpose |
|---|---|
| Python 3.10+ (tested on 3.14) | runtime |
| `edge-tts` | online neural TTS |
| `pyttsx3` | offline TTS fallback |
| `pypinyin` | pinyin generation |
| `Pillow` | photo loading, emoji rasterisation |
| `tkinter` | GUI (included in Python on Windows) |
| `sqlite3` | history (included in Python) |

No `pygame` or other heavy dependencies. Audio playback uses the **Windows MCI API** via
`ctypes`, which supports MP3 and WAV natively.

---

## Installation

```powershell
# 1. Clone the repository
git clone https://github.com/sedoglia/hsk1-simulator.git
cd hsk1-simulator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python run.py
```

---

## Running the app

```powershell
python run.py
```

The app opens on the **Home screen**. Press **Start test** to begin. The Listening section
loads and pre-synthesises audio (with a progress bar); the Reading section starts immediately.

At the end press **Finish & grade** to see your score. From the Results screen you can:
- Expand **Review answers** to read every Q&A with audio replay.
- Press **Start test** again for a new randomised exam.
- Navigate to **History & progress** to see all past results.

---

## Running the tests

```powershell
python -m unittest discover -s tests -v
```

31 tests across three files:

| File | Tests | What is verified |
|---|---|---|
| `test_exam_structure.py` | 19 | 40 questions, 4×5 per section, correct types per part, timings, scoring, A–F bank sharing, official-150 conformity, randomness |
| `test_images.py` | 9 | ≥ 50 image concepts, all files exist on disk, no photo/emoji mix in one question, distinct images per question, variety across 40 exams |
| `test_audio.py` | 3 | sequence playback, stop cancels remaining clips, second clip never starts before first finishes |

---

## Project layout

```
hsk1-simulator/
│
├── run.py                      # entry point — python run.py
├── requirements.txt
├── README.md                   # this file (English)
├── README.it.md                # Italian version
│
├── hsk1sim/                    # main package
│   ├── config.py               # all paths, exam constants, feature flags
│   ├── i18n.py                 # all UI strings in IT and EN; Translator class
│   ├── tts.py                  # HybridTTS: edge-tts + pyttsx3, disk cache, adaptive speed
│   ├── audio.py                # AudioPlayer via Windows MCI (play, play_sequence, stop, warmup)
│   ├── emoji_render.py         # visual_to_image(): photo or emoji → Tkinter PhotoImage
│   ├── visual_catalog.py       # maps sentences/words → image paths; loads word_images.json
│   ├── exam.py                 # Exam model: generate(), score(), details(), duration_seconds()
│   ├── question_gen.py         # 8 generators (one per part) + sentence/dialogue templates
│   ├── db.py                   # SQLite: save_attempt(), get_attempts(), delete_attempt(), clear()
│   │
│   ├── assets/
│   │   ├── scenes/             # s01.jpg … s32.jpg — curated exam scene photos
│   │   └── words/              # CC-licensed concept photos (apple_1.jpg, doctor_1.jpg, …)
│   │
│   ├── data/
│   │   ├── vocab_hsk1.json     # 295 words: hanzi, pinyin, it, en, emoji, category, hsk1_official
│   │   ├── official_150.json   # list of the 150 official HSK1 hanzi
│   │   ├── sentences.json      # 123 sentences: zh, it, en, key (image concept)
│   │   ├── dialogues.json      # 64 dialogues: q, a, q_it/en, a_it/en, key
│   │   ├── grammar.json        # 64 fill-in items: q, a, d (distractors), pt_it, pt_en, it, en
│   │   ├── word_images.json    # { hanzi: ["words/file.jpg", …] } — CC photo index
│   │   └── image_credits.json  # { "words/file.jpg": { creator, license, source } }
│   │
│   └── ui/
│       ├── app.py              # App class: root window, screen router, language toggle
│       ├── welcome.py          # Home screen
│       ├── exam_view.py        # Exam screen: part-by-part, A–F bank, audio controls
│       ├── results.py          # Results screen: scores, answer review, delete button
│       ├── history.py          # History screen: table + chart + delete/clear buttons
│       ├── settings_view.py    # Settings screen
│       └── widgets.py          # shared colour theme, f() font helper, button() helper
│
├── tests/
│   ├── test_exam_structure.py
│   ├── test_images.py
│   └── test_audio.py
│
└── userdata/                   # created at first run (git-ignored)
    ├── history.db              # SQLite attempt history
    └── audio_cache/            # synthesised MP3/WAV files, keyed by content hash
```

---

## Data files

### `vocab_hsk1.json`
Array of word objects. Each entry:
```json
{
  "hanzi": "学校",
  "pinyin": "xuéxiào",
  "it": "scuola",
  "en": "school",
  "emoji": "🏫",
  "category": "place",
  "hsk1_official": true
}
```
`hsk1_official: true` means the word is in the official 150-word syllabus.
Set `OFFICIAL_150_ONLY = False` in `config.py` to use the full ~295-word set.

### `sentences.json`
Natural HSK1 sentences linked to a picturable concept (`key`):
```json
{ "zh": "他在学校工作。", "it": "Lavora a scuola.", "en": "He works at school.", "key": "学校" }
```

### `dialogues.json`
Q&A pairs, some linked to a concept (`key`) for use in Listening Part 3:
```json
{ "q": "你去哪儿？", "a": "我去学校。", "q_it": "Dove vai?", "q_en": "Where are you going?",
  "a_it": "Vado a scuola.", "a_en": "I'm going to school.", "key": "学校" }
```

### `grammar.json`
Fill-in-the-blank items. `a` is the correct word; `d` is a list of two plausible distractors:
```json
{ "q": "他 （ ____ ） 学校。", "a": "在", "d": ["是", "有"],
  "pt_it": "在 per il luogo", "pt_en": "在 for location",
  "it": "Lui è a scuola.", "en": "He is at school." }
```

---

## Extending the app

### Regenerate vocabulary
```powershell
python build_vocab.py
```
Reads the word list in `build_vocab.py`, computes pinyin with `pypinyin`, and writes
`hsk1sim/data/vocab_hsk1.json`. Edit the `WORDS` list to add or change entries.

### Download more CC images
```powershell
python fetch_images.py   # fetch 2 images per concept (initial run)
python fetch_more.py     # top up concepts that have fewer than 2 images
```
Both scripts query the [Openverse](https://openverse.org) API (no key required) and save
images to `hsk1sim/assets/words/`. Credits are written to `data/image_credits.json`.

### Validate HSK1 conformity
```powershell
python validate_banks.py
```
Tokenises every sentence and dialogue with a max-match segmenter and reports any Chinese
words that are not in the official 150 (or the explicitly whitelisted morphemes).

---

## Technical notes

- **Audio anti-clipping**: a 350 ms silent WAV is played once at exam start (`player.warmup()`)
  to initialise the Windows audio device, preventing the first syllable from being cut off.
  Each clip also uses MCI `cue output` + `seek to start` before playback.
- **Thread safety**: the loading bar is updated via a `queue.Queue` polled on the main thread
  (every 80 ms), not via `after()` calls from the worker thread.
- **Scroll persistence**: clicking an answer calls a lightweight `_refresh()` closure that
  recolours only the affected widgets in-place, so the scroll position never jumps.
- **Image deduplication**: the `_distinct_image_items()` generator guarantees that all options
  within a matching-bank question map to different image files, even when two concepts share
  the same curated scene.
- **Grammar pool balance**: Reading Part 4 selects ~3 "rich" items (content words or compound
  sentences) and ~2 "base" items (grammar words / short sentences) per exam, matching the
  composition of the official word bank.

---

## License

**Code**: MIT — see [LICENSE](LICENSE).

**Photos in `assets/words/`**: CC0 or CC-BY, per `data/image_credits.json`.

**Photos in `assets/scenes/`**: curated for this project; free to use for personal study.

**Official Hanban exam papers** (H10901–H11005, not included in this repository):
© Hanban / Center for Language Education and Cooperation. Download separately from
[chinesetest.cn](https://www.chinesetest.cn) or authorised distributors.
