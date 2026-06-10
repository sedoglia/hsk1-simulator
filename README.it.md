# Simulatore d'esame HSK1

> **English version → [README.md](README.md)**

Un'applicazione desktop **Python / Tkinter** che replica fedelmente l'esame ufficiale di
certificazione cinese **HSK di livello 1**, basata sul 考试大纲 (syllabus ufficiale) e sul
样卷 (prova campione) del Centro per l'Educazione e la Cooperazione Linguistica
(CLEC / 教育部中外语言交流合作中心), verificata contro gli esami reali H10901–H11005.

Ogni esecuzione genera un test da 40 domande **completamente diverso**. L'app gira interamente
su Windows, funziona offline (con TTS degradato) e non richiede account né abbonamenti.

---

## Indice

1. [Struttura dell'esame](#struttura-dellesame)
2. [Funzionalità](#funzionalità)
3. [Requisiti](#requisiti)
4. [Installazione](#installazione)
5. [Avvio dell'applicazione](#avvio-dellapplicazione)
6. [Esecuzione dei test automatici](#esecuzione-dei-test-automatici)
7. [Struttura del progetto](#struttura-del-progetto)
8. [File di dati](#file-di-dati)
9. [Estendere l'applicazione](#estendere-lapplicazione)
10. [Note tecniche](#note-tecniche)
11. [Licenza](#licenza)

---

## Struttura dell'esame

L'esame HSK1 ha due sezioni e 40 domande totali, ciascuna del valore di 5 punti.

| | Ascolto 听力 (~15 min) | Lettura 阅读 (17 min) |
|---|---|---|
| **Parte 1** | Frase breve → immagine **Vero / Falso** | Parola + immagine **Vero / Falso** |
| **Parte 2** | Frase → scegli **1 tra 3** immagini (A/B/C) | Frase → scegli **1 tra 6** immagini (A–F) |
| **Parte 3** | Dialogo → scegli **1 tra 6** immagini (A–F) | Domanda → abbina **1 di 6** risposte (A–F) |
| **Parte 4** | Enunciato + domanda → scegli **1 di 3** risposte | Completa il buco (banco di **6** parole) |

**Tempi**: ~15 min Ascolto · +3 min per la scheda risposte · 17 min Lettura ·
~40 min totali (inclusi 5 min per i dati personali).

**Punteggio**: Ascolto / 100 + Lettura / 100 = **/ 200** · **Sufficienza ≥ 120 / 200**.

Ogni quesito di Ascolto viene **riprodotto due volte**, come nell'esame reale.
Tutte le domande mostrano il **pinyin**, come stabilito dal syllabus ufficiale
(*"试卷上的试题都有拼音"*). Ogni parte si apre con un **esempio svolto** (例如),
identico al foglio ufficiale.

---

## Funzionalità

### Riproduzione fedele dell'esame
- Una parte intera (5 quesiti) per schermata, navigabile con Avanti / Indietro.
- Le parti ad abbinamento (A3, L2, L3, L4) mostrano un **banco A–F condiviso** in cima alla
  schermata; il candidato sceglie la lettera corrispondente per ciascun quesito — esattamente
  come nel foglio ufficiale a stampa.
- La selezione della risposta avviene sul posto (senza ricaricare la pagina), quindi la
  posizione di scroll non salta mai.

### Generazione randomica delle domande
Le domande vengono generate nuove a ogni esecuzione a partire da banche curate:

| Banca | Elementi | Usata in |
|---|---|---|
| `sentences.json` | 123 frasi naturali HSK1 | A2, L2 |
| `dialogues.json` | 64 coppie dialogo Q&R | A3, L3 |
| `grammar.json` | 64 esercizi di completamento | L4 |
| `vocab_hsk1.json` | 295 parole HSK1 | A1, L1, A4, distrattori |

Tutti i contenuti usano **solo vocabolario ufficiale HSK1** (syllabus da 150 parole).
La difficoltà delle frasi, dei dialoghi e dei completamenti è stata confrontata
statisticamente con gli esami reali e risulta allo stesso livello.

### Sintesi vocale
- **Online (alta qualità)**: `edge-tts` con la voce Microsoft Xiaoxiao Neural (`zh-CN-XiaoxiaoNeural`).
- **Fallback offline**: `pyttsx3` con voce cinese Windows SAPI (se installata).
- **Velocità adattiva**: la velocità di lettura rallenta per le frasi più lunghe, in modo che
  ogni parola sia più facile da seguire (−10 % per ≤ 4 caratteri, fino a −38 % per > 10 caratteri).
- Tutto l'audio viene **conservato su disco** per hash del contenuto, così viene sintetizzato
  una sola volta.
- All'avvio dell'esame viene riprodotta una clip silenziosa di riscaldamento per evitare che
  la prima sillaba venga tagliata dal driver audio di Windows.

### Immagini
- **32 scene curate** (`assets/scenes/`) abbinate manualmente a frasi specifiche.
- **70+ foto con licenza CC** (`assets/words/`) provenienti da [Openverse](https://openverse.org),
  che coprono tutti i 53 concetti illustrabili dell'HSK1.
- Ogni concetto ha **almeno 2 foto diverse**, quindi test ripetuti mostrano immagini diverse.
- In una domanda, tutte le opzioni sono sempre foto (mai un mix di foto ed emoji), così il
  tipo di immagine non può rivelare la risposta.
- I crediti delle foto CC sono salvati in `data/image_credits.json`.

### Punteggio e storico
- Il calcolo del punteggio segue il modello lineare ufficiale: ogni risposta corretta = 5 punti per sezione.
- Ogni tentativo viene salvato in un **database SQLite** locale con:
  - Data e ora
  - Punteggi Ascolto / Lettura / Totale
  - Dettaglio per-parte (corrette / totali per ciascuna delle 8 parti)
  - Durata in secondi
  - Lingua dell'interfaccia usata
- La **schermata Storico** mostra una tabella scorrevole (con colonna Durata) e un grafico
  a linee del punteggio totale nel tempo, con linea tratteggiata di sufficienza a 120.
- I risultati possono essere **eliminati** singolarmente dalla schermata Risultati e dalla
  schermata Storico; un pulsante **Azzera tutto** cancella l'intero storico (con conferma).

### Interfaccia utente
- **Bilingue** Italiano / Inglese: commutabile al volo con il pulsante IT / EN nell'header.
- **Timer a conto alla rovescia per sezione**: modalità rigida che avanza automaticamente allo
  scadere del tempo; modalità rilassata senza limite.
- **Revisione delle risposte**: dopo l'esame, un elenco scorrevole mostra ogni domanda con
  la risposta corretta, la tua risposta, il pinyin, la traduzione italiano/inglese e un pulsante
  Riascolta per le domande di Ascolto.
- **Schermata Impostazioni**: timer rigido sì/no · mostra/nascondi pinyin · prova della voce ·
  mostra/nascondi esempi svolti (例如).

---

## Requisiti

| Dipendenza | Scopo |
|---|---|
| Python 3.10+ (testato su 3.14) | runtime |
| `edge-tts` | TTS neurale online |
| `pyttsx3` | TTS offline di fallback |
| `pypinyin` | generazione del pinyin |
| `Pillow` | caricamento foto, rasterizzazione emoji |
| `tkinter` | GUI (incluso in Python su Windows) |
| `sqlite3` | storico (incluso in Python) |

Nessuna dipendenza pesante come `pygame`. La riproduzione audio usa l'**API MCI di Windows**
tramite `ctypes`, che supporta nativamente MP3 e WAV.

---

## Installazione

```powershell
# 1. Clona il repository
git clone https://github.com/sedoglia/hsk1-simulator.git
cd hsk1-simulator

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Avvia
python run.py
```

---

## Avvio dell'applicazione

```powershell
python run.py
```

L'app si apre sulla **schermata Home**. Premi **Inizia il test** per cominciare. La sezione
Ascolto carica e pre-sintetizza l'audio (con barra di avanzamento); la sezione Lettura parte
immediatamente.

Alla fine premi **Termina e correggi** per vedere il punteggio. Dalla schermata Risultati puoi:
- Espandere **Rivedi le risposte** per leggere ogni Q&R con riascolto audio.
- Premere **Inizia il test** per un nuovo esame randomico.
- Andare a **Storico e progressi** per vedere tutti i risultati passati.

---

## Esecuzione dei test automatici

```powershell
python -m unittest discover -s tests -v
```

31 test in tre file:

| File | Test | Cosa viene verificato |
|---|---|---|
| `test_exam_structure.py` | 19 | 40 domande, 4×5 per sezione, tipi per parte, tempi, punteggio, condivisione banco A–F, conformità alle 150 ufficiali, casualità |
| `test_images.py` | 9 | ≥ 50 concetti illustrati, tutti i file esistono su disco, nessun mix foto/emoji in una domanda, immagini distinte per domanda, varietà su 40 esami |
| `test_audio.py` | 3 | riproduzione sequenziale, stop annulla le clip rimanenti, la seconda clip non parte prima che finisca la prima |

---

## Struttura del progetto

```
hsk1-simulator/
│
├── run.py                      # punto di avvio — python run.py
├── requirements.txt
├── README.md                   # versione inglese
├── README.it.md                # questo file (italiano)
│
├── hsk1sim/                    # pacchetto principale
│   ├── config.py               # tutti i percorsi, costanti d'esame, flag di configurazione
│   ├── i18n.py                 # tutte le stringhe UI in IT e EN; classe Translator
│   ├── tts.py                  # HybridTTS: edge-tts + pyttsx3, cache su disco, velocità adattiva
│   ├── audio.py                # AudioPlayer via Windows MCI (play, play_sequence, stop, warmup)
│   ├── emoji_render.py         # visual_to_image(): foto o emoji → Tkinter PhotoImage
│   ├── visual_catalog.py       # mappa frasi/parole → percorsi immagini; carica word_images.json
│   ├── exam.py                 # modello Exam: generate(), score(), details(), duration_seconds()
│   ├── question_gen.py         # 8 generatori (uno per parte) + template frasi/dialoghi
│   ├── db.py                   # SQLite: save_attempt(), get_attempts(), delete_attempt(), clear()
│   │
│   ├── assets/
│   │   ├── scenes/             # s01.jpg … s32.jpg — scene curate per l'esame
│   │   └── words/              # foto CC per concetti (apple_1.jpg, doctor_1.jpg, …)
│   │
│   ├── data/
│   │   ├── vocab_hsk1.json     # 295 parole: hanzi, pinyin, it, en, emoji, category, hsk1_official
│   │   ├── official_150.json   # lista dei 150 hanzi del syllabus ufficiale HSK1
│   │   ├── sentences.json      # 123 frasi: zh, it, en, key (concetto-immagine)
│   │   ├── dialogues.json      # 64 dialoghi: q, a, q_it/en, a_it/en, key
│   │   ├── grammar.json        # 64 item completamento: q, a, d (distrattori), pt_it, pt_en, it, en
│   │   ├── word_images.json    # { hanzi: ["words/file.jpg", …] } — indice foto CC
│   │   └── image_credits.json  # { "words/file.jpg": { creator, license, source } }
│   │
│   └── ui/
│       ├── app.py              # classe App: finestra root, router schermate, toggle lingua
│       ├── welcome.py          # schermata Home
│       ├── exam_view.py        # schermata Esame: per-parte, banco A–F, controlli audio
│       ├── results.py          # schermata Risultati: punteggi, revisione risposte, pulsante elimina
│       ├── history.py          # schermata Storico: tabella + grafico + pulsanti elimina/azzera
│       ├── settings_view.py    # schermata Impostazioni
│       └── widgets.py          # tema colori condiviso, helper f() per font, helper button()
│
├── tests/
│   ├── test_exam_structure.py
│   ├── test_images.py
│   └── test_audio.py
│
└── userdata/                   # creata al primo avvio (esclusa da git)
    ├── history.db              # storico dei tentativi in SQLite
    └── audio_cache/            # file MP3/WAV sintetizzati, indicizzati per hash del contenuto
```

---

## File di dati

### `vocab_hsk1.json`
Array di oggetti-parola. Ogni elemento:
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
`hsk1_official: true` indica che la parola è nel syllabus ufficiale da 150 parole.
Imposta `OFFICIAL_150_ONLY = False` in `config.py` per usare il set esteso da ~295 voci.

### `sentences.json`
Frasi naturali HSK1 collegate a un concetto illustrabile (`key`):
```json
{ "zh": "他在学校工作。", "it": "Lavora a scuola.", "en": "He works at school.", "key": "学校" }
```

### `dialogues.json`
Coppie Q&R, alcune collegate a un concetto (`key`) per l'uso nell'Ascolto Parte 3:
```json
{ "q": "你去哪儿？", "a": "我去学校。", "q_it": "Dove vai?", "q_en": "Where are you going?",
  "a_it": "Vado a scuola.", "a_en": "I'm going to school.", "key": "学校" }
```

### `grammar.json`
Item di completamento. `a` è la parola corretta; `d` è una lista di due distrattori plausibili:
```json
{ "q": "他 （ ____ ） 学校。", "a": "在", "d": ["是", "有"],
  "pt_it": "在 per il luogo", "pt_en": "在 for location",
  "it": "Lui è a scuola.", "en": "He is at school." }
```

---

## Estendere l'applicazione

### Rigenerare il vocabolario
```powershell
python build_vocab.py
```
Legge la lista di parole in `build_vocab.py`, calcola il pinyin con `pypinyin` e scrive
`hsk1sim/data/vocab_hsk1.json`. Modifica la lista `WORDS` per aggiungere o cambiare voci.

### Scaricare altre foto CC
```powershell
python fetch_images.py   # scarica 2 foto per concetto (prima esecuzione)
python fetch_more.py     # integra i concetti che hanno meno di 2 foto
```
Entrambi gli script interrogano le API di [Openverse](https://openverse.org) (nessuna chiave
richiesta) e salvano le foto in `hsk1sim/assets/words/`. I crediti vengono scritti in
`data/image_credits.json`.

### Verificare la conformità all'HSK1
```powershell
python validate_banks.py
```
Tokenizza ogni frase e dialogo con un segmentatore max-match e segnala qualsiasi parola
cinese che non è nelle 150 ufficiali (o nei morfemi esplicitamente ammessi).

---

## Note tecniche

- **Anti-troncamento audio**: una WAV silenziosa da 350 ms viene riprodotta una volta
  all'avvio dell'esame (`player.warmup()`) per inizializzare il dispositivo audio di Windows,
  evitando che la prima sillaba venga tagliata. Ogni clip usa anche MCI `cue output` +
  `seek to start` prima della riproduzione.
- **Thread safety**: la barra di caricamento viene aggiornata tramite una `queue.Queue`
  interrogata sul thread principale (ogni 80 ms), non tramite chiamate `after()` dal thread
  worker.
- **Persistenza dello scroll**: fare clic su una risposta chiama una closure leggera
  `_refresh()` che ricolora solo i widget coinvolti sul posto, quindi la posizione di scroll
  non salta mai.
- **Deduplicazione delle immagini**: il generatore `_distinct_image_items()` garantisce che
  tutte le opzioni in una domanda ad abbinamento puntino a file di immagini diversi, anche
  quando due concetti condividono la stessa scena curata.
- **Bilanciamento del banco R4**: la Lettura Parte 4 seleziona ~3 item "ricchi" (parole di
  contenuto o frasi composte) e ~2 item "base" (parole grammaticali / frasi brevi) per esame,
  corrispondendo alla composizione del banco parole degli esami ufficiali.

---

## Licenza

**Codice**: MIT — vedi [LICENSE](LICENSE).

**Foto in `assets/words/`**: CC0 o CC-BY, vedi `data/image_credits.json` per le attribuzioni.

**Foto in `assets/scenes/`**: curate per questo progetto; libere per uso didattico personale.

**Esami ufficiali Hanban** (H10901–H11005, non inclusi in questo repository):
© Hanban / Center for Language Education and Cooperation. Scaricabili separatamente da
[chinesetest.cn](https://www.chinesetest.cn) o da distributori autorizzati.
