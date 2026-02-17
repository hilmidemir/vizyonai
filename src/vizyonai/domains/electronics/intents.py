import unicodedata


INTENT_KEYWORDS = {
    "charger": ["şarj", "adaptör", "adapter", "charger", "başlık", "şarj cihazı"],
    "cable": ["kablo", "cable", "type-c to", "lightning to", "kordon"],
    "camera": ["kamera", "cam", "dslr", "aksiyon kamera", "action cam"],
    "massage": ["masaj", "massage", "boyun masaj", "masaj aleti"],
}


def _norm_text(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def detect_intent(q: str) -> str:
    t = _norm_text(q)
    for intent, kws in INTENT_KEYWORDS.items():
        if any(_norm_text(keyword) in t for keyword in kws):
            return intent
    return "unknown"
