# -*- coding: utf-8 -*-
"""Riproduzione audio tramite l'API MCI di Windows (winmm.dll).

Riproduce mp3 e wav nativamente senza dipendenze esterne (pygame non e'
disponibile su Python 3.14). La riproduzione e' asincrona.
"""
import ctypes
import os
import threading
import wave

from . import config

_winmm = ctypes.windll.winmm if os.name == "nt" else None
_lock = threading.Lock()
_alias_counter = [0]


def _mci(command: str) -> int:
    if _winmm is None:
        return 1
    return _winmm.mciSendStringW(ctypes.c_wchar_p(command), None, 0, None)


def _ensure_silence(ms=350):
    """Crea (una volta) un breve WAV di silenzio per 'svegliare' la scheda audio.

    Il primo suono dopo un periodo d'inattivita' viene spesso troncato dal device:
    riproducendo prima questo silenzio, il taglio cade sul silenzio e la voce
    successiva si sente completa.
    """
    path = os.path.join(config.CACHE_DIR, f"_silence_{ms}.wav")
    if not os.path.exists(path):
        rate = 22050
        frames = b"\x00\x00" * int(rate * ms / 1000)
        try:
            with wave.open(path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(frames)
        except Exception:
            return None
    return path


_SILENCE = _ensure_silence()


class AudioPlayer:
    """Riproduce un file alla volta; stop() interrompe la riproduzione corrente."""

    def __init__(self):
        self._alias = None
        self._generation = 0

    def stop(self):
        with _lock:
            # Invalida il worker corrente prima di interrompere il file.
            self._generation += 1
            if self._alias:
                _mci(f"stop {self._alias}")
                _mci(f"close {self._alias}")
                self._alias = None

    def warmup(self):
        """Sveglia la scheda audio una volta (in background), senza bloccare la UI."""
        threading.Thread(target=self._warmup, daemon=True).start()

    def _warmup(self):
        """Riproduce un brevissimo silenzio per 'svegliare' la scheda audio.

        Chiamato una sola volta all'avvio dell'esame: insieme a 'cue'/'seek' per
        clip elimina il taglio dei primi millisecondi alla prima riproduzione.
        """
        if not _SILENCE:
            return
        with _lock:
            _alias_counter[0] += 1
            alias = f"warm_{_alias_counter[0]}"
            if _mci(f'open "{_SILENCE}" type waveaudio alias {alias}') != 0:
                return
        _mci(f"cue {alias} output")
        _mci(f"play {alias} wait")
        _mci(f"close {alias}")

    def _play_file_blocking(self, path, generation):
        """Riproduce un singolo file e ritorna solo quando e' terminato."""
        with _lock:
            if generation != self._generation:
                return False
            _alias_counter[0] += 1
            alias = f"hsk_{_alias_counter[0]}"
            self._alias = alias
            ext = os.path.splitext(path)[1].lower()
            mci_type = "mpegvideo" if ext == ".mp3" else "waveaudio"
            # path tra virgolette per gestire spazi
            if _mci(f'open "{path}" type {mci_type} alias {alias}') != 0:
                if _mci(f'open "{path}" alias {alias}') != 0:
                    self._alias = None
                    return False

        # cue + seek: pre-carica il device e riparte dall'inizio, evitando che
        # i primi millisecondi della voce vengano tagliati alla prima riproduzione.
        _mci(f"seek {alias} to start")
        _mci(f"cue {alias} output")
        # "wait" evita la gara del polling: il file successivo parte solo dopo
        # il completamento effettivo di quello corrente.
        _mci(f"play {alias} wait")

        with _lock:
            still_current = generation == self._generation and self._alias == alias
            if self._alias == alias:
                _mci(f"close {alias}")
                self._alias = None
        return still_current

    def _start_worker(self, paths, gap_sec, on_done):
        paths = [p for p in paths if p and os.path.exists(p)]
        if not paths:
            if on_done:
                on_done()
            return

        self.stop()
        generation = self._generation

        def work():
            for i, path in enumerate(paths):
                if not self._play_file_blocking(path, generation):
                    return
                if i < len(paths) - 1:
                    # Pausa interrompibile: stop() impedisce la battuta seguente.
                    deadline = threading.Event()
                    if deadline.wait(gap_sec) or generation != self._generation:
                        return
            if generation == self._generation and on_done:
                on_done()

        threading.Thread(target=work, daemon=True).start()

    def play(self, path: str, on_done=None):
        """Riproduce `path` una volta in un worker seriale."""
        self._start_worker([path], 0, on_done)

    def play_sequence(self, paths, gap_sec=0.8, on_done=None):
        """Riproduce piu file in sequenza, senza possibilita' di sovrapposizione."""
        self._start_worker(paths, gap_sec, on_done)


# Istanza globale condivisa
player = AudioPlayer()
