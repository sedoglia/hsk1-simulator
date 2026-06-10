# -*- coding: utf-8 -*-
"""Internazionalizzazione IT/EN / bilingual UI strings."""

STRINGS = {
    # Generali / home
    "app_title":      {"it": "Simulatore d'esame HSK1", "en": "HSK1 Exam Simulator"},
    "subtitle":       {"it": "Prova ufficiale di cinese — Livello 1", "en": "Official Chinese test — Level 1"},
    "start_test":     {"it": "▶  Inizia il test", "en": "▶  Start test"},
    "history_btn":    {"it": "📊  Storico e progressi", "en": "📊  History & progress"},
    "settings_btn":   {"it": "⚙  Impostazioni", "en": "⚙  Settings"},
    "quit":           {"it": "Esci", "en": "Quit"},
    "language":       {"it": "Lingua", "en": "Language"},
    "back_home":      {"it": "← Home", "en": "← Home"},
    "info_line":      {"it": "40 domande · ~40 min · Ascolto + Lettura · Sufficienza 120/200",
                       "en": "40 questions · ~40 min · Listening + Reading · Pass 120/200"},

    # Impostazioni
    "settings_title": {"it": "Impostazioni", "en": "Settings"},
    "strict_timer":   {"it": "Timer rigido (avanza allo scadere del tempo)",
                       "en": "Strict timer (advance when time runs out)"},
    "show_pinyin":    {"it": "Mostra il pinyin durante la revisione",
                       "en": "Show pinyin during review"},
    "show_examples":  {"it": "Mostra l'esempio svolto (例如) a inizio parte",
                       "en": "Show the worked example (例如) at the start of each part"},
    "voice_test":     {"it": "Prova la voce", "en": "Test the voice"},
    "save":           {"it": "Salva", "en": "Save"},

    # Sezioni
    "section_listening": {"it": "Ascolto (听力)", "en": "Listening (听力)"},
    "section_reading":   {"it": "Lettura (阅读)", "en": "Reading (阅读)"},
    "part":           {"it": "Parte", "en": "Part"},
    "question":       {"it": "Domanda", "en": "Question"},
    "of":             {"it": "di", "en": "of"},

    # Audio / navigazione
    "play_audio":     {"it": "🔊  Ascolta", "en": "🔊  Play audio"},
    "play_again":     {"it": "🔁  Riascolta", "en": "🔁  Play again"},
    "plays_left":     {"it": "Riproduzioni rimaste: {n}", "en": "Plays left: {n}"},
    "next":           {"it": "Avanti →", "en": "Next →"},
    "previous":       {"it": "← Indietro", "en": "← Back"},
    "next_section":   {"it": "Vai alla Lettura →", "en": "Go to Reading →"},
    "finish_exam":    {"it": "Termina e correggi", "en": "Finish & grade"},
    "time_left":      {"it": "Tempo: {t}", "en": "Time: {t}"},

    # Tipi di domanda (consegne)
    "instr_L1": {"it": "Ascolta. La frase corrisponde all'immagine? Scegli ✓ (Vero) o ✗ (Falso).",
                 "en": "Listen. Does the audio match the picture? Choose ✓ (True) or ✗ (False)."},
    "instr_L2": {"it": "Ascolta la frase e scegli l'immagine corrispondente.",
                 "en": "Listen to the sentence and choose the matching picture."},
    "instr_L3": {"it": "Ascolta il dialogo e scegli l'immagine giusta tra le 6 del banco (A-F).",
                 "en": "Listen to the dialogue and choose the right picture from the 6 (A-F)."},
    "instr_L4": {"it": "Ascolta e rispondi alla domanda scegliendo l'opzione giusta.",
                 "en": "Listen and answer the question by choosing the right option."},
    "instr_R1": {"it": "L'immagine corrisponde alla parola? Scegli ✓ (Vero) o ✗ (Falso).",
                 "en": "Does the picture match the word? Choose ✓ (True) or ✗ (False)."},
    "instr_R2": {"it": "Leggi la frase e scegli l'immagine giusta tra le 6 del banco (A-F).",
                 "en": "Read the sentence and choose the right picture from the 6 (A-F)."},
    "instr_R3": {"it": "Leggi la domanda e scegli la risposta giusta tra le 6 del banco (A-F).",
                 "en": "Read the question and choose the right answer from the 6 (A-F)."},
    "instr_R4": {"it": "Completa la frase scegliendo la parola giusta tra le 6 del banco (A-F).",
                 "en": "Complete the sentence by choosing the right word from the 6 (A-F)."},

    "example_label":  {"it": "Esempio (例如)", "en": "Example (例如)"},
    "true":           {"it": "✓ Vero", "en": "✓ True"},
    "false":          {"it": "✗ Falso", "en": "✗ False"},

    # Risultati
    "results_title":  {"it": "Risultato dell'esame", "en": "Exam result"},
    "listening_score":{"it": "Ascolto", "en": "Listening"},
    "reading_score":  {"it": "Lettura", "en": "Reading"},
    "total_score":    {"it": "Totale", "en": "Total"},
    "passed":         {"it": "PROMOSSO ✓", "en": "PASSED ✓"},
    "failed":         {"it": "NON SUPERATO ✗", "en": "NOT PASSED ✗"},
    "pass_hint":      {"it": "Servono almeno {n}/200 per superare l'esame.",
                       "en": "You need at least {n}/200 to pass."},
    "correct_count":  {"it": "Risposte corrette: {c}/{t}", "en": "Correct answers: {c}/{t}"},
    "review_answers": {"it": "Rivedi le risposte", "en": "Review answers"},
    "hide_review":    {"it": "Nascondi la revisione", "en": "Hide review"},
    "your_answer":    {"it": "Tua risposta", "en": "Your answer"},
    "correct_answer": {"it": "Risposta corretta", "en": "Correct answer"},
    "no_answer":      {"it": "(nessuna risposta)", "en": "(no answer)"},
    "review_correct": {"it": "Corretta", "en": "Correct"},
    "review_wrong":   {"it": "Sbagliata", "en": "Wrong"},

    # Storico
    "history_title":  {"it": "Storico dei tentativi", "en": "Attempt history"},
    "no_history":     {"it": "Nessun test svolto finora. Inizia il tuo primo esame!",
                       "en": "No tests taken yet. Start your first exam!"},
    "col_date":       {"it": "Data", "en": "Date"},
    "col_listening":  {"it": "Ascolto", "en": "Listening"},
    "col_reading":    {"it": "Lettura", "en": "Reading"},
    "col_total":      {"it": "Totale", "en": "Total"},
    "col_result":     {"it": "Esito", "en": "Result"},
    "progress_chart": {"it": "Andamento del punteggio totale", "en": "Total score trend"},
    "col_duration":   {"it": "Durata", "en": "Duration"},
    "delete_result":  {"it": "🗑 Elimina questo risultato", "en": "🗑 Delete this result"},
    "delete_selected":{"it": "🗑 Elimina selezionato", "en": "🗑 Delete selected"},
    "delete_all":     {"it": "Azzera tutto", "en": "Clear all"},
    "confirm_delete": {"it": "Eliminare il risultato selezionato?", "en": "Delete the selected result?"},
    "confirm_delete_all": {"it": "Eliminare TUTTI i risultati? L'operazione è irreversibile.",
                           "en": "Delete ALL results? This cannot be undone."},
    "no_selection":   {"it": "Seleziona prima un risultato dalla tabella.",
                       "en": "Select a result from the table first."},
    "section_detail": {"it": "Dettaglio per parte", "en": "Per-part detail"},
    "attempts_count": {"it": "Tentativi: {n} · Migliore: {best}/200 · Promossi: {p}",
                       "en": "Attempts: {n} · Best: {best}/200 · Passed: {p}"},

    # Dialoghi vari
    "loading_audio":  {"it": "Preparazione dell'audio… {p}%", "en": "Preparing audio… {p}%"},
    "offline_warn":   {"it": "Modalità offline: voce di sistema (qualità inferiore).",
                       "en": "Offline mode: system voice (lower quality)."},
    "confirm_quit_exam": {"it": "Vuoi uscire dal test in corso? I progressi andranno persi.",
                          "en": "Quit the current test? Your progress will be lost."},
    "yes": {"it": "Sì", "en": "Yes"},
    "no":  {"it": "No", "en": "No"},
    "answered_of":    {"it": "Risposte date: {a}/{t}", "en": "Answered: {a}/{t}"},
    "match_hint":     {"it": "Tocca una frase e poi l'immagine corrispondente.",
                       "en": "Tap a sentence then its matching picture."},
}


class Translator:
    """Tiene la lingua corrente e traduce le chiavi."""

    def __init__(self, lang="it"):
        self.lang = lang if lang in ("it", "en") else "it"

    def set_language(self, lang):
        if lang in ("it", "en"):
            self.lang = lang

    def t(self, key, **fmt):
        entry = STRINGS.get(key)
        if entry is None:
            return key
        text = entry.get(self.lang, entry.get("it", key))
        if fmt:
            try:
                return text.format(**fmt)
            except (KeyError, IndexError):
                return text
        return text


# Istanza globale condivisa
tr = Translator()
