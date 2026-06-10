# -*- coding: utf-8 -*-
"""Verifica che frasi e dialoghi usino SOLO le 150 parole ufficiali HSK1.

Tokenizza ogni frase con max-match goloso sul vocabolario e segnala i token
che non appartengono alle 150 ufficiali.

Esegui:  python validate_banks.py
"""
import json
import os
import re

DATA = os.path.join(os.path.dirname(__file__), "hsk1sim", "data")

vocab = json.load(open(os.path.join(DATA, "vocab_hsk1.json"), encoding="utf-8"))
official = set(json.load(open(os.path.join(DATA, "official_150.json"), encoding="utf-8")))
# vocabolario noto per la segmentazione (tutte le voci), ordinato per lunghezza desc
known = sorted({w["hanzi"] for w in vocab}, key=len, reverse=True)
# Ammessi: composti/morfemi di parole ufficiali e parole effettivamente usate
# nei FOGLI D'ESAME UFFICIALI HSK1 (che vanno oltre la lista "stretta" di 150).
EXTRA_OK = {
    # composti e forme di parole ufficiali
    "一些", "一点儿", "很多", "这儿", "那儿", "哪儿", "你好", "我们", "你们",
    "他们", "她们", "名字", "做菜", "做饭", "每天",
    # morfemi che compongono parole ufficiali (前面/外面/今天/中国/说话/...)
    "面", "外", "国", "说", "天", "汉", "儿", "雨", "们", "今",
    # nomi propri usati nei dialoghi (王明, 小白)
    "王", "明", "白",
    # parole presenti nei fogli d'esame ufficiali HSK1
    "它", "弟弟", "妹妹", "哥哥", "姐姐", "只", "杯", "两", "好吃", "件",
    "还", "还是", "贵", "给", "新", "把", "忙", "帮", "咖啡", "晚上", "早上",
    "一起", "做", "饭", "号", "有点儿",
}

CJK = re.compile(r"[一-鿿]")


def tokenize(text):
    text = "".join(ch for ch in text if CJK.match(ch))
    tokens, i = [], 0
    while i < len(text):
        for w in known:
            if text.startswith(w, i):
                tokens.append(w)
                i += len(w)
                break
        else:
            tokens.append(text[i])
            i += 1
    return tokens


def offenders(text):
    bad = []
    for tok in tokenize(text):
        if tok in official or tok in EXTRA_OK:
            continue
        bad.append(tok)
    return bad


def check_file(name, fields):
    data = json.load(open(os.path.join(DATA, name), encoding="utf-8"))
    n_bad = 0
    for entry in data:
        text = " ".join(entry.get(f, "") for f in fields)
        bad = offenders(text)
        if bad:
            n_bad += 1
            print(f"  [{name}] {text.strip()[:40]} -> fuori-150: {' '.join(bad)}")
    print(f"== {name}: {len(data)} voci, {n_bad} con parole fuori-150\n")
    return n_bad


def main():
    print("Validazione banche (solo 150 ufficiali)\n")
    total = 0
    total += check_file("sentences.json", ["zh"])
    total += check_file("dialogues.json", ["q", "a"])
    total += check_file("grammar.json", ["q", "a"])
    print("TOTALE voci con parole fuori-150:", total)


if __name__ == "__main__":
    main()
