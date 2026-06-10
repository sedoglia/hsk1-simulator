# Simulatore Esame HSK1 · HSK1 Exam Simulator

Applicazione desktop in Python con interfaccia grafica **bilingue (Italiano / Inglese)**
che simula in modo fedele l'esame di certificazione di cinese **HSK livello 1**: due sezioni
(Ascolto + Lettura), 40 domande generate in modo **casuale** ad ogni esecuzione, sintesi
vocale del cinese, valutazione finale in stile esame reale e **storico** dei progressi.

*A bilingual (Italian/English) Python desktop app that faithfully simulates the official
**HSK Level 1** Chinese exam: Listening + Reading, 40 randomly generated questions each run,
Chinese text-to-speech, real exam-style scoring, and a progress history.*

---

## 🇮🇹 Italiano

### Caratteristiche
- **Struttura fedele all'esame ufficiale** (verificata sul **syllabus ufficiale 考试大纲 一级**,
  sul **样卷** del 教育部中外语言交流合作中心 e sul foglio **H10901**):
  40 domande (20 Ascolto + 20 Lettura), 4 parti per sezione. Tutte le domande riportano il **pinyin**,
  come nell'esame reale.
  - *Ascolto*: 1) frase+immagine Vero/Falso · 2) scelta tra 3 immagini (A/B/C) ·
    3) **abbinamento** dialogo→immagine (banco di 6, A-F) · 4) enunciato+domanda→risposta.
    L'audio si riproduce **due volte**, come nell'esame.
  - *Lettura*: 1) parola+immagine Vero/Falso · 2) **abbinamento** frase→immagine (banco di 6) ·
    3) **abbinamento** domanda→risposta (banco di 6) · 4) **abbinamento** completamento (banco di 6 parole).
- **Punteggio reale**: Ascolto /100 + Lettura /100 = /200. **Sufficienza 120/200**.
- **Domande casuali**: ogni test è diverso, con distrattori coerenti pescati dal vocabolario.
- **Sintesi vocale ibrida**: voce online di alta qualità (`edge-tts`, Microsoft Neural zh-CN)
  con **fallback offline** automatico (`pyttsx3` / voci di Windows) se manca la connessione.
- **Immagini d'esame chiare e varie**: scene fotografiche curate + foto con licenza **CC**
  (scaricate da Openverse, vedi `data/image_credits.json`), **più immagini per concetto** scelte
  a caso → ripetendo il test compaiono figure diverse. Dentro una domanda le opzioni sono sempre
  tutte foto (mai mix foto/emoji). Fallback emoji solo per concetti astratti.
- **Domande sempre diverse**: frasi e mini-dialoghi delle parti illustrate sono generati da
  modelli sui concetti delle 150 parole → varietà altissima (≈180 frasi/dialoghi distinti su
  40 esami) mantenendo solo vocabolario ufficiale.
- **Svolgimento come l'esame reale**: una **parte intera per schermata** (5 quesiti); le parti ad
  abbinamento (Ascolto P3, Lettura P2/P3/P4) mostrano un **unico banco di 6 opzioni A–F** a cui
  abbinare i 5 quesiti, esattamente come nel foglio ufficiale.
- **Storico e progressi**: ogni tentativo è salvato in SQLite con **data/ora e dettaglio per-parte**;
  tabella (con durata), grafico con soglia 120, e pulsanti per **eliminare un singolo esito** o
  **azzerare tutto** (anche "elimina questo risultato" nella pagina dei risultati).
- **Interfaccia IT/EN** commutabile al volo, **timer per sezione** (15 min Ascolto, 17 min Lettura, +3 min foglio risposte),
  **revisione delle risposte** con caratteri, pinyin, traduzione e riascolto dell'audio.
- **Impostazioni**: timer rigido on/off, mostra/nascondi pinyin, prova della voce.

### Requisiti
- Windows (testato su Windows 11, Python 3.14).
- Connessione internet **consigliata** per la voce di alta qualità (non obbligatoria).

### Installazione ed avvio
```powershell
pip install -r requirements.txt
python run.py
```

Il vocabolario è già generato in `hsk1sim/data/vocab_hsk1.json`. Per rigenerarlo:
```powershell
python build_vocab.py
```

### Test automatici
La suite verifica che gli esami generati rispettino la struttura **ufficiale** HSK1
(riferimento: syllabus 考试大纲 一级 + 样卷, [chinesetest.cn](https://www.chinesetest.cn/HSK/1)):
40 quesiti, 4+4 parti da 5, punteggio 100/100/200, soglia 120, tempi (15 / +3 / 17 min),
tipologie per parte, banco di 6 nelle parti ad abbinamento, **uso delle sole 150 parole
ufficiali**, casualità e copertura grammaticale.
```powershell
python -m unittest discover -s tests -v
```

### Materiali ufficiali di riferimento
Nella cartella `official_exams/` sono presenti i 5 esami ufficiali HSK1 (H10901, H10902,
H11003, H11004, H11005) in **PDF + MP3 + soluzioni**, usati per allineare struttura, tempi e
tipologie di domanda all'esame reale Hanban/Istituto Confucio.

### Nota sul vocabolario
Per default il test usa **solo le 150 parole del syllabus ufficiale HSK1** (file
`hsk1sim/data/official_150.json`), come da esame reale. Il dataset completo contiene ~295 voci
(le 150 ufficiali + aggiunte comuni HSK 3.0); impostando `OFFICIAL_150_ONLY = False` in
`hsk1sim/config.py` si usa il set esteso. Le immagini si possono ampliare con `python fetch_images.py`
(scarica foto CC) e si può verificare il rispetto delle 150 con `python validate_banks.py`.
Tutte le voci hanno pinyin, traduzione IT/EN ed emoji
dove ha senso.

### Esempi 例如
Come nel foglio d'esame ufficiale, all'inizio di ogni parte viene mostrato un **esempio svolto**
(例如) già risolto. Si può disattivare dalle Impostazioni.

---

## 🇬🇧 English

### Features
- **Faithful exam structure**: 40 questions (20 Listening + 20 Reading), 4 parts each section.
  - *Listening*: 1) sentence+picture True/False · 2) sentence→picture · 3) dialogue→picture ·
    4) statement+question→answer. Audio can be played **twice**, like the real exam.
  - *Reading*: 1) picture+word True/False · 2) sentence→picture · 3) match question/answer ·
    4) fill in the missing word.
- **Real scoring**: Listening /100 + Reading /100 = /200. **Pass mark 120/200**.
- **Randomized questions**: every test differs, with coherent distractors from the vocabulary.
- **Hybrid TTS**: high-quality online voice (`edge-tts`, Microsoft Neural zh-CN) with automatic
  **offline fallback** (`pyttsx3` / Windows voices) when offline.
- **Clear exam pictures**: purpose-made photographic scenes tied to the full sentence; emoji
  fallback only for abstract concepts or extended-vocabulary entries not yet illustrated.
- **History & progress**: every attempt saved to a local SQLite database, with a table and a
  score-trend chart (pass-line at 120).
- **Switchable IT/EN UI**, **per-section timer** (15 min Listening, 17 min Reading, +3 min answer sheet),
  **answer review** with characters, pinyin, translation and audio replay.
- **Settings**: strict timer on/off, show/hide pinyin, voice test.

### Requirements & run
```powershell
pip install -r requirements.txt
python run.py
```

---

## Struttura del progetto / Project layout
```
run.py                 # avvio / launcher
build_vocab.py         # generatore del vocabolario / vocabulary builder
test_gui.py            # smoke test della GUI / GUI smoke test
requirements.txt
hsk1sim/
  config.py            # costanti e percorsi / constants & paths
  i18n.py              # stringhe IT/EN / bilingual strings
  tts.py               # TTS ibrido / hybrid TTS
  audio.py             # riproduzione audio (Windows MCI) / audio playback
  emoji_render.py      # scene/emoji -> immagini Tk / scene/emoji to Tk images
  visual_catalog.py    # collegamento frasi/parole -> scene / visual scene catalog
  assets/scenes/       # immagini locali generate per l'esame / generated local exam pictures
  db.py                # storico SQLite / SQLite history
  question_gen.py      # generatori delle 8 parti / question generators
  exam.py              # modello d'esame e punteggio / exam model & scoring
  data/                # vocab_hsk1.json, sentences.json, dialogues.json
  ui/                  # schermate Tkinter / Tkinter screens
userdata/              # generata a runtime: history.db + cache audio
```

I dati utente (database e cache audio) vengono creati automaticamente in `userdata/`.
