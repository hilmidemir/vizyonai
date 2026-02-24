# VizyonAI — Amaç

## Ana hedef

Yapay zekâyı mağazanda satış personeline **doğru ürün eşleştirme** ve **alternatif öneri** desteği vermek için kullanmak.

- Yapay zekâ, satış personeline müşterinin talep ettiği telefon modeline uygun aksesuarı hızlı ve doğru şekilde bulma desteği sağlar.

---

## Kullanım senaryoları

**Senaryo 1 – Doğru ürün eşleştirme**
- Müşteri: "Samsung S10 Plus için şarj cihazı istiyorum."
- AI destekli sistem: Stok veritabanını kontrol eder, uyumlu USB-C hızlı şarj cihazını listeler.

**Senaryo 2 – Alternatif öneri**
- Müşteri: "Redmi Note 8 için koruyucu cam var mı?"
- AI destekli sistem: Stokta Note 8 camı olmadığını görür, uyumlu alternatif olarak A50 camını önerir.

**Senaryo 3 – Stok ve fiyat kontrolü**
- Müşteri: "iPhone 12 için orijinal şarj adaptörü var mı?"
- AI destekli sistem: Vega muhasebe sisteminden stok ve fiyatı kontrol eder, SQL üzerinden güncel fiyatı gösterir.

**Senaryo 4 – Eğitim yükünü azaltma**
- Yeni personel: Telefon modellerini ezberlemek yerine AI arayüzüne "Huawei P30 Lite kılıf" yazar veya söyler.
- AI destekli sistem: Doğru kılıfı ve uyumlu alternatifleri listeler.
- Müşteriye sunulan cihaz özellikleri sorulduğunda (ör. "abc55 speaker özellikleri") ürünü sesli olarak müşteriyi ikna edici biçimde anlatır.

---

## Kullanım şekli

- **Kullanıcı:** Mağaza içi personel.
- **Arayüz:** AI arayüzü mağaza içi personel içindir; yazılı veya sesli soru desteklenir. Cevap kısa ve net olmalı, alternatif önerisi içermelidir. (Görüntülü soru sonraki aşamadır.)
- **Ortam:** Mağazada bir dizüstü bilgisayar; soru ve cevaplar sadece bu bilgisayardan alınır.

---

## Amaca uygun beklentiler

- Yapay zeka, sorulan telefon/tablet modelinin **şarj girişini** ve **hızlı şarj teknolojisini** zaten biliyor olmalı.
- Amaca uygun kurulacak AI sistemine **stoğundaki ürünlerin özellikleri kolayca öğretilebilmeli.**

  Örnek ürün tanımları:
  - Stok kodu SG47: şarj aleti, şarj hızı 25W, kablosu Type-C to Type-C (alış fiyatı, satış fiyatı 1–4).
  - Stok kodu SG46: şarj aleti, şarj hızı 20W, Lightning to Type-C.
  - Stok kodu KIRILMAZCAMLAR: tüm kırılmaz cam modelleri tek stokta; uyumlu koruyucu cam modelleri listesi ayrı dosyada (mevcut Excel) tutulabilir.
