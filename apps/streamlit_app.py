import streamlit as st

from vizyonai.adapters.data.csv_source import load_dataframes
from vizyonai.adapters.llm.lmstudio import get_client
from vizyonai.config.domains import get_domain_name
from vizyonai.core.engine import Engine
from vizyonai.llm.render import format_answer

st.set_page_config(page_title="VizyonAI", layout="centered")
st.title(f"VizyonAI (Moduler - {get_domain_name().capitalize()} Domain)")


@st.cache_data(show_spinner=False)
def get_data():
    return load_dataframes()


@st.cache_resource(show_spinner=False)
def get_llm_client():
    return get_client()


@st.cache_resource(show_spinner=False)
def get_engine(products_df, phones_df):
    return Engine(products_df, phones_df)


products_df, phones_df = get_data()
client = get_llm_client()
engine = get_engine(products_df, phones_df)

with st.sidebar:
    if st.button("Verileri Yenile"):
        st.cache_data.clear()
        st.cache_resource.clear()
        products_df, phones_df = get_data()
        client = get_llm_client()
        engine = get_engine(products_df, phones_df)
        st.success("Veriler yenilendi")

q = st.text_input("Soru", placeholder="Orn: S21 icin 25W sarj adaptoru / 45W sarj aleti")

if st.button("Sor"):
    if not q.strip():
        st.warning("Bir soru yaz.")
    else:
        r = engine.handle_query(q.strip())
        picked = r.get("products", [])

        with st.expander("Debug"):
            st.write(r)

        with st.spinner("Yanit hazirlaniyor..."):
            answer = format_answer(client, q.strip(), picked)

        st.subheader("Yanit")
        st.write(answer)