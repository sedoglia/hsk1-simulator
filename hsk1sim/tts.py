# -*- coding: utf-8 -*-
"""Sintesi vocale ibrida: edge-tts (online) con fallback pyttsx3 (offline).

I file audio vengono messi in cache su disco per hash del testo, cosi non
vengono rigenerati ogni volta.
"""
import asyncio
import hashlib
import os
import threading

from . import config

try:
    import edge_tts  # online, alta qualita
    _HAS_EDGE = True
except Exception:  # pragma: no cover
    _HAS_EDGE = False

try:
    import pyttsx3  # offline (SAPI)
    _HAS_PYTTSX3 = True
except Exception:  # pragma: no cover
    _HAS_PYTTSX3 = False


def _zh_len(text: str) -> int:
    """Numero di caratteri cinesi (esclude punteggiatura e spazi)."""
    return sum(1 for ch in text if "一" <= ch <= "鿿")


def rate_for(text: str) -> str:
    """Velocità edge-tts adattiva: più lenta per le frasi lunghe (parole scandite meglio)."""
    n = _zh_len(text)
    if n <= 4:
        return "-10%"
    if n <= 7:
        return "-22%"
    if n <= 10:
        return "-30%"
    return "-38%"


def _pyttsx_rate_for(text: str) -> int:
    """Velocità pyttsx3 (parole/min) adattiva alla lunghezza."""
    n = _zh_len(text)
    if n <= 4:
        return 150
    if n <= 7:
        return 135
    if n <= 10:
        return 122
    return 110


def _key(text: str) -> str:
    raw = f"{text}|{config.EDGE_VOICE}|{rate_for(text)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


class HybridTTS:
    def __init__(self):
        self.last_offline = False          # True se l'ultima sintesi e' avvenuta offline
        self._pyttsx_lock = threading.Lock()
        self._edge_failed = False          # se edge fallisce una volta, evitiamo nuovi tentativi

    # --- API pubblica ---
    def synth(self, text: str) -> str | None:
        """Restituisce il percorso del file audio per `text` (lo genera se serve)."""
        if not text:
            return None
        k = _key(text)
        mp3 = os.path.join(config.CACHE_DIR, k + ".mp3")
        wav = os.path.join(config.CACHE_DIR, k + ".wav")
        if os.path.exists(mp3) and os.path.getsize(mp3) > 0:
            return mp3
        if os.path.exists(wav) and os.path.getsize(wav) > 0:
            self.last_offline = True
            return wav

        # 1) prova online
        if _HAS_EDGE and not self._edge_failed:
            try:
                self._edge_synth(text, mp3)
                if os.path.exists(mp3) and os.path.getsize(mp3) > 0:
                    self.last_offline = False
                    return mp3
            except Exception:
                self._edge_failed = True  # probabilmente offline: non riprovare

        # 2) fallback offline
        if _HAS_PYTTSX3:
            try:
                self._pyttsx_synth(text, wav)
                if os.path.exists(wav) and os.path.getsize(wav) > 0:
                    self.last_offline = True
                    return wav
            except Exception:
                pass
        return None

    def prefetch(self, texts, progress=None):
        """Pre-genera l'audio per una lista di testi (con callback di avanzamento)."""
        uniq = [t for t in dict.fromkeys(texts) if t]
        total = len(uniq) or 1
        for i, t in enumerate(uniq, 1):
            self.synth(t)
            if progress:
                progress(int(i * 100 / total))

    # --- implementazioni ---
    def _edge_synth(self, text: str, out_path: str):
        async def _run():
            comm = edge_tts.Communicate(text, config.EDGE_VOICE, rate=rate_for(text))
            await comm.save(out_path)
        asyncio.run(_run())

    def _pyttsx_synth(self, text: str, out_path: str):
        with self._pyttsx_lock:
            engine = pyttsx3.init()
            # cerca una voce cinese installata in Windows
            try:
                for v in engine.getProperty("voices"):
                    name = (getattr(v, "name", "") or "").lower()
                    langs = " ".join(
                        l.decode() if isinstance(l, bytes) else str(l)
                        for l in (getattr(v, "languages", []) or [])
                    ).lower()
                    blob = f"{name} {langs} {getattr(v, 'id', '')}".lower()
                    if any(s in blob for s in ("chinese", "zh", "huihui", "kangkang", "yaoyao")):
                        engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass
            engine.setProperty("rate", _pyttsx_rate_for(text))
            engine.save_to_file(text, out_path)
            engine.runAndWait()
            engine.stop()


# Istanza globale condivisa
tts = HybridTTS()
