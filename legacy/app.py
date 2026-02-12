import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.vizyonai.domain.matcher import load_data, recommend  # recommend(q, products_df, phones_df) olacak

load_dotenv()

# --- LLM client (1 kere) ---
client = OpenAI(
    base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key="lm-studio"
)

MODEL = os.getenv("LMSTUDIO_MODEL", "qwen3-8b")

# --- Data (1 kere, cache) ---
@st.cache_data(show_spinner=False)
def get_data():
    return load_data()

products_df, phones_df = get_data()  # ✅ sadece bir kere yüklenir (cache)

# (opsiyonel) CSV güncelledikten sonra yenilemek için
with st.sidebar:
    if st.button("Verileri Yenile"):
        st.cache_data.clear()
        products_df, phones_df = get_data()
        st.success("Veriler yenilendi ✅")

SYSTEM = """Sen mağaza içi satış destek asistanısın.
Kurallar:
- Sadece verilen ürünlerden bahset.
- Cevap TAM 2 satır:
  Öneri: ...
  Alternatif: ...
- Her satırda 1-2 cümle ile faydayı anlat. Özellikleri madde madde sayma ama stok kodunu ver.
- 'Orijinal' gibi iddialar yok.
- 'stokta var/yok' gibi iddialar yok.
"""

def llm_format_answer(user_q: str, picked: list):
    if len(picked) == 0:
        return (
            "Öneri: Uygun ürün bulamadım. Modeli biraz daha net yazar mısın?\n"
            "Alternatif: Cihazın şarj giriş tipini (USB-C/Lightning) söylersen hızlı öneririm."
        )

    p1 = picked[0]
    p2 = picked[1] if len(picked) > 1 else None

    context = f"""KULLANICI SORUSU: {user_q}

SEÇİLEN ÜRÜNLER:
1) Stok:{p1.get("stok_kodu")} | Ad:{p1.get("urun_adi")} | {p1.get("watt")}W | Port:{p1.get("port")} | Kablo:{p1.get("kablo")} | Hızlı:{p1.get("hizli_sarj")} | Fiyat:{p1.get("satis_fiyat", p1.get("fiyat4"))}$
"""
    if p2:
        context += f"""2) Stok:{p2.get("stok_kodu")} | Ad:{p2.get("urun_adi")} | {p2.get("watt")}W | Port:{p2.get("port")} | Kablo:{p2.get("kablo")} | Hızlı:{p2.get("hizli_sarj")} | Fiyat:{p2.get("satis_fiyat", p2.get("fiyat4"))}$
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": context}
        ],
        temperature=0.2,
        max_tokens=180
    )
    return resp.choices[0].message.content


# --- UI ---
st.set_page_config(page_title="VizyonAI - Faz 2", layout="centered")
st.title("VizyonAI (Faz 2 - Local Veri + Eşleştirme)")

q = st.text_input("Soru", placeholder="Örn: Samsung S10 Plus için şarj cihazı istiyorum")

if st.button("Sor"):
    if not q.strip():
        st.warning("Bir soru yaz.")
    else:
        # ✅ doğru çağrı: df parametreli
        r = recommend(q.strip(), products_df, phones_df)
        picked = r.get("products", [])

        with st.expander("Debug (şimdilik)"):
            st.write(r)

        with st.spinner("Yanıt hazırlanıyor..."):
            answer = llm_format_answer(q.strip(), picked)

        st.subheader("Yanıt")
        st.write(answer)
