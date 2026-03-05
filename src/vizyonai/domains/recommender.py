import unicodedata
from collections import Counter

import pandas as pd
from rapidfuzz import fuzz, process

from vizyonai.domains.electronics.extractors import extract_port, extract_watt
from vizyonai.domains.electronics.intents import detect_intent
from vizyonai.domains.electronics.ranking import sort_by_closest_watt


def _norm_text(value: str) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _norm_port(value: str) -> str:
    s = _norm_text(value).replace(" ", "").replace("-", "").replace("_", "")
    if s in {"typec", "usbc", "usbtypec"}:
        return "usb-c"
    if "lightning" in s:
        return "lightning"
    if "microusb" in s or s == "micro":
        return "micro-usb"
    return s


def _pick_category(df: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    out = df.copy()
    out["kategori_norm"] = out["kategori"].astype(str).map(_norm_text)
    mask = out["kategori_norm"].apply(
        lambda value: any(keyword in value for keyword in keywords)
    )
    return out[mask]


def _match_phone_model(q: str, phones_df: pd.DataFrame) -> tuple[str | None, int]:
    if "model" not in phones_df.columns:
        return None, 0

    choices_raw = phones_df["model"].dropna().astype(str).tolist()
    if not choices_raw:
        return None, 0

    # Normalize hem sorguyu hem de aday modelleri ki
    # "Ultra / FE / Edge / +" gibi varyantlar daha isabetli eşleşsin.
    normalized_query = _norm_text(q)
    normalized_choices = [_norm_text(model) for model in choices_raw]

    # En iyi birkaç adayı alıp, sorgu içinde tam geçen en uzun model ismini
    # tercih ediyoruz. Böylece "Galaxy S25 Ultra" varken "Galaxy S25"
    # seçilme olasılığı azalır.
    candidates = process.extract(
        normalized_query,
        normalized_choices,
        scorer=fuzz.WRatio,
        limit=5,
    )

    if not candidates:
        return None, 0

    # normalized -> orijinal model eşlemesi
    norm_to_raw = {norm: raw for norm, raw in zip(normalized_choices, choices_raw)}

    # Önce sorgu içinde tam alt dize olan modelleri bul.
    substring_candidates: list[tuple[str, int]] = []
    for norm_model, score, _ in candidates:
        if norm_model in normalized_query:
            substring_candidates.append((norm_model, int(score)))

    # Varsa, en uzun modeli (varyant adı içeren) seç.
    if substring_candidates:
        norm_model, score = max(
            substring_candidates, key=lambda item: (len(item[0]), item[1])
        )
        return norm_to_raw[norm_model], score

    # Aksi halde RapidFuzz'un en iyi adayını kullan.
    best_norm, score, _ = max(candidates, key=lambda item: item[1])
    return norm_to_raw[best_norm], int(score)


def _infer_phone_specs_from_query(q: str) -> dict | None:
    normalized = _norm_text(q)
    tokens = [token for token in normalized.replace("/", " ").split() if token]

    def has_keyword(*keywords: str, threshold: int = 80) -> bool:
        for token in tokens:
            for keyword in keywords:
                if fuzz.ratio(token, keyword) >= threshold:
                    return True
        return False

    if has_keyword("iphone"):
        port = "USB-C" if any(str(n) in normalized for n in range(15, 100)) else "Lightning"
        return {"model": "inferred-iphone", "charge_port": port, "max_watt": 20}

    if has_keyword("galaxy", "samsung") or has_keyword("s24", "s23", "s22", "s21"):
        watt = 45 if any(tag in normalized for tag in ["ultra", "+", "plus"]) else 25
        return {"model": "inferred-galaxy", "charge_port": "Type-C", "max_watt": watt}

    return None


def _pick_products_for_charger(
    products_df: pd.DataFrame,
    phone_row: dict | None,
    requested_watt: int | None,
    requested_port: str | None,
) -> list[dict]:
    df = _pick_category(products_df, ["sarj", "charger", "adapter"])
    if df.empty:
        return []

    port_target = requested_port or (
        str(phone_row.get("charge_port", "")) if phone_row else None
    )
    if port_target:
        df["port_norm"] = df["port"].astype(str).map(_norm_port)
        df = df[df["port_norm"] == _norm_port(port_target)]

    if df.empty:
        return []

    watt_target = requested_watt
    if watt_target is None and phone_row:
        try:
            watt_target = int(float(phone_row.get("max_watt")))
        except (TypeError, ValueError):
            watt_target = None

    if watt_target is not None:
        df = df.copy()
        df["watt_num"] = pd.to_numeric(df["watt"], errors="coerce")
        exact_watt = df[df["watt_num"] == int(watt_target)]
        if not exact_watt.empty:
            return exact_watt.head(2).to_dict(orient="records")

        # If port filtering removed all exact matches, keep same watt as strict rule.
        fallback_all = _pick_category(products_df, ["sarj", "charger", "adapter"]).copy()
        fallback_all["watt_num"] = pd.to_numeric(fallback_all["watt"], errors="coerce")
        fallback_exact = fallback_all[fallback_all["watt_num"] == int(watt_target)]
        if not fallback_exact.empty:
            return fallback_exact.head(2).to_dict(orient="records")

        df = sort_by_closest_watt(df, watt_target)
    else:
        df = df.copy()
        df["watt_num"] = pd.to_numeric(df["watt"], errors="coerce").fillna(0)
        df = df.sort_values("watt_num", ascending=False)

    return df.head(2).to_dict(orient="records")


def _pick_products_generic(products_df: pd.DataFrame, intent: str) -> list[dict]:
    intent_keywords = {
        "cable": ["kablo", "cable"],
        "camera": ["kamera", "camera", "cam"],
        "massage": ["masaj", "massage"],
    }

    keywords = intent_keywords.get(intent)
    if not keywords:
        return []

    return _pick_category(products_df, keywords).head(2).to_dict(orient="records")


def recommend(q: str, products_df: pd.DataFrame, phones_df: pd.DataFrame) -> dict:
    intent = detect_intent(q)
    requested_watt = extract_watt(q)
    requested_port = extract_port(q)

    phone_model, score = _match_phone_model(q, phones_df)
    phone_row = None
    if phone_model and score >= 80:
        phone_row = phones_df[phones_df["model"] == phone_model].iloc[0].to_dict()
    elif intent == "charger":
        phone_row = _infer_phone_specs_from_query(q)

    if intent == "charger":
        products = _pick_products_for_charger(
            products_df=products_df,
            phone_row=phone_row,
            requested_watt=requested_watt,
            requested_port=requested_port,
        )
    else:
        products = _pick_products_generic(products_df, intent)

    return {
        "intent": intent,
        "phone_model": phone_model,
        "match_score": score,
        "phone_row": phone_row,
        "requested_watt": requested_watt,
        "requested_port": requested_port,
        "products": products,
    }
