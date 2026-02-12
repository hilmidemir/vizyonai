import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key="lm-studio"
)
MODEL = os.getenv("LMSTUDIO_MODEL", "qwen3-8b")

# ✅ CSV yolu (gerekirse değiştir)
CSV_PATH = "data/products.csv"

df = pd.read_csv(CSV_PATH)

# ✅ Senin dosyana göre perakende fiyat kolonu: satis_fiyat
# Yine de sağlam olsun diye alternatif isimleri de kontrol ediyoruz.
price_candidates = ["satis_fiyat", "fiyat3", "perakende_fiyat", "fiyat"]
price_col = next((c for c in price_candidates if c in df.columns), None)

if price_col is None:
    raise ValueError(f"Fiyat kolonu bulunamadı. Mevcut kolonlar: {df.columns.tolist()}")

# Envanteri modele kısa "kart" olarak veriyoruz
product_cards = "\n".join(
    f"- {r.stok_kodu} | {r.urun_adi} | {r.kategori} | {r.watt}W | Port:{r.port} | Kablo:{r.kablo} | Hızlı:{r.hizli_sarj} | Toptan:{r.toptan_fiyat}$ | Perakende:{getattr(r, price_col)}$"
    for r in df.itertuples(index=False)
)

SYSTEM = f"""Sen mağaza içi satış destek asistanısın.

Sıkı kurallar:
- SADECE aşağıdaki ENVANTERDE olan stok kodlarını önerebilirsin.
- "Orijinal", "resmi" gibi iddialar yok.
- Cevap TAM 2 satır olacak: 1 öneri + 1 alternatif.
- Her satırda ürün için 1-2 cümlelik kısa açıklama yaz: 
  * Kullanıcıya faydayı anlat (ör: hızlı şarj, uyumluluk, kullanım kolaylığı).
  * Özellikleri madde madde sayma. (Watt, port, kablo gibi detayları tek cümlede doğal geçir.)
- Fiyatı en sona koy.

ÇIKTI FORMATI (tam böyle):
Öneri: <stok_kodu> - <1-2 cümle açıklama> - Fiyat: <perakende>$
Alternatif: <stok_kodu> - <1-2 cümle açıklama> - Fiyat: <perakende>$

ENVANTER:
{product_cards}
"""

user_q = "Samsung S10 Plus için şarj cihazı istiyorum."

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_q}
    ],
    temperature=0.1,
    max_tokens=160
)

print(resp.choices[0].message.content)
