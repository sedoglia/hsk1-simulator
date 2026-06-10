# -*- coding: utf-8 -*-
"""Test su immagini e varietà delle domande illustrate.

Verifica:
  - copertura: abbastanza concetti con immagine;
  - coerenza: in una domanda-immagine TUTTE le opzioni sono foto (mai mix foto/emoji);
  - i file immagine referenziati esistono su disco;
  - varietà: ripetendo il test compaiono molte immagini e frasi diverse.
"""
import os
import unittest

import hsk1sim.question_gen as qg
from hsk1sim.exam import Exam


class TestImageCoverage(unittest.TestCase):
    def test_enough_image_concepts(self):
        self.assertGreaterEqual(len(qg.IMAGE_VOCAB), 50,
                                "troppi pochi concetti illustrati per le domande-immagine")

    def test_image_files_exist(self):
        for _ in range(10):
            ex = Exam.generate()
            for q in ex.listening + ex.reading:
                if q.qtype == "image":
                    for o in q.options:
                        self.assertTrue(o.get("image"), "opzione-immagine senza foto")
                        self.assertTrue(os.path.exists(o["image"]),
                                        f"file immagine mancante: {o.get('image')}")


class TestImageConsistency(unittest.TestCase):
    def test_no_photo_emoji_mix(self):
        """Dentro una domanda-immagine non si mischiano foto ed emoji (svelerebbe la risposta)."""
        for _ in range(20):
            ex = Exam.generate()
            for q in ex.listening + ex.reading:
                if q.qtype == "image":
                    has = [bool(o.get("image")) for o in q.options]
                    self.assertTrue(all(has) or not any(has),
                                    f"{q.section} P{q.part}: mix foto/emoji nelle opzioni")

    def test_image_options_distinct_within_question(self):
        for _ in range(20):
            ex = Exam.generate()
            for q in ex.listening + ex.reading:
                if q.qtype == "image":
                    imgs = [o.get("image") for o in q.options]
                    self.assertEqual(len(set(imgs)), len(imgs),
                                     f"{q.section} P{q.part}: immagini duplicate tra le opzioni")


class TestVariety(unittest.TestCase):
    """Ripetendo il test devono comparire immagini e frasi diverse."""

    @classmethod
    def setUpClass(cls):
        cls.sentences, cls.images = set(), set()
        for _ in range(40):
            ex = Exam.generate()
            for q in ex.listening + ex.reading:
                if q.qtype == "image":
                    for o in q.options:
                        if o.get("image"):
                            cls.images.add(o["image"])
                if q.part in (2, 3):
                    cls.sentences.add(q.review_zh)

    def test_many_distinct_images(self):
        self.assertGreaterEqual(len(self.images), 40,
                                f"poca varietà di immagini ({len(self.images)})")

    def test_many_distinct_sentences(self):
        self.assertGreaterEqual(len(self.sentences), 80,
                                f"poca varietà di frasi ({len(self.sentences)})")


if __name__ == "__main__":
    unittest.main(verbosity=2)
