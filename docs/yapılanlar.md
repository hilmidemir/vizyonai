# VizyonAI — Yapılanlar

## Mevcut Sistem Durumu

✅ **Operasyonel** — Temel akış çalışıyor

## Kullanılan Programlar ve Teknolojiler

- **Python 3.12** (Windows)
- **Streamlit** — Web UI framework
- **LM Studio** — Lokal LLM server
- **Qwen 3 VL 8B** — Kullanılan model
- **OpenAI Python SDK** — LMStudio API iletişimi
- **Pandas** — CSV veri işleme
- **RapidFuzz** — Bulanık eşleştirme
- **ChromaDB** — RAG için vektör depo (hazır)

## Kurulu Bileşenler

- Sanal ortam (venv) kurulu ve aktif
- Proje paketi editable mode'da kurulu (`pip install -e .`)
- `.env` dosyası hazırlandı
- Test CSV verileri oluşturuldu (`data/products.csv`, `data/phone_specs.csv`)

## Sistem Mimarisi

```
Kullanıcı → Streamlit UI → Engine → LMStudio API
                              ↓
                        CSV Verileri (Pandas)
                              ↓
                        Niyet Tanıma + Ürün Eşleştirme
                              ↓
                        LLM Yanıt Formatı → UI
```

## Temel Akış (Çalışan)

1. Kullanıcı soru giriyor → Streamlit
2. Engine intent'i detektlüyor (şarj, kablo, kamera, masaj)
3. Ürün kataloğundan eşleşir ve telefon modelini bulur
4. LLM (qwen3-vl-8b) yanıtı doğal dilde formatlar
5. Sonuç tarayıcıda gösterilir

## Test Sonuçları

- ✅ LMStudio API bağlantısı: OK
- ✅ Streamlit UI başlatması: OK
- ✅ Temel soru-cevap: OK (test: "merhaba" → LLM yanıtı alındı)
- ✅ CSV veri yükleme: OK
- ✅ Intent detection: OK

## Henüz Yapılmayan (Faz 2+)

- MSSQL Vega entegrasyonu
- ChromaDB RAG kurulumu
- Excel uyumluluk listesi (KIRILMAZCAMLAR) işlemesi
- Vektör embedding ve semantik arama
- Gelişmiş eşleştirme kuralları
- Ses giriş/çıkış
- Üretim ortamı hazırlığı

## Sonraki Adımlar

1. CSV veri setini genişletmek (gerçekçi ürünler)
2. MSSQL bağlantısı ve görünümleri oluşturmak
3. RAG vektör veritabanını kurgulamak
4. Test sorularıyla doğruluk metriği ölçmek
