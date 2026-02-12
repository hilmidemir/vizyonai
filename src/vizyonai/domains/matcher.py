import pandas as pd
from rapidfuzz import process, fuzz

INTENT_KEYWORDS = {
    "charger": ["şarj", "adaptör", "adapter", "charger", "başlık", "şarj cihazı"],
    "cable": ["kablo", "cable", "type-c to", "lightning to"],
    "glass": ["cam", "kırılmaz", "ekran koruyucu", "screen protector"],
    "case": ["kılıf", "case", "kap"],
}

def detect_intent(q: str) -> str:
    t = q.lower()
    for intent, kws in INTENT_KEYWORDS.items():
        if any(k in t for k in kws):
            return intent
    return "unknown"

def load_data():
    products = pd.read_csv("data/products.csv")
    phones = pd.read_csv("data/phone_specs.csv")
    return products, phones

def match_phone_model(q: str, phones_df: pd.DataFrame):
    # Telefon modeli listesi
    choices = phones_df["model"].dropna().tolist()
    if not choices:
        return None, 0

    # En yakın eşleşme
    best = process.extractOne(q, choices, scorer=fuzz.WRatio)
    if not best:
        return None, 0
    model, score, _ = best
    return model, score

def normalize_port(x: str) -> str:
    s = str(x).lower().strip()
    s = s.replace(" ", "").replace("-", "").replace("_", "")
    if s in ["typec", "usbc", "usbtypec", "usb c", "usb-c"]:
        return "usb-c"
    if "lightning" in s:
        return "lightning"
    if "microusb" in s or "micro" in s:
        return "micro-usb"
    return s

def pick_products_for_charger(products_df: pd.DataFrame, phone_row: dict):
    # Port uyumu: USB-C / Lightning
    port = str(phone_row["charge_port"]).strip()
    max_watt = float(phone_row["max_watt"]) if str(phone_row["max_watt"]).strip() != "" else 999

    df = products_df.copy()

    # kategori şarj
    df = df[df["kategori"].astype(str).str.lower().str.contains("şarj")]

    # port uyumu (ürün port alanını senin CSV’de nasıl tuttuğuna göre)
    # örn: products.csv'de port = "USB-C" veya "Lightning"
    port_norm = normalize_port(port)
    df["port_norm"] = df["port"].astype(str).apply(normalize_port)
    df = df[df["port_norm"] == port_norm]


    # watt <= max_watt (eğer ürün watt sayısal değilse hata vermesin)
    df["watt_num"] = pd.to_numeric(df["watt"], errors="coerce")
    df["watt_num"] = pd.to_numeric(df["watt"], errors="coerce").fillna(0)

    # max_watt'a en yakın olanı seç, ama mümkünse >= max_watt tercih et
    df["under"] = df["watt_num"] < max_watt
    df["diff"] = (df["watt_num"] - max_watt).abs()
    df = df.sort_values(["under", "diff", "watt_num"], ascending=[True, True, True])


    top = df.head(2)
    return top.to_dict(orient="records")

def pick_products_generic(products_df: pd.DataFrame, intent: str):
    df = products_df.copy()
    if intent == "cable":
        df = df[df["kategori"].astype(str).str.lower().str.contains("kablo")]
    elif intent == "glass":
        df = df[df["kategori"].astype(str).str.lower().str.contains("cam")]
    elif intent == "case":
        df = df[df["kategori"].astype(str).str.lower().str.contains("kılıf")]
    else:
        df = df.head(0)

    top = df.head(2)
    return top.to_dict(orient="records")

# matcher.py
def recommend(q: str, products_df, phones_df):
    intent = detect_intent(q)

    phone_model, score = match_phone_model(q, phones_df)
    phone_row = None
    if phone_model and score >= 70:
        phone_row = phones_df[phones_df["model"] == phone_model].iloc[0].to_dict()

    if intent == "charger" and phone_row:
        recs = pick_products_for_charger(products_df, phone_row)
    else:
        recs = pick_products_generic(products_df, intent)

    return {
        "intent": intent,
        "phone_model": phone_model,
        "match_score": score,
        "phone_row": phone_row,
        "products": recs
    }
