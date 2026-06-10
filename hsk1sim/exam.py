# -*- coding: utf-8 -*-
"""Modello d'esame: assembla le 40 domande, calcola il punteggio."""
from . import config, question_gen


class Exam:
    def __init__(self):
        self.listening = []   # 20 domande
        self.reading = []     # 20 domande
        self.start_ts = None
        self.end_ts = None

    @classmethod
    def generate(cls):
        ex = cls()
        for gen in question_gen.LISTENING_GENERATORS:
            ex.listening.extend(gen(config.QUESTIONS_PER_PART))
        for gen in question_gen.READING_GENERATORS:
            ex.reading.extend(gen(config.QUESTIONS_PER_PART))
        return ex

    # --- audio da pre-generare (solo ascolto) ---
    def listening_audio_texts(self):
        texts = []
        for q in self.listening:
            texts.extend(q.audio_texts)
        return texts

    # --- punteggio ---
    def _section_score(self, questions):
        if not questions:
            return 0, 0
        correct = sum(1 for q in questions if q.is_correct)
        score = round(correct * config.SECTION_MAX_SCORE / len(questions))
        return correct, score

    def score(self):
        l_correct, l_score = self._section_score(self.listening)
        r_correct, r_score = self._section_score(self.reading)
        total = l_score + r_score
        return {
            "listening_correct": l_correct,
            "listening_total": len(self.listening),
            "listening_score": l_score,
            "reading_correct": r_correct,
            "reading_total": len(self.reading),
            "reading_score": r_score,
            "total": total,
            "passed": total >= config.PASS_SCORE,
        }

    def duration_seconds(self):
        if self.start_ts and self.end_ts:
            return max(0, int(self.end_ts - self.start_ts))
        return 0

    def details(self):
        """Dettaglio per-parte del tentativo (per lo storico)."""
        def breakdown(questions):
            d = {}
            for q in questions:
                cell = d.setdefault(f"P{q.part}", [0, 0])
                cell[1] += 1
                if q.is_correct:
                    cell[0] += 1
            return d

        sc = self.score()
        return {
            "listening_parts": breakdown(self.listening),
            "reading_parts": breakdown(self.reading),
            "listening_correct": sc["listening_correct"],
            "reading_correct": sc["reading_correct"],
            "listening_score": sc["listening_score"],
            "reading_score": sc["reading_score"],
            "total": sc["total"],
            "duration_s": self.duration_seconds(),
        }
