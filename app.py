"""Chat-brugerflade til dine noter.

Kør:  streamlit run app.py
"""
import streamlit as st

from ask import answer

st.set_page_config(page_title="Spørg mine noter")
st.title("Spørg mine noter")
st.caption("RAG med ChromaDB og en lokal model via Ollama")

# Streamlit kører hele scriptet forfra ved hver handling,
# så samtalen skal gemmes i session_state for ikke at forsvinde.
if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(hits: list[dict]) -> None:
    with st.expander("Kilder"):
        for h in hits:
            st.markdown(f"**{h['source']}, side {h['page']}**")
            st.caption(h["text"][:300] + "...")


# Vis tidligere beskeder
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("hits"):
            show_sources(msg["hits"])

# Nyt spørgsmål
if question := st.chat_input("Stil et spørgsmål til dine noter"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Søger i noterne og tænker..."):
            text, raw_hits = answer(question)
        hits = [{"source": m["source"], "page": m["page"], "text": doc} for doc, m in raw_hits]
        st.markdown(text)
        show_sources(hits)

    st.session_state.messages.append({"role": "assistant", "content": text, "hits": hits})
