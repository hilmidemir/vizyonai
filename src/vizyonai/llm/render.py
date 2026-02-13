from openai import APIConnectionError, APIStatusError

from vizyonai.config.settings import LMSTUDIO_MODEL
from vizyonai.llm.prompts import SYSTEM_PROMPT


def _fallback_answer(picked: list[dict], reason: str | None = None) -> str:
    if not picked:
        return (
            "Öneri: Uygun ürün bulamadım. Modeli biraz daha net yazar mısın?\n"
            "Alternatif: Cihazın şarj giriş tipini (USB-C/Lightning) yazarsan hızlı öneririm."
        )

    p1 = picked[0]
    p2 = picked[1] if len(picked) > 1 else None

    line1 = (
        f"Öneri: {p1.get('stok_kodu')} - {p1.get('urun_adi')} "
        f"({p1.get('watt')}W, {p1.get('port')}) ihtiyaca en yakın seçenek."
    )

    if p2:
        line2 = (
            f"Alternatif: {p2.get('stok_kodu')} - {p2.get('urun_adi')} "
            f"({p2.get('watt')}W, {p2.get('port')}) benzer ihtiyaç için ikinci seçenek."
        )
    else:
        line2 = "Alternatif: İkinci uygun ürün bulunamadı, farklı filtre ile tekrar bakabilirim."

    if reason:
        line2 = f"{line2} (LLM: {reason})"

    return f"{line1}\n{line2}"


def format_answer(client, user_q: str, picked: list[dict]) -> str:
    if not picked:
        return _fallback_answer(picked)

    p1 = picked[0]
    p2 = picked[1] if len(picked) > 1 else None

    context = f"""KULLANICI SORUSU: {user_q}

SECILEN URUNLER:
1) Stok:{p1.get("stok_kodu")} | Ad:{p1.get("urun_adi")} | {p1.get("watt")}W | Port:{p1.get("port")} | Kablo:{p1.get("kablo")} | Hizli:{p1.get("hizli_sarj")} | Fiyat:{p1.get("satis_fiyat", p1.get("fiyat4"))}$
"""
    if p2:
        context += f"""2) Stok:{p2.get("stok_kodu")} | Ad:{p2.get("urun_adi")} | {p2.get("watt")}W | Port:{p2.get("port")} | Kablo:{p2.get("kablo")} | Hizli:{p2.get("hizli_sarj")} | Fiyat:{p2.get("satis_fiyat", p2.get("fiyat4"))}$
"""

    try:
        resp = client.chat.completions.create(
            model=LMSTUDIO_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.2,
            max_tokens=180,
        )
        content = resp.choices[0].message.content
        if not content:
            return _fallback_answer(picked, reason="boş yanıt")
        return content.strip()
    except APIConnectionError:
        return _fallback_answer(picked, reason="bağlantı yok")
    except APIStatusError as exc:
        return _fallback_answer(picked, reason=f"api hata {exc.status_code}")
    except Exception:
        return _fallback_answer(picked, reason="beklenmeyen hata")
