# -*- coding: utf-8 -*-
"""Generazione randomica delle domande per le 8 parti dell'esame HSK1.

Ogni generatore restituisce 5 oggetti Question. I distrattori sono pescati dal
vocabolario in modo coerente (stessa categoria quando possibile).
"""
import json
import random

from pypinyin import Style, pinyin as _pinyin

from . import config
from .visual_catalog import (dialogue_scene, has_word_image, sentence_has_image,
                             sentence_image, word_scene)

# ---------------------------------------------------------------- caricamento dati
with open(config.VOCAB_FILE, encoding="utf-8") as f:
    VOCAB = json.load(f)
with open(config.SENTENCES_FILE, encoding="utf-8") as f:
    SENTENCES = json.load(f)
with open(config.DIALOGUES_FILE, encoding="utf-8") as f:
    DIALOGUES = json.load(f)
with open(config.GRAMMAR_FILE, encoding="utf-8") as f:
    GRAMMAR = json.load(f)

VOCAB_BY_HANZI = {w["hanzi"]: w for w in VOCAB}

# Pool effettivo: solo le 150 ufficiali se richiesto dal syllabus, altrimenti tutte.
if config.OFFICIAL_150_ONLY:
    VOCAB_POOL = [w for w in VOCAB if w.get("hsk1_official")]
else:
    VOCAB_POOL = list(VOCAB)

POOL_HANZI = {w["hanzi"] for w in VOCAB_POOL}
POOL_EMOJI = {w["emoji"] for w in VOCAB_POOL if w.get("emoji")}
EMOJI_VOCAB = [w for w in VOCAB_POOL if w.get("emoji")]
IMAGE_VOCAB = [w for w in EMOJI_VOCAB if has_word_image(w["hanzi"])]

# Frasi utilizzabili: hanno un'immagine (scena curata o foto della parola-chiave)
# e la parola-chiave appartiene al pool (150 ufficiali).
SENTENCES_POOL = [s for s in SENTENCES
                  if sentence_has_image(s["zh"], s.get("key")) and s.get("key") in POOL_HANZI]
EMOJI_DIALOGUES = [d for d in DIALOGUES if dialogue_scene(d["a"])]

# Parte 4: parole del banco (contenuto + grammatica) tutte presenti nel vocabolario.
GRAMMAR_POOL = [g for g in GRAMMAR
                if g["a"] in VOCAB_BY_HANZI and all(d in VOCAB_BY_HANZI for d in g["d"])]

# Item "ricchi" (parola di contenuto da inserire o frase composta/dialogo) vs base
# (parola grammaticale, frase breve). Il foglio reale mescola entrambi ~a metà.
_R4_FUNCTION = {"是", "有", "在", "很", "太", "不", "没", "吗", "呢", "的", "了", "个",
                "本", "块", "岁", "会", "能", "想", "都", "和", "上", "里", "点", "几",
                "多少", "什么", "谁", "喜欢", "请"}


def _r4_is_rich(g):
    qlen = sum(1 for ch in g["q"] if "一" <= ch <= "鿿")
    return g["a"] not in _R4_FUNCTION or qlen >= 9


GRAMMAR_RICH = [g for g in GRAMMAR_POOL if _r4_is_rich(g)]


def pin(zh: str) -> str:
    """Pinyin di una stringa cinese (con toni)."""
    w = VOCAB_BY_HANZI.get(zh)
    if w:
        return w["pinyin"]
    return " ".join(s[0] for s in _pinyin(zh, style=Style.TONE))


def _by_category(cat):
    return [w for w in VOCAB_POOL if w["category"] == cat]


_CN_DIGITS = "零一二三四五六七八九"


def num2cn(n: int) -> str:
    """Converte un intero 0-99 in numerale cinese (per pronuncia e fedelta)."""
    if n < 10:
        return _CN_DIGITS[n]
    if n < 20:
        return "十" + (_CN_DIGITS[n % 10] if n % 10 else "")
    if n < 100:
        tens, ones = divmod(n, 10)
        return _CN_DIGITS[tens] + "十" + (_CN_DIGITS[ones] if ones else "")
    return str(n)


# ---------------------------------------------------------------- modello Question
class Question:
    def __init__(self, section, part, qtype, instr_key):
        self.section = section          # "listening" | "reading"
        self.part = part                # 1..4
        self.qtype = qtype              # "tf" | "image" | "text"
        self.instr_key = instr_key
        self.audio_texts = []           # testi cinesi da pronunciare (ascolto)
        self.display_image = None       # emoji mostrata come stimolo
        self.display_image_path = None  # scena fotografica mostrata come stimolo
        self.display_zh = None          # testo cinese mostrato (lettura)
        self.display_pinyin = None
        self.options = []               # lista di dict opzione
        self.correct = 0                # indice opzione corretta
        self.user_answer = None         # indice scelto dall'utente
        # dati per la revisione
        self.review_zh = ""
        self.review_pinyin = ""
        self.review_it = ""
        self.review_en = ""
        self.grammar_point = None       # (it, en) del punto grammaticale, se presente

    @property
    def is_correct(self):
        return self.user_answer == self.correct


def _img_opt(word):
    return {"kind": "image", "emoji": word["emoji"], "zh": word["hanzi"],
            "pinyin": word["pinyin"], "it": word["it"], "en": word["en"],
            "image": word_scene(word["hanzi"])}


def _scene_opt(item, image_path, zh, it, en):
    return {"kind": "image", "emoji": item.get("emoji"), "image": image_path,
            "zh": zh, "pinyin": pin(zh), "it": it, "en": en}


def _sentence_opt(sentence):
    return _scene_opt(sentence, sentence_image(sentence["zh"], sentence.get("key")), "",
                      sentence["it"], sentence["en"])


def _dialogue_opt(dialogue):
    return _scene_opt(dialogue, dialogue_scene(dialogue["a"]), dialogue["a"],
                      dialogue["a_it"], dialogue["a_en"])


def _txt_opt(zh, it="", en=""):
    return {"kind": "text", "emoji": None, "zh": zh, "pinyin": pin(zh),
            "it": it, "en": en}


def _shuffle_with_correct(options, correct_opt):
    """Mischia le opzioni e restituisce (lista, indice_corretto)."""
    opts = options[:]
    random.shuffle(opts)
    return opts, opts.index(correct_opt)


def _img_opt_from_emoji(emoji):
    """Costruisce un'opzione-immagine dall'emoji (con significato dal vocabolario)."""
    w = next((x for x in EMOJI_VOCAB if x["emoji"] == emoji), None)
    if w:
        return _img_opt(w)
    return {"kind": "image", "emoji": emoji, "image": None,
            "zh": "", "pinyin": "", "it": "", "en": ""}


def _visual_key(word):
    return word["hanzi"]   # distinzione per concetto (l'immagine puo' variare)


def _pick_distinct(items, keyfn, k):
    """Sceglie k elementi con chiave (keyfn) a due a due distinta."""
    pool = items[:]
    random.shuffle(pool)
    chosen, seen = [], set()
    for it in pool:
        kv = keyfn(it)
        if kv and kv not in seen:
            seen.add(kv)
            chosen.append(it)
            if len(chosen) == k:
                break
    return chosen


def _idx(pool, obj):
    """Indice per identita' (evita confusioni tra dict con stesso valore)."""
    for i, o in enumerate(pool):
        if o is obj:
            return i
    return 0


def _matching_pool(correct_opts, extra_opt):
    """Banco condiviso di 6 opzioni (5 corrette + 1 distrattore extra), mischiato."""
    pool = list(correct_opts) + [extra_opt]
    random.shuffle(pool)
    return pool


# ---------------------------------------------------------------- generazione frasi/dialoghi
# Frasi e mini-dialoghi generati da modelli sui concetti illustrati: varietà
# (quasi) infinita e sempre con sole parole delle 150, ogni concetto ha un'immagine.
_DRINKS = {"茶", "水"}

# frasi naturali (stile esame reale) raggruppate per parola-chiave (concetto illustrato)
from collections import defaultdict as _dd
_CURATED_BY_KEY = _dd(list)
for _s in SENTENCES:
    if _s.get("key"):
        _CURATED_BY_KEY[_s["key"]].append(_s)

# dialoghi naturali (2 battute) raggruppati per concetto illustrato (per l'ascolto P3)
_DIALOGUES_BY_KEY = _dd(list)
for _d in DIALOGUES:
    if _d.get("key"):
        _DIALOGUES_BY_KEY[_d["key"]].append(_d)


_ADJ_TR = {
    "热": ("Oggi fa caldo.", "It's hot today."),
    "冷": ("Oggi fa freddo.", "It's cold today."),
    "高兴": ("Sono contento.", "I'm happy."),
}


def make_image_sentence(w):
    """Frase semplice (solo parole base) che descrive il concetto `w`.

    Più modelli per categoria -> più varietà testuale (ogni esecuzione differente).
    """
    h, cat, it, en = w["hanzi"], w["category"], w["it"], w["en"]
    variants = []
    if cat == "food":
        if h in _DRINKS:
            variants = [
                (f"我想喝{h}。", f"Voglio bere {it}.", f"I want to drink {en}."),
                (f"我喜欢喝{h}。", f"Mi piace bere {it}.", f"I like to drink {en}."),
                (f"这是{h}。", f"Questo è {it}.", f"This is {en}."),
            ]
        else:
            variants = [
                (f"我喜欢吃{h}。", f"Mi piace mangiare {it}.", f"I like to eat {en}."),
                (f"我想吃{h}。", f"Voglio mangiare {it}.", f"I want to eat {en}."),
                (f"这是{h}。", f"Questo è {it}.", f"This is {en}."),
            ]
    elif cat == "animal":
        variants = [
            (f"我家有{h}。", f"A casa ho un {it}.", f"I have a {en} at home."),
            (f"我喜欢{h}。", f"Mi piacciono i {it}.", f"I like {en}s."),
            (f"这是{h}。", f"Questo è un {it}.", f"This is a {en}."),
        ]
    elif cat == "people":
        if h == "人":
            variants = [("那儿有很多人。", "Lì ci sono molte persone.", "There are many people there.")]
        elif h in {"老师", "医生", "学生"}:
            variants = [
                (f"他是{h}。", f"Lui è un {it}.", f"He is a {en}."),
                (f"这是我的{h}。", f"Questo è il mio {it}.", f"This is my {en}."),
            ]
        else:
            variants = [
                (f"这是我的{h}。", f"Questo è il mio/la mia {it}.", f"This is my {en}."),
                (f"我爱我的{h}。", f"Amo il mio/la mia {it}.", f"I love my {en}."),
            ]
    elif cat == "place":
        variants = [
            (f"我去{h}。", f"Vado: {it}.", f"I go to the {en}."),
            (f"他在{h}。", f"È a/in: {it}.", f"He is at the {en}."),
            (f"我在{h}。", f"Sono a/in: {it}.", f"I am at the {en}."),
        ]
    elif cat == "transport":
        variants = [
            (f"我坐{h}去北京。", f"Vado a Pechino in {it}.", f"I go to Beijing by {en}."),
            (f"这是{h}。", f"Questo è {it}.", f"This is a {en}."),
        ]
    elif cat == "verb":
        # solo forme sicure (evita progressivi sgrammaticati tipo "他在下雨")
        variants = [(f"我喜欢{h}。", f"Mi piace: {it}.", f"I like to {en}.")]
    elif cat == "adj":
        zh = f"今天很{h}。" if h in {"热", "冷"} else f"我很{h}。"
        t = _ADJ_TR.get(h, (it.capitalize() + ".", en.capitalize() + "."))
        variants = [(zh, t[0], t[1])]
    else:  # object e altro
        variants = [
            (f"这是{h}。", f"Questo è {it}.", f"This is a {en}."),
            (f"我有{h}。", f"Ho {it}.", f"I have a {en}."),
            (f"这是我的{h}。", f"Questo è il mio {it}.", f"This is my {en}."),
        ]
    zh, vit, ven = random.choice(variants)
    return {"zh": zh, "it": vit, "en": ven, "key": h}


def sentence_for_concept(w):
    """Frase naturale (stile esame reale) per il concetto; modello solo se non disponibile."""
    curated = _CURATED_BY_KEY.get(w["hanzi"])
    if curated:
        return random.choice(curated)
    return make_image_sentence(w)


def dialogue_for_concept(w):
    """Mini-dialogo naturale (2 battute) che rivela il concetto; fallback su una frase."""
    dias = _DIALOGUES_BY_KEY.get(w["hanzi"])
    if dias:
        d = random.choice(dias)
        return {"q": d["q"], "a": d["a"], "zh": d["a"],
                "it": d.get("a_it", ""), "en": d.get("a_en", "")}
    s = sentence_for_concept(w)
    return {"q": "", "a": s["zh"], "zh": s["zh"], "it": s["it"], "en": s["en"]}


def _concept_opt(w, sentence):
    """Opzione-immagine per un concetto, con l'immagine coerente alla frase."""
    return {"kind": "image", "emoji": w["emoji"],
            "image": sentence_image(sentence["zh"], w["hanzi"]),
            "zh": "", "pinyin": "", "it": sentence["it"], "en": sentence["en"]}


def _distinct_image_items(build, k):
    """Sceglie k concetti con IMMAGINI a due a due distinte (concetti diversi possono
    condividere la stessa scena, quindi va garantita l'unicità dell'immagine).

    `build(concept)` -> dict con 'zh' o 'a' (testo) e 'it'/'en'.
    Restituisce lista di (concept, payload, image_path).
    """
    pool = IMAGE_VOCAB[:]
    random.shuffle(pool)
    items, used = [], set()
    for w in pool:
        p = build(w)
        text = p.get("zh") or p.get("a") or ""
        img = sentence_image(text, w["hanzi"])
        if not img or img in used:
            continue
        used.add(img)
        items.append((w, p, img))
        if len(items) == k:
            break
    return items


def _image_option(w, payload, img):
    return {"kind": "image", "emoji": w["emoji"], "image": img,
            "zh": "", "pinyin": "", "it": payload.get("it", ""), "en": payload.get("en", "")}


def make_concept_dialogue(w):
    """Mini-dialogo (Q + A) che rivela il concetto `w` (per l'ascolto P3)."""
    h, cat, it, en = w["hanzi"], w["category"], w["it"], w["en"]
    if cat == "food":
        verb = "喝" if h in _DRINKS else "吃"
        q, a = f"你喜欢{verb}什么？", f"我喜欢{verb}{h}。"
    elif cat == "people":
        if h == "人":
            q, a = "那儿有人吗？", "有很多人。"
        else:
            q, a = "他是谁？", f"他是我的{h}。"
    elif cat == "place":
        q, a = "你去哪儿？", f"我去{h}。"
    elif cat == "transport":
        q, a = "你怎么去？", f"我坐{h}去。"
    elif cat == "verb":
        q, a = "他在做什么？", f"他在{h}。"
    else:  # object/animal/adj/...
        q, a = "这是什么？", f"这是{h}。"
    return {"q": q, "a": a, "key": h,
            "q_it": "", "a_it": f"{it}", "q_en": "", "a_en": f"{en}"}


# Frasi brevi per l'Ascolto P1 (come nel reale: 打电话, 吃米饭, 下雨了, 一只猫...).
# La parola-chiave (concetto illustrato) resta `w["hanzi"]`; qui solo l'AUDIO è una frase.
L1_PHRASES = {
    "吃": "吃米饭", "喝": "喝水", "看": "看电视", "读": "读书", "写": "写字",
    "坐": "坐飞机", "买": "买东西", "打电话": "打电话", "睡觉": "睡觉了",
    "学习": "学习汉语", "工作": "去工作", "下雨": "下雨了", "听": "他在听",
    "住": "住在家", "爱": "我爱你",
    "茶": "一杯茶", "水": "喝水", "米饭": "吃米饭", "菜": "做菜",
    "苹果": "吃苹果", "水果": "买水果",
    "书": "看书", "电视": "看电视", "电影": "看电影", "电脑": "我的电脑",
    "杯子": "一个杯子", "钱": "很多钱", "衣服": "买衣服", "椅子": "一把椅子",
    "爸爸": "我爸爸", "妈妈": "我妈妈", "儿子": "我儿子", "女儿": "我女儿",
    "朋友": "我朋友", "老师": "我的老师", "学生": "很多学生", "医生": "他是医生",
    "人": "很多人",
    "学校": "去学校", "家": "回家", "商店": "去商店", "医院": "去医院",
    "火车站": "在火车站", "中国": "去中国",
    "飞机": "坐飞机", "出租车": "坐出租车",
    "狗": "一只狗", "猫": "一只猫",
    "热": "天气很热", "冷": "天气很冷", "高兴": "很高兴",
    "天气": "天气很好", "点": "三点",
}


# ---------------------------------------------------------------- ASCOLTO
def gen_listening_p1(n=5):
    """Frase breve (audio) + immagine -> Vero/Falso (come il foglio reale)."""
    out = []
    words = random.sample(IMAGE_VOCAB, k=min(n * 2, len(IMAGE_VOCAB)))
    for i in range(n):
        w = words[i]
        match = random.random() < 0.5
        if match:
            shown = w
        else:
            shown = random.choice([x for x in IMAGE_VOCAB if _visual_key(x) != _visual_key(w)])
        phrase = L1_PHRASES.get(w["hanzi"], w["hanzi"])
        q = Question("listening", 1, "tf", "instr_L1")
        q.audio_texts = [phrase]
        q.display_image = shown["emoji"]
        q.display_image_path = word_scene(shown["hanzi"])
        q.options = [{"kind": "tf", "value": True}, {"kind": "tf", "value": False}]
        q.correct = 0 if match else 1
        q.review_zh = phrase
        q.review_pinyin = pin(phrase)
        q.review_it = f"Audio: {phrase} ({w['it']}) · Immagine: {shown['it']}"
        q.review_en = f"Audio: {phrase} ({w['en']}) · Picture: {shown['en']}"
        out.append(q)
    return out


def gen_listening_p2(n=5):
    """Ascolta una frase -> scegli 1 immagine fra 3 (immagini distinte)."""
    out = []
    for _ in range(n):
        items = _distinct_image_items(sentence_for_concept, 3)  # 1 corretta + 2 distrattori
        opts = [_image_option(w, p, img) for (w, p, img) in items]
        correct_opt = opts[0]
        random.shuffle(opts)
        cw, s, _ = items[0]
        q = Question("listening", 2, "image", "instr_L2")
        q.audio_texts = [s["zh"]]
        q.options = opts
        q.correct = opts.index(correct_opt)
        q.review_zh, q.review_pinyin = s["zh"], pin(s["zh"])
        q.review_it, q.review_en = s["it"], s["en"]
        out.append(q)
    return out


def gen_listening_p3(n=5):
    """Abbinamento: ascolta un dialogo -> scegli l'immagine da un banco di 6 (A-F).

    Formato ufficiale HSK1: 6 immagini condivise per 5 domande (1 distrattore in piu').
    """
    items = _distinct_image_items(dialogue_for_concept, n + 1)  # 6 immagini distinte
    opts = [_image_option(w, p, img) for (w, p, img) in items]
    pool = opts[:]
    random.shuffle(pool)
    out = []
    for w, d, img in items[:n]:
        co = next(o for o in pool if o["image"] == img)
        q = Question("listening", 3, "image", "instr_L3")
        q.audio_texts = [t for t in (d.get("q"), d.get("a")) if t]
        q.options = pool
        q.correct = pool.index(co)
        q.review_zh = " ".join(t for t in (d.get("q"), d.get("a")) if t)
        q.review_pinyin = " ".join(pin(t) for t in (d.get("q"), d.get("a")) if t)
        q.review_it = d.get("it", "")
        q.review_en = d.get("en", "")
        out.append(q)
    return out


def num_mw(n: int) -> str:
    """Numero davanti a un classificatore: il 2 isolato diventa 两 (两个, 两点)."""
    return "两" if n == 2 else num2cn(n)


def _p4_time():
    h = random.randint(1, 12)
    o1, o2 = random.sample([x for x in range(1, 13) if x != h], 2)
    return (f"现在是{num_mw(h)}点。", "现在几点？",
            f"{num_mw(h)}点", [f"{num_mw(o1)}点", f"{num_mw(o2)}点"])


def _p4_age():
    ages = [16, 18, 19, 20, 21, 22, 25, 30]
    a, o1, o2 = random.sample(ages, 3)
    return (f"他今年{num2cn(a)}岁。", "他今年多大？",
            f"{num2cn(a)}岁", [f"{num2cn(o1)}岁", f"{num2cn(o2)}岁"])


def _p4_people():
    p, o1, o2 = random.sample(range(2, 8), 3)
    return (f"我家有{num_mw(p)}个人。", "他家有几个人？",
            f"{num_mw(p)}个", [f"{num_mw(o1)}个", f"{num_mw(o2)}个"])


def _p4_food():
    f = random.sample(_by_category("food"), 3)
    return (f"我喜欢吃{f[0]['hanzi']}。", "他喜欢吃什么？",
            f[0]["hanzi"], [f[1]["hanzi"], f[2]["hanzi"]])


def _p4_place():
    p = random.sample(_by_category("place"), 3)
    return (f"下午我去{p[0]['hanzi']}。", "他下午做什么？",
            f"去{p[0]['hanzi']}", [f"去{p[1]['hanzi']}", f"去{p[2]['hanzi']}"])


def _p4_possessive():
    obj = random.choice(["书", "电脑", "杯子", "电视"])
    owner, o1, o2 = random.sample(["我", "他", "同学", "妈妈"], 3)
    return (f"这是{owner}的{obj}。", f"那是谁的{obj}？",
            f"{owner}的", [f"{o1}的", f"{o2}的"])


def _p4_location():
    obj = random.choice(["猫", "狗", "书", "杯子"])
    locs = random.sample(["桌子上", "椅子上", "家里", "商店里"], 3)
    return (f"我的{obj}在{locs[0]}。", f"{obj}在哪儿？",
            locs[0], [locs[1], locs[2]])


def _p4_weather():
    states = random.sample([("今天很冷。", "很冷"), ("外面下雨了。", "下雨了"),
                            ("今天有点儿热。", "有点儿热"), ("今天天气很好。", "很好")], 3)
    return (states[0][0], "今天天气怎么样？",
            states[0][1], [states[1][1], states[2][1]])


def _p4_activity():
    acts = random.sample(["回家", "打电话", "看电视", "看电影", "买东西", "学习"], 3)
    return (f"下午我想{acts[0]}。", "他下午想做什么？",
            f"想{acts[0]}", [f"想{acts[1]}", f"想{acts[2]}"])


def _p4_description():
    states = random.sample([("我朋友很漂亮。", "很漂亮"), ("我朋友很高兴。", "很高兴"),
                            ("我朋友爱学习。", "爱学习"), ("我朋友很好。", "很好")], 3)
    return (states[0][0], "他朋友怎么样？",
            states[0][1], [states[1][1], states[2][1]])


def _p4_day():
    days = random.sample(["星期一", "星期二", "星期三", "星期四", "星期五", "星期六"], 3)
    return (f"我们{days[0]}去看电影。", "他们什么时候去看电影？",
            days[0], [days[1], days[2]])


# tipi a "frase piena" (risposte di 3+ caratteri, come la metà del foglio reale)
_P4_RICH = [_p4_possessive, _p4_location, _p4_weather, _p4_activity, _p4_description, _p4_place]
# tipi brevi (numeri/nomi/giorni), presenti anch'essi nel reale
_P4_SIMPLE = [_p4_time, _p4_age, _p4_people, _p4_food, _p4_day]


def gen_listening_p4(n=5):
    """Ascolta enunciato + domanda -> scegli la risposta (testo).

    Come nei fogli ufficiali: ~3 risposte a frase piena (possessivi, luoghi,
    stati, intenzioni, descrizioni) e ~2 brevi (numeri/nomi/giorni).
    """
    out = []
    n_rich = min(len(_P4_RICH), max(3, n - 2))
    builders = random.sample(_P4_RICH, n_rich) + random.sample(_P4_SIMPLE, max(0, n - n_rich))
    random.shuffle(builders)
    builders = builders[:n]
    for build in builders:
        stmt, ques, correct, dists = build()
        q = Question("listening", 4, "text", "instr_L4")
        correct_opt = _txt_opt(correct)
        opts, idx = _shuffle_with_correct([correct_opt] + [_txt_opt(d) for d in dists], correct_opt)
        q.audio_texts = [stmt, ques]
        q.options = opts
        q.correct = idx
        q.review_zh = f"{stmt} {ques}"
        q.review_pinyin = f"{pin(stmt)} {pin(ques)}"
        q.review_it = "Enunciato + domanda d'ascolto"
        q.review_en = "Listening statement + question"
        out.append(q)
    return out


# ---------------------------------------------------------------- LETTURA
def gen_reading_p1(n=5):
    """Immagine + parola -> Vero/Falso."""
    out = []
    words = random.sample(IMAGE_VOCAB, k=min(n * 2, len(IMAGE_VOCAB)))
    for i in range(n):
        w = words[i]
        match = random.random() < 0.5
        shown = w if match else \
            random.choice([x for x in IMAGE_VOCAB if _visual_key(x) != _visual_key(w)])
        q = Question("reading", 1, "tf", "instr_R1")
        q.display_image = shown["emoji"]
        q.display_image_path = word_scene(shown["hanzi"])
        q.display_zh = w["hanzi"]
        q.display_pinyin = w["pinyin"]
        q.options = [{"kind": "tf", "value": True}, {"kind": "tf", "value": False}]
        q.correct = 0 if match else 1
        q.review_zh, q.review_pinyin = w["hanzi"], w["pinyin"]
        q.review_it, q.review_en = w["it"], w["en"]
        out.append(q)
    return out


def gen_reading_p2(n=5):
    """Abbinamento: leggi la frase -> scegli l'immagine da un banco di 6 (A-F)."""
    items = _distinct_image_items(sentence_for_concept, n + 1)  # 6 immagini distinte
    opts = [_image_option(w, p, img) for (w, p, img) in items]
    pool = opts[:]
    random.shuffle(pool)
    out = []
    for w, s, img in items[:n]:
        co = next(o for o in pool if o["image"] == img)
        q = Question("reading", 2, "image", "instr_R2")
        q.display_zh, q.display_pinyin = s["zh"], pin(s["zh"])
        q.options = pool
        q.correct = pool.index(co)
        q.review_zh, q.review_pinyin = s["zh"], pin(s["zh"])
        q.review_it, q.review_en = s["it"], s["en"]
        out.append(q)
    return out


def gen_reading_p3(n=5):
    """Abbinamento: leggi la domanda -> scegli la risposta da un banco di 6 (A-F)."""
    dias = _pick_distinct(DIALOGUES, lambda d: d["a"], n)
    used = {d["a"] for d in dias}
    correct_opts = [_txt_opt(d["a"], d["a_it"], d["a_en"]) for d in dias]
    extra_d = random.choice([x for x in DIALOGUES if x["a"] not in used])
    pool = _matching_pool(correct_opts, _txt_opt(extra_d["a"], extra_d["a_it"], extra_d["a_en"]))
    out = []
    for d, co in zip(dias, correct_opts):
        q = Question("reading", 3, "text", "instr_R3")
        q.display_zh, q.display_pinyin = d["q"], pin(d["q"])
        q.options = pool
        q.correct = _idx(pool, co)
        q.review_zh = f"{d['q']} → {d['a']}"
        q.review_pinyin = f"{pin(d['q'])} → {pin(d['a'])}"
        q.review_it = f"{d['q_it']} — {d['a_it']}"
        q.review_en = f"{d['q_en']} — {d['a_en']}"
        out.append(q)
    return out


def gen_reading_p4(n=5):
    """Completa la frase con la parola mancante (banco di 6, A-F).

    Come nel foglio ufficiale, il banco mescola parole grammaticali (是/有/在,
    classificatori, particelle, modali, negazioni) e parole di CONTENUTO
    (名字, 汉语, 漂亮, 前面, 没关系...), in frasi anche composte o dialoghi.
    """
    # selezione bilanciata: ~3 item "ricchi" (contenuto/composte) + ~2 base, come il reale
    n_rich = min(len(GRAMMAR_RICH), max(2, n // 2 + 1))
    rich = _pick_distinct(GRAMMAR_RICH, lambda g: g["a"], n_rich)
    chosen_ans = {g["a"] for g in rich}
    rest = _pick_distinct([g for g in GRAMMAR_POOL if g["a"] not in chosen_ans],
                          lambda g: g["a"], n - len(rich))
    items = rich + rest
    random.shuffle(items)
    used = {g["a"] for g in items}
    correct_opts = [_txt_opt(g["a"]) for g in items]
    # distrattore extra: una parola grammaticale plausibile, diversa dalle 5 risposte
    extra_candidates = [w for g in items for w in g["d"] if w not in used]
    if not extra_candidates:
        extra_candidates = [g["a"] for g in GRAMMAR_POOL if g["a"] not in used]
    pool = _matching_pool(correct_opts, _txt_opt(random.choice(extra_candidates)))
    out = []
    for g, co in zip(items, correct_opts):
        full = g["q"].replace("（ ____ ）", g["a"])
        q = Question("reading", 4, "text", "instr_R4")
        q.display_zh = g["q"]
        q.display_pinyin = None  # niente pinyin: rivelerebbe la risposta
        q.options = pool
        q.correct = _idx(pool, co)
        q.review_zh, q.review_pinyin = full, pin(full)
        q.review_it, q.review_en = g["it"], g["en"]
        q.grammar_point = (g["pt_it"], g["pt_en"])
        out.append(q)
    return out


LISTENING_GENERATORS = [gen_listening_p1, gen_listening_p2, gen_listening_p3, gen_listening_p4]
READING_GENERATORS = [gen_reading_p1, gen_reading_p2, gen_reading_p3, gen_reading_p4]


# Esempi svolti (例如) all'inizio di ogni parte, come nel foglio d'esame ufficiale.
#   kind: "tf" (parola+immagine, risposta ✓/✗) | "image" (risposta = emoji) | "text"
EXAMPLES = {
    ("listening", 1): {"kind": "tf", "zh": "看电影", "emoji": "🎬", "answer": "✓"},
    ("listening", 2): {"kind": "image", "zh": "这是我的书。", "answer_emoji": "📕",
                       "answer_image": sentence_image("这是我的书。", "书")},
    ("listening", 3): {"kind": "image", "zh": "你好！很高兴认识你。", "answer_emoji": "🤝"},
    ("listening", 4): {"kind": "text", "zh": "下午我去商店。问：他下午去哪里？", "answer_zh": "商店"},
    ("reading", 1): {"kind": "tf", "zh": "飞机", "emoji": "✈️",
                     "image": word_scene("飞机"), "answer": "✓"},
    ("reading", 2): {"kind": "image", "zh": "我很喜欢这本书。", "answer_emoji": "📕",
                     "answer_image": sentence_image("这是我的书。", "书")},
    ("reading", 3): {"kind": "text", "zh": "你喝水吗？", "answer_zh": "好的，谢谢。"},
    ("reading", 4): {"kind": "text", "zh": "你叫什么（名字）？", "answer_zh": "名字"},
}
# aggiunge il pinyin a ogni esempio
for _e in EXAMPLES.values():
    _e["pinyin"] = pin(_e["zh"])
    if _e.get("answer_zh"):
        _e["answer_pinyin"] = pin(_e["answer_zh"])
