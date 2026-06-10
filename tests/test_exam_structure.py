# -*- coding: utf-8 -*-
"""Test automatici: gli esami generati rispettano la struttura HSK1 reale.

Specifica di riferimento: SYLLABUS UFFICIALE (HSK 考试大纲 一级) + 样卷 ufficiale del
教育部中外语言交流合作中心, confermati dal foglio d'esame H10901:
  - 40 quesiti, 2 prove: 听力 (20 题, 约15 分钟) + 阅读 (20 题, 17 分钟)
  - 填写答题卡: 3 min · 共计 ~35 min effettivi · totale ~40 min (incl. 5 min dati personali)
  - Nota ufficiale: «试卷上的试题都有拼音» (tutte le domande riportano il pinyin)
  - Ascolto: 4 parti da 5 · Lettura: 4 parti da 5
  - Ascolto P1: vero/falso (1 immagine) · P2: 3 immagini A/B/C · P3: ABBINAMENTO 6 immagini
  - Lettura P1: vero/falso (parola+immagine) · P2: ABBINAMENTO 6 immagini ·
    P3: ABBINAMENTO 6 risposte · P4: ABBINAMENTO 6 parole
  - Orale base 100 · Testo base 100 · Totale 200 · Sufficienza 120/200

Esegui:  python -m unittest discover tests -v
"""
import unittest

from hsk1sim import config
from hsk1sim.exam import Exam
from hsk1sim import question_gen as qg


# Specifica ufficiale (tuttocina.it) usata come "verita" per i test
SPEC = {
    "total_questions": 40,
    "listening_questions": 20,
    "reading_questions": 20,
    "parts_per_section": 4,
    "questions_per_part": 5,
    "section_max": 100,
    "total_max": 200,
    "pass_score": 120,
    "listening_minutes": 15,
    "reading_minutes": 17,
    "answer_card_minutes": 3,
    "personal_info_minutes": 5,
    "listening_plays": 2,
}

# parti ad abbinamento: banco condiviso di 6 opzioni (A-F) per 5 domande
MATCHING_PARTS = {("listening", 3), ("reading", 2), ("reading", 3), ("reading", 4)}


def expected_option_count(section, part):
    if EXPECTED_TYPES[(section, part)] == "tf":
        return 2
    if (section, part) in MATCHING_PARTS:
        return 6
    return 3  # scelta tripla A/B/C

# tipologia attesa per ciascuna parte
EXPECTED_TYPES = {
    ("listening", 1): "tf",
    ("listening", 2): "image",
    ("listening", 3): "image",
    ("listening", 4): "text",
    ("reading", 1): "tf",
    ("reading", 2): "image",
    ("reading", 3): "text",
    ("reading", 4): "text",
}


def gen_many(n=30):
    return [Exam.generate() for _ in range(n)]


class TestConfigMatchesSpec(unittest.TestCase):
    """La configurazione dell'app coincide con la specifica tuttocina."""

    def test_question_counts(self):
        self.assertEqual(config.TOTAL_QUESTIONS, SPEC["total_questions"])
        self.assertEqual(config.QUESTIONS_PER_PART, SPEC["questions_per_part"])
        self.assertEqual(config.LISTENING_PARTS, SPEC["parts_per_section"])
        self.assertEqual(config.READING_PARTS, SPEC["parts_per_section"])

    def test_scoring(self):
        self.assertEqual(config.SECTION_MAX_SCORE, SPEC["section_max"])
        self.assertEqual(config.TOTAL_MAX_SCORE, SPEC["total_max"])
        self.assertEqual(config.PASS_SCORE, SPEC["pass_score"])

    def test_timing(self):
        self.assertEqual(config.LISTENING_TIME_SEC, SPEC["listening_minutes"] * 60)
        self.assertEqual(config.READING_TIME_SEC, SPEC["reading_minutes"] * 60)
        self.assertEqual(config.ANSWER_CARD_TIME_SEC, SPEC["answer_card_minutes"] * 60)
        self.assertEqual(config.PERSONAL_INFO_TIME_SEC, SPEC["personal_info_minutes"] * 60)

    def test_audio_played_twice(self):
        self.assertEqual(config.LISTENING_PLAYS, SPEC["listening_plays"])


class TestExamStructure(unittest.TestCase):
    """Struttura delle domande generate (su molti esami casuali)."""

    @classmethod
    def setUpClass(cls):
        cls.exams = gen_many(30)

    def test_total_and_section_counts(self):
        for ex in self.exams:
            self.assertEqual(len(ex.listening) + len(ex.reading), SPEC["total_questions"])
            self.assertEqual(len(ex.listening), SPEC["listening_questions"])
            self.assertEqual(len(ex.reading), SPEC["reading_questions"])

    def test_four_parts_five_questions_each(self):
        for ex in self.exams:
            for section, qs in (("listening", ex.listening), ("reading", ex.reading)):
                counts = {}
                for q in qs:
                    self.assertEqual(q.section, section)
                    self.assertIn(q.part, (1, 2, 3, 4))
                    counts[q.part] = counts.get(q.part, 0) + 1
                self.assertEqual(sorted(counts), [1, 2, 3, 4],
                                 f"{section}: devono esserci esattamente 4 parti")
                for part, c in counts.items():
                    self.assertEqual(c, SPEC["questions_per_part"],
                                     f"{section} parte {part}: attesi 5 quesiti, trovati {c}")

    def test_question_types_per_part(self):
        for ex in self.exams:
            for q in ex.listening + ex.reading:
                self.assertEqual(q.qtype, EXPECTED_TYPES[(q.section, q.part)],
                                 f"tipo errato per {q.section} P{q.part}")

    def test_options_count_and_correct_index(self):
        for ex in self.exams:
            for q in ex.listening + ex.reading:
                expected = expected_option_count(q.section, q.part)
                self.assertEqual(len(q.options), expected,
                                 f"{q.section} P{q.part}: attese {expected} opzioni")
                self.assertTrue(0 <= q.correct < len(q.options),
                                "indice della risposta corretta fuori range")

    def test_matching_parts_share_pool_of_six(self):
        """Le parti ad abbinamento: 5 domande con lo STESSO banco di 6 opzioni,
        5 risposte corrette distinte (1 distrattore non usato)."""
        for ex in self.exams:
            by_part = {}
            for q in ex.listening + ex.reading:
                if (q.section, q.part) in MATCHING_PARTS:
                    by_part.setdefault((q.section, q.part), []).append(q)
            for key, qs in by_part.items():
                self.assertEqual(len(qs), 5, f"{key}: 5 domande")
                # stesso banco condiviso (stesso oggetto lista) di 6 opzioni
                pool = qs[0].options
                self.assertEqual(len(pool), 6, f"{key}: banco di 6 opzioni")
                for q in qs:
                    self.assertIs(q.options, pool, f"{key}: banco non condiviso")
                # 5 risposte corrette distinte fra le 6 opzioni
                corrects = {q.correct for q in qs}
                self.assertEqual(len(corrects), 5, f"{key}: 5 risposte corrette distinte")

    def test_listening_has_audio_reading_has_none(self):
        for ex in self.exams:
            for q in ex.listening:
                self.assertTrue(q.audio_texts, "domanda d'ascolto senza audio")
            for q in ex.reading:
                self.assertEqual(q.audio_texts, [], "domanda di lettura non deve avere audio")
                # la lettura deve mostrare uno stimolo (immagine o testo)
                self.assertTrue(q.display_image or q.display_zh)

    def test_image_options_have_visual(self):
        for ex in self.exams:
            for q in ex.listening + ex.reading:
                if q.qtype == "image":
                    for opt in q.options:
                        self.assertEqual(opt["kind"], "image")
                        self.assertTrue(opt.get("image") or opt.get("emoji"))

    def test_scene_questions_use_local_images(self):
        for ex in self.exams:
            for q in ex.listening + ex.reading:
                if (q.section, q.part) in {("listening", 2), ("listening", 3),
                                          ("reading", 2)}:
                    for opt in q.options:
                        self.assertTrue(opt.get("image"))
                if q.qtype == "tf":
                    self.assertTrue(q.display_image_path)


class TestScoring(unittest.TestCase):
    """Calcolo del punteggio in base 100/100/200 con soglia 120."""

    def test_perfect_score(self):
        ex = Exam.generate()
        for q in ex.listening + ex.reading:
            q.user_answer = q.correct
        sc = ex.score()
        self.assertEqual(sc["listening_score"], 100)
        self.assertEqual(sc["reading_score"], 100)
        self.assertEqual(sc["total"], 200)
        self.assertTrue(sc["passed"])

    def test_zero_score(self):
        ex = Exam.generate()
        sc = ex.score()  # nessuna risposta
        self.assertEqual(sc["total"], 0)
        self.assertFalse(sc["passed"])

    def test_partial_score_and_threshold(self):
        ex = Exam.generate()
        # 12 corrette su 20 nell'ascolto, 12 su 20 nella lettura
        for i, q in enumerate(ex.listening):
            q.user_answer = q.correct if i < 12 else (q.correct + 1) % len(q.options)
        for i, q in enumerate(ex.reading):
            q.user_answer = q.correct if i < 12 else (q.correct + 1) % len(q.options)
        sc = ex.score()
        self.assertEqual(sc["listening_score"], round(12 * 100 / 20))  # 60
        self.assertEqual(sc["reading_score"], round(12 * 100 / 20))    # 60
        self.assertEqual(sc["total"], 120)
        self.assertTrue(sc["passed"])  # 120 e' esattamente la soglia

    def test_just_below_threshold_fails(self):
        ex = Exam.generate()
        for i, q in enumerate(ex.listening):
            q.user_answer = q.correct if i < 11 else (q.correct + 1) % len(q.options)
        for i, q in enumerate(ex.reading):
            q.user_answer = q.correct if i < 12 else (q.correct + 1) % len(q.options)
        sc = ex.score()  # 55 + 60 = 115
        self.assertLess(sc["total"], SPEC["pass_score"])
        self.assertFalse(sc["passed"])


class TestRandomness(unittest.TestCase):
    """Ogni esame deve essere diverso (domande casuali)."""

    def test_exams_differ(self):
        def signature(ex):
            return tuple(q.review_zh for q in ex.listening + ex.reading)
        sigs = {signature(Exam.generate()) for _ in range(10)}
        self.assertGreater(len(sigs), 1, "gli esami generati sono tutti identici")

    def test_no_exceptions_over_many_generations(self):
        try:
            gen_many(50)
        except Exception as e:  # pragma: no cover
            self.fail(f"generazione fallita: {e}")


class TestOfficialVocabulary(unittest.TestCase):
    """Le domande usano solo le 150 parole del syllabus ufficiale."""

    def test_vocab_marks_exactly_150_official(self):
        official = [w for w in qg.VOCAB if w.get("hsk1_official")]
        self.assertEqual(len(official), 150, "devono essere marcate esattamente 150 parole ufficiali")

    def test_pool_restricted_to_official(self):
        if not config.OFFICIAL_150_ONLY:
            self.skipTest("modalita' 150-only disattivata")
        for w in qg.VOCAB_POOL:
            self.assertTrue(w.get("hsk1_official"), f"{w['hanzi']} non e' ufficiale")

    def test_tested_words_are_official(self):
        """Ogni opzione/stimolo che corrisponde a un vocabolo deve essere ufficiale."""
        if not config.OFFICIAL_150_ONLY:
            self.skipTest("modalita' 150-only disattivata")
        offenders = set()
        for _ in range(30):
            ex = Exam.generate()
            for q in ex.listening + ex.reading:
                words = [o.get("zh") for o in q.options]
                words += [q.display_zh]
                for zh in words:
                    w = qg.VOCAB_BY_HANZI.get(zh)
                    if w and not w.get("hsk1_official"):
                        offenders.add(zh)
        self.assertEqual(offenders, set(), f"parole non ufficiali usate: {offenders}")


class TestGrammarCoverage(unittest.TestCase):
    """La Parte 4 di Lettura verifica le regole grammaticali HSK1."""

    def test_reading_p4_is_grammar(self):
        for _ in range(20):
            ex = Exam.generate()
            p4 = [q for q in ex.reading if q.part == 4]
            self.assertEqual(len(p4), 5)
            for q in p4:
                self.assertIsNotNone(q.grammar_point, "P4 deve avere un punto grammaticale")
                self.assertEqual(len(q.grammar_point), 2)  # (it, en)
                # distrattori grammaticalmente plausibili ma diversi dalla risposta
                labels = [o["zh"] for o in q.options]
                self.assertEqual(len(set(labels)), len(labels), "opzioni duplicate")

    def test_grammar_bank_integrity(self):
        for g in qg.GRAMMAR:
            self.assertIn("（ ____ ）", g["q"])
            self.assertNotIn(g["a"], g["d"])
            self.assertEqual(len(g["d"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
