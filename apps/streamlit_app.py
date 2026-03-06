import streamlit as st

from vizyonai.adapters.data.csv_source import load_dataframes
from vizyonai.adapters.llm.lmstudio import get_client
from vizyonai.config.domains import get_domain_name
from vizyonai.core.engine import Engine
from vizyonai.llm.render import format_answer
from vizyonai.ui.streamlit_components import (
    render_answer_block,
    render_header,
    render_logo_placeholder,
    render_recommendation_card,
    render_sidebar,
)
from vizyonai.ui.streamlit_theme import APP_CSS

st.set_page_config(page_title="VizyonAI", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)


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

domain_name = get_domain_name()

refresh_clicked = render_sidebar(domain_name)
if refresh_clicked:
    st.cache_data.clear()
    st.cache_resource.clear()
    products_df, phones_df = get_data()
    client = get_llm_client()
    engine = get_engine(products_df, phones_df)
    st.success("Veriler yenilendi")

left_col, right_col = st.columns([1, 2], gap="large")
with left_col:
    render_logo_placeholder()

with right_col:
    render_header()

query = st.text_input(
    "Soru",
    placeholder="Samsung Galaxy S21 için uygun şarj aleti nedir?",
)

ask = st.button("Sor", use_container_width=True)
if ask:
    q = query.strip()
    if not q:
        st.warning("Bir soru yaz.")
    else:
        result = engine.handle_query(q)
        picked = result.get("products", [])

        with st.expander("Debug", expanded=False):
            st.write(result)

        with st.spinner("Model düşünüyor..."):
            answer = format_answer(client, q, picked)

        st.markdown("### Açılan öneri şablonları")
        if not picked:
            st.info("Bu sorgu için uygun ürün bulunamadı.")
        else:
            col1, col2 = st.columns(2, gap="medium")
            for idx, product in enumerate(picked, start=1):
                target_col = col1 if idx % 2 == 1 else col2
                with target_col:
                    render_recommendation_card(product, idx)

        st.markdown("### Model Yanıtı")
        render_answer_block(answer)
