# -*- coding: utf-8 -*-
"""Test della cancellazione delle sequenze audio."""
import os
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from hsk1sim.audio import AudioPlayer


class TestAudioSequence(unittest.TestCase):
    def test_stop_cancels_remaining_sequence(self):
        player = AudioPlayer()
        played = []
        done = threading.Event()

        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name in ("one.mp3", "two.mp3"):
                path = os.path.join(tmp, name)
                open(path, "wb").close()
                paths.append(path)

            def fake_play(path, generation):
                played.append(path)
                return generation == player._generation

            with patch.object(player, "_play_file_blocking", side_effect=fake_play):
                player.play_sequence(paths, gap_sec=0.05, on_done=done.set)
                time.sleep(0.01)
                player.stop()
                time.sleep(0.12)

        self.assertEqual(played, [paths[0]])
        self.assertFalse(done.is_set())

    def test_sequence_never_starts_second_file_before_first_finishes(self):
        player = AudioPlayer()
        first_can_finish = threading.Event()
        second_started = threading.Event()

        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name in ("one.mp3", "two.mp3"):
                path = os.path.join(tmp, name)
                open(path, "wb").close()
                paths.append(path)

            def fake_play(path, generation):
                if path == paths[0]:
                    first_can_finish.wait(1)
                else:
                    second_started.set()
                return generation == player._generation

            with patch.object(player, "_play_file_blocking", side_effect=fake_play):
                player.play_sequence(paths, gap_sec=0)
                time.sleep(0.05)
                self.assertFalse(second_started.is_set())
                first_can_finish.set()
                self.assertTrue(second_started.wait(1))


if __name__ == "__main__":
    unittest.main()
