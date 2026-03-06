from __future__ import annotations

import streamlit as st


def render_sidebar(domain_name: str) -> bool:
    with st.sidebar:
        st.markdown("### Vizyon AI")
        st.caption(f"Store Assistant • {domain_name.capitalize()} Domain")

        menu = st.selectbox("Menü", ["Ana Sayfa", "İletişim", "Hakkımızda", "SSS"])
        st.caption(f"Seçili: {menu}")

        st.markdown(
            """
            <div class='vz-panel'>
              <div class='vz-kicker'>Yakında</div>
              <div style='font-weight:600; margin-bottom:0.25rem;'>Sesli giriş</div>
              <div style='font-size:0.85rem; color:rgba(255,255,255,.70)'>
                Şimdilik text input var. Sonra mikrofon butonu ve canlı dinleme animasyonu eklenebilir.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return st.button("Verileri Yenile", use_container_width=True)


def render_header() -> None:
    st.markdown(
        """
        <section class='vz-panel'>
          <div class='vz-kicker'>Yeni nesil arayüz</div>
          <div class='vz-title'>Ürünü sor, en iyi öneriyi anında kap</div>
          <div class='vz-subtitle'>
            Kullanıcı modeli ya da ürünü yazar. Sistem düşünürken loading gösterir.
            Sonra modelin döndürdüğü öneri sayısı kadar kart açılır.
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_logo_placeholder() -> None:
    st.markdown(
        """
        <div class='vz-panel' style='text-align:center;'>
          <div class='vz-kicker'>Logo alanı</div>
          <div style='border:2px dashed rgba(252,165,165,.30); border-radius:18px; padding:1rem;'>
            <div style='font-size:2rem; color:#fca5a5;'>V</div>
            <div style='font-weight:600;'>1024 x 1024 Logo</div>
            <div style='font-size:.85rem; color:rgba(255,255,255,.55)'>
              Buraya Vizyon İletişim logosu yerleşecek
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(product: dict, idx: int) -> None:
    title = product.get("urun_adi") or "Bilinmeyen Ürün"
    stock = product.get("stok_kodu", "-")
    watt = product.get("watt", "-")
    port = product.get("port", "-")
    cable = product.get("kablo", "-")
    fast = product.get("hizli_sarj", "-")
    price = product.get("satis_fiyat", product.get("fiyat4", "-"))

    st.markdown(
        f"""
        <article class='vz-card'>
          <div class='vz-badge'>Öneri {idx}</div>
          <div style='font-size:1.1rem; font-weight:700; margin-bottom:0.3rem;'>{title}</div>
          <div style='font-size:0.86rem; color:rgba(252,165,165,.9); margin-bottom:0.8rem;'>
            Stok: {stock} • {watt}W • {port}
          </div>
          <div class='vz-spec'>Kablo: {cable}</div>
          <div class='vz-spec'>Hızlı Şarj: {fast}</div>
          <div class='vz-spec'>Fiyat: {price}</div>
        </article>
        """,
        unsafe_allow_html=True,
    )


def render_answer_block(answer: str) -> None:
    st.markdown(
        f"<div class='vz-answer'>{answer}</div>",
        unsafe_allow_html=True,
    )
