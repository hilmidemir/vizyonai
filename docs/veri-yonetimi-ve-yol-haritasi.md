# VizyonAI — Veri Yönetimi ve Yol Haritası

Bu doküman; veri modeli, entegrasyonlar, RAG stratejisi, tazelik/yönetim politikaları ve uygulama yol haritasını tanımlar. Karar gerektiren başlıklar “Karar Gerekiyor” ile işaretlenmiştir.

---

## 1. Kapsam ve Hedefler

- Doğru ürün eşleştirme ve alternatif öneri için gereken veri varlıklarının (stok, fiyat, uyumluluk, cihaz özellikleri) düzenlenmesi.
- Deterministik veritabanı sorguları ile semantik aramanın (RAG) hibrit çalışması.
- Kolay bakım, düşük operasyon maliyeti, veri tazeliği garanti.

---

## 2. Veri Kaynakları ve Sahiplik

- MSSQL (Vega) — Kaynak sistem, tekil doğruluk noktası (SoT):
  - Stok kartları (SKU, açıklama, grup, marka, model, teknik özellik etiketleri)
  - Fiyatlar (SatisFiyat1–4; toptan/perakende)
  - Stok miktarları, depo bilgileri
- Dosya Kaynakları (Excel/CSV):
  - KIRILMAZCAMLAR uyumluluk listesi (mevcut Excel) [Karar Gerekiyor: sütun düzeni]
  - Telefon teknik özellikleri (şarj tipi, watt, hızlı şarj standardı) — başlangıçta CSV/Excel
- Vektör Veritabanı (ChromaDB):
  - Teknik bilgi notları, eşleştirme kuralları ve SSS içerikleri (semantik arama için)

Sahiplik:
- Operasyon: MSSQL/Vega ekipleri
- Veri Hazırlık: AI projesi veri sorumlusu
- Uygulama: Backend ekibi (ETL, senkronizasyon script’leri)

---

## 3. Mantıksal Veri Modeli

Varlıklar:
- Product (SKU): sku_code, name, category, brand, attrs (key:val), price_tiers {1..4}, stock_qty
- DeviceModel: brand, model, charge_port, fast_charge_std (PD/QC/VOOC…), notes
- Compatibility: device_model_id, accessory_sku, compatibility_type (native/alt), confidence
- PricePolicy: sku_code, tier (1..4), description (ör. perakende/toptan), is_default

Örnek Eşleme Notları:
- SG47 → {power_w: 25W, cable: "Type-C ↔ Type-C", protocol: PD}
- SG46 → {power_w: 20W, cable: "Lightning ↔ Type-C", protocol: PD}
- KIRILMAZCAMLAR → tek SKU; model bazlı uygunluk Compatibility tablosunda tutulur.

Fiziksel Şema Önerileri:
- MSSQL (read-only görünüm): vw_products, vw_prices, vw_stock, vw_attributes, vw_compatibility
- CSV/Excel: device_models.csv, glass_compatibility.csv

---

## 4. Veri Standartları ve Sözlük

- charge_port: {USB-C, Lightning, Micro-USB}
- fast_charge_std: {USB-PD, QC, SCP, VOOC, PPS}
- power_w: tamsayı (örn. 25)
- cable_type: {C↔C, C↔Lightning, A↔C, A↔Lightning}
- compatibility_type: {native, alternative}

Adlandırma:
- sku_code: büyük harf (örn. SG47)
- device key: brand|model (örn. SAMSUNG|S10 PLUS)

---

## 5. RAG ve Arama Stratejisi

Hibrit yaklaşım:
1) Deterministik aramalar (MSSQL/CSV): sku, stok, fiyat, kesin uyumluluk.
2) RAG (ChromaDB): belirsiz istekler, özellik açıklamaları, marka/model varyant eşleme, satış konuşması ve SSS.

Embedding ve İndeksleme:
- Türkçe + teknik terimler için çok dilli bir gömme modeli (örn. bge-m3 ya da minilm-embedding) [Karar Gerekiyor: model seçimi]
- Chunking: 512–800 karakter; overlap 50–100
- Koleksiyonlar: device_specs, compatibility_notes, sales_scripts, faq

Geri Getirme:
- K = 4–8 belge; mmr veya cosine similarity; minimum skor eşiği 0.25–0.35
- Tazelik etiketi (version, updated_at) ile yanıt tarafında kanıt listesi döndürme

---

## 6. Entegrasyonlar

- MSSQL (Vega): ODBC/TDS üzerinden read-only kullanıcı.
  - Örnek görünümler:
    - vw_products(sku_code, name, brand, category, attrs_json)
    - vw_prices(sku_code, price1, price2, price3, price4)
    - vw_stock(sku_code, qty, depot)
- Dosya → CSV Dönüşümü: Excel (KIRILMAZCAMLAR, device specs) günlük/haftalık otomasyon.
- ChromaDB: dosyalardan ve SQL’den üretilen bilgi notlarının gömülmesi.

---

## 7. Veri Tazeliği ve Senkronizasyon

- MSSQL: anlık okuma (her sorguda canlı).
- Excel/CSV: planlı içe-aktarım (örn. her gece 02:00), manuel tetikleme opsiyonu.
- ChromaDB: yeniden-gömme politikası — değişen belgeler için delta tabanlı güncelleme; tam indeks haftalık.

Sürümleme:
- Koleksiyon adlarında sürüm (device_specs_v1) ve metadata’da commit_id tutma.

---

## 8. Kalite Güvencesi ve Veri Doğrulama

- Şema doğrulama: CSV kolonları ve tipleri pydantic ile doğrulanır.
- İş Kuralları:
  - charge_port ve cable_type uyum kontrolü (örn. cihaz Lightning ise C↔Lightning/Lightning↔C aksesuarları).
  - power_w eşik kontrolü (cihaz ihtiyacı ≤ adaptör gücü; üst sınır bilgilendirme).
  - fiyat katmanı seçim kuralı (perakende: price3 varsayılan).
- Test Seti: 50+ gerçek soru; isabet, gecikme ve alternatif kalitesi ölçümü.

---

## 9. Güvenlik, Yetkilendirme ve Gizlilik

- Read-only DB kullanıcıları; yalnızca gerekli şema/görünümler.
- Loglarda PII yok; sadece teknik metrikler.
- Dosya paylaşımlarında salt-okunur izinler; sürücü harfi yerine UNC path kullanımı.

---

## 10. Yol Haritası (Fazlar ve Çıkış Kriterleri)

Faz 1 — Kurulum ve İskelet (2 hafta)
- Python ortamı, LM Studio, Qwen model kurulumu
- Basit akış: sor → niyet/varlık çıkar → MSSQL’den stok/fiyat → kısa cevap
- Çıkış Kriterleri: p95 < 5 sn; temel stok/fiyat doğru %95; sağlık uçları aktif

Faz 2 — Veri Hazırlığı ve RAG (2–3 hafta)
- Device specs ve KIRILMAZCAMLAR Excel → CSV normalizasyonu
- ChromaDB koleksiyonlarının oluşturulması ve ilk gömme
- Çıkış Kriterleri: belirsiz isteklerde doğru yönlendirme %85+; alternatif öneri anlamlı

Faz 3 — Gelişmiş Eşleştirme ve Kurallar (2 hafta)
- power_w, cable_type, protocol kurallarının uygulanması; uyumsuzluk uyarıları
- Fiyat katmanı mantığı ve kampanya kuralları (opsiyonel)
- Çıkış Kriterleri: otomatize 50+ testin %90+ başarı; kullanıcı geri bildirimi pozitif

Faz 4 — UI İyileştirme ve Pilot (1–2 hafta)
- Streamlit kiosk, sesli giriş (opsiyonel), kısa kart görünümleri
- Pilot mağazada saha testi; log analizi ve iyileştirme döngüsü
- Çıkış Kriterleri: Operasyon el kitabı tamam, eğitim 1 saatten az, sorun bildirimleri kritik değil

---

## 11. Operasyon ve Bakım

- Günlük/haftalık içe-aktarım görevleri (Task Scheduler)
- Log rotasyonu, metrik raporu, kapasite izleme
- Şema/değişiklik yönetimi: değişiklik setleri ve sürüm notları

---

## 12. Açık Kararlar (Karar Gerekiyor)

1) Embedding modeli seçimi (bge-m3, minilm-embedding vb.)
2) KIRILMAZCAMLAR Excel kolon şeması ve dönüştürme kuralları
3) Backend ayrışması (Streamlit + arka servis mi, ayrı FastAPI mi)
4) Tam çevrimdışı gereksinimi ve paketleme (model + embeddings)
5) MSSQL görünüm isimleri ve erişim rolleri

---

## 13. Ekler

- Örnek CSV Şemaları:
  - device_models.csv: brand,model,charge_port,fast_charge_std,power_w,notes
  - glass_compatibility.csv: brand,model,sku_code,compatibility_type,confidence
- Test Soru Seti İskelesi: questions.csv (question, expected_intent, expected_answer_contains)
