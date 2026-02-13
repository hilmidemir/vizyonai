import streamlit as st

from vizyonai.adapters.data.csv_source import load_dataframes
from vizyonai.adapters.llm.lmstudio import get_client
from vizyonai.core.engine import Engine
from vizyonai.config.domains import get_domain_name
from vizyonai.llm.render import format_answer

st.set_page_config(page_title="VizyonAI", layout="centered")
st.title(f"VizyonAI (Modüler - {get_domain_name().capitalize()} Domain)")

client = get_client()

@st.cache_data(show_spinner=False)
def get_data():
    return load_dataframes()

products_df, phones_df = get_data()

with st.sidebar:
    if st.button("Verileri Yenile"):
        st.cache_data.clear()
        products_df, phones_df = get_data()
        st.success("Veriler yenilendi ✅")

engine = Engine(products_df, phones_df)

q = st.text_input("Soru", placeholder="Örn: S21 için 25W şarj adaptörü / 45W şarj aleti")

if st.button("Sor"):
    if not q.strip():
        st.warning("Bir soru yaz.")
    else:
        r = engine.handle_query(q.strip())
        picked = r.get("products", [])

        with st.expander("Debug"):
            st.write(r)

        with st.spinner("Yanıt hazırlanıyor..."):
            answer = format_answer(client, q.strip(), picked)

        st.subheader("Yanıt")
        st.write(answer)
