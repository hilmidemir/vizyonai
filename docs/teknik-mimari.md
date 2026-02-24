# VizyonAI — Teknik Mimari

Bu doküman; sistemin mimarisi, bileşenleri, dağıtım topolojisi, güvenlik, izleme/işletme ve performans hedeflerini tanımlar. Karar gerektiren başlıklar “Karar Gerekiyor” ibaresiyle işaretlenmiştir.

---

## 1. Mimari Amaç ve Varsayımlar

- Amaç: Mağaza personeline doğru ürün eşleştirme ve alternatif öneri sunan, LAN üzerinde çalışan, dış bağımlılığı en aza indirilmiş bir yapay zekâ destekli asistan sağlamak.
- Varsayımlar:
  - Ortam: Windows 
  - Veri Kaynağı: Vega muhasebe programı (MSSQL 2014) salt-okunur erişim ile.
  - Model: Yerel LLM servisinde barındırılan Qwen 3 8B 
  - UI: Tek mağaza içi PC’den tarayıcı ile erişim (Streamlit kiosk tarzı kullanım).
  - Entegrasyon: RAG (ChromaDB) + deterministik MSSQL sorguları ile hibrit yaklaşım.

---

## 2. Yüksek Seviye Bileşenler

- Kullanıcı Arayüzü (UI): Streamlit
  - Metin ve (opsiyonel) ses girişli soru-cevap
  - Rol/kiosk modu, kısaltılmış yanıtlar ve öneri kartları
- Orkestrasyon ve Backend: Python
  - LangChain tabanlı zincirler, araç/fonksiyon çağrıları (tool calling)
  - İş kuralları: stok-fiyat, uyumluluk eşleştirme, alternatif üretme
  - MSSQL ve ChromaDB entegrasyonu
- LLM Servisi (Inference): LM Studio üzerinde Qwen 3 8B
  - Yerel HTTP API ile entegrasyon
  - Prompt şablonları ve sistem yönergeleri
- Veri Katmanı:
  - MSSQL (Vega): stok, fiyat, ürün temel alanları (read-only)
  - ChromaDB (vektör veritabanı): telefon teknik özellikleri, eşleştirme kuralları, SSS
  - Dosya Kaynakları: Excel/CSV (ör. KIRILMAZCAMLAR uyumluluk matrisi)

---

## 3. Dağıtım Topolojisi (On-Prem, LAN)

- Windows Server 2019 üzerinde aşağıdaki servisler:
  1) LM Studio: Qwen modelini servis eder (localhost:port)
  2) Python Backend: FastAPI/uvicorn ya da Streamlit’in arka plan servisi [Karar Gerekiyor]
  3) ChromaDB: Gömülü (lokal klasör) veya servis modunda [Karar Gerekiyor]
  4) Streamlit UI: LAN içinde tek bir URL üzerinden erişim
- Ağ: UI makineleri → Backend → (LM Studio + MSSQL + ChromaDB)
- Kimlik: LAN içi erişim kısıtlamaları, Windows Firewall kuralları

Metinsel Diyagram (özet):

[Personel PC] → (HTTP) → [Streamlit UI] → (HTTP/Local) → [Python Backend]
  → (HTTP) → [LM Studio/Qwen]
  → (ODBC/TDS) → [MSSQL (Vega)]
  → (local FS/HTTP) → [ChromaDB]

---

## 4. Güvenlik ve Erişim

- Erişim Modeli:
  - UI ve Backend sadece LAN’dan erişilebilir.
  - Backend → MSSQL: read-only kullanıcı ile bağlanır.
  - LM Studio API yalnızca localhost veya sunucu iç IP aralığına bind edilir.
- Kimlik Bilgileri ve Sırlar:
  - MSSQL bağlantı dizesi Windows Credential Manager veya .env (NTFS izinli) dosyasında saklanır.
  - Kaynak dosyalar (Excel/CSV) paylaşımlı klasörlerde salt-okunur paylaştırılır.
- Ağ ve Güvenlik Duvarı:
  - Gerekli portlar (ör. Streamlit: 8501, Backend: 8000-8080, LM Studio: 1234 örnek) whitelist edilir.
  - Dışarıya açık port yok; model/bağımlılık indirmeleri için geçici outbound kuralı (gerekirse).
- Kayıtlar ve PII:
  - Sorgu/cevap log’larında müşteri PII saklanmaz. Yalnızca teknik izleme ve anonimleştirilmiş metrikler tutulur.

---

## 5. İzleme, Gözlemlenebilirlik ve Günlükleme

- Uygulama Log’ları: JSON satır log (zaman damgası, istek ID, kullanıcı oturumu, gecikme, hata kodu)
- Sağlık Kontrolleri: /health endpoint’i (LLM, MSSQL, ChromaDB bağımlılık kontrolleri)
- Metrikler: istek başına gecikme p50/p95, LLM token kullanımı, öneri isabet oranı, hata oranı
- Alarm/İşletme: Windows Event Viewer entegrasyonu ve periyodik rapor (CSV/Email intranet)

---

## 6. Performans Hedefleri ve Boyutlandırma

- Hedef Gecikme (ortalama):
  - Basit stok/fiyat sorguları: < 1.5 sn
  - Karma öneri (LLM + DB): < 3 sn (p95 < 5 sn)
- Boyutlandırma Önerileri [Karar Gerekiyor]:
  - GPU mevcutsa: Qwen 3 8B Instruct (int4/int8), 8–16 GB VRAM önerilir.
  - CPU-only durumda: int4 quant, 4–8 vCPU, 16–32 GB RAM; maksimum eşzamanlılık 1–3 oturum.
- LM Parametreleri (başlangıç):
  - max_tokens: 512–768, temperature: 0.2–0.4, top_p: 0.95, stop dizileri: prompt şablonuna göre

---

## 7. Uygulama Sözleşmeleri ve API Sınırları

- Giriş (UI → Backend):
  - request_id, user_id (opsiyonel), query_text, language (tr), context_flags ("kısa_cevap", "alternatif_öner"), channel (text/voice)
- İş Akışı (Backend):
  1) Niyet/varlık çıkarımı (intents, extractors)
  2) Deterministik aramalar: MSSQL stok/fiyat, uyumluluk tabloları
  3) Bilgi boşluğu varsa: RAG üzerinden bağlamsal arama (ChromaDB)
  4) Cevap üretimi ve kural tabanlı özetleme (kısa, net, alternatifli)
- Çıkış (Backend → UI):
  - answer_text, alternatives[], evidence[], latency_ms, trace_id

---

## 8. Promptlama ve Fonksiyon Çağrıları

- Sistem Prompt Prensipleri:
  - Kısa, eylem odaklı cevaplar; net ürün/adet/fiyat bilgisini vurgula.
  - Uygunluk kanıtı (ör. “25W, Type-C to Type-C, cihaz X ile uyumlu”).
  - Alternatif üret: stok yoksa uyumlu modeller/markalar öner.
- Fonksiyon Çağrıları (örnek):
  - get_stock_price(sku|model) → MSSQL
  - find_compatible_accessories(device_model) → MSSQL/Excel
  - semantic_lookup(query) → ChromaDB

---

## 9. Veri Yaşam Döngüsü ve Tazelik

- MSSQL verileri: anlık okuma (read-only), fiyat ve stok gerçek zamanlı.
- Excel/CSV (ör. KIRILMAZCAMLAR): günlük/haftalık içe-aktarım; normalize şema ile ChromaDB’ye bilgi notları olarak gömme.
- ChromaDB: gömü güncelleme politikası (ör. günlük cron), versiyonlu koleksiyonlar (v1, v2) ile geri dönüş kolaylığı.

---

## 10. Güvenilirlik, Yedekleme ve Geri Dönüş (DR)

- Yedekleme:
  - ChromaDB veri klasörü düzenli yedeklenir (günlük snapshot + haftalık offsite intranet paylaşıma kopya).
  - Konfigürasyon dosyaları (.env, ayarlar) sürüm kontrolünde ve şifreli kasada.
- DR Senaryosu:
  - Sunucu arızasında: yedek imajdan geri dönüş, LM Studio + Backend + Chroma yeniden ayağa kalkış runbook’u.

---

## 11. Güvenlik Testleri ve Kabul Kriterleri

- Penetrasyon yüzeyi: yalnızca LAN, firewall kural doğrulaması.
- Yetkisiz erişim denemesi: LM Studio ve Backend portları dışa kapalı.
- Veri sızıntısı: log taraması; PII’nin bulunmaması.
- Kabul: p95 gecikme hedefi, doğru eşleştirme isabeti (> %90 belirlenmiş test setinde), alternatif öneri kalitesi kullanıcı testinde onaylı.

---

## 12. Açık Kararlar (Karar Gerekiyor)

1) Model varyantı: Qwen 3 8B Instruct, quant: int4/int8/FP16; donanım (GPU modeli) bilgisi.
2) Backend sunum şekli: Ayrı FastAPI servisi mi, yoksa Streamlit içinde entegre backend mi?
3) ChromaDB çalışma modu: gömülü (local klasör) mı servis modu mu? Veri dizini konumu.
4) Excel → SQL mi CSV mi? KIRILMAZCAMLAR şema detayları.
5) Tam çevrimdışı mod gereksinimi: yalnızca ilk indirme mi, yoksa mutlak offline mi?

---

## 13. İlk Kurulum Kontrol Listesi

- Windows Server güncellemeleri ve .NET/VC++ önkoşulları
- Python 3.11+, pip/venv kurulumu; bağımlılıkların yüklenmesi (requirements.txt)
- LM Studio kurulumu; Qwen 3 8B indirme; API portunun doğrulanması
- MSSQL read-only kullanıcı ve firewall kuralı
- ChromaDB veri klasörü oluşturma ve izinler
- Streamlit servisinin başlatılması ve LAN’dan erişim testi

---

## 14. Operasyonel Runbook (Özet)

- Servis başlatma sırası: MSSQL → LM Studio → ChromaDB → Backend → UI
- Sağlık kontrolü: /health OK ise kullanıcıya aç
- Log rotasyonu: günlük dosyaları 7 gün sakla, sonra arşivle
- Güncelleme: önce test ortamında doğrula; model/embedding sürümleri ile not düş
