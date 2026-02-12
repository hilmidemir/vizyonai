import unicodedata

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

    choices = phones_df["model"].dropna().astype(str).tolist()
    if not choices:
        return None, 0

    best = process.extractOne(q, choices, scorer=fuzz.WRatio)
    if not best:
        return None, 0

    model, score, _ = best
    return model, int(score)


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
    if phone_model and score >= 70:
        phone_row = phones_df[phones_df["model"] == phone_model].iloc[0].to_dict()

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
