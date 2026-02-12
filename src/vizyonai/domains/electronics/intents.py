INTENT_KEYWORDS = {
    "charger": ["şarj", "adaptör", "adapter", "charger", "başlık", "şarj cihazı"],
    "cable": ["kablo", "cable", "type-c to", "lightning to", "kordon"],
    "camera": ["kamera", "cam", "dslr", "aksiyon kamera", "action cam"],
    "massage": ["masaj", "massage", "boyun masaj", "masaj aleti"],
}

def detect_intent(q: str) -> str:
    t = q.lower()
    for intent, kws in INTENT_KEYWORDS.items():
        if any(k in t for k in kws):
            return intent
    return "unknown"
