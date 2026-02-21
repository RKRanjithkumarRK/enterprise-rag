import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "https://enterprise-policy-rag-wb9d.onrender.com")

st.set_page_config(page_title="Enterprise Policy RAG", page_icon="🔐", layout="wide")
st.title("🔐 Enterprise Information Security Policy Assistant")
st.markdown("Grounded · Confidence-Scored RAG System")

if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.text_input("Ask a question about the policy document:")

if st.button("Submit"):
    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving and generating answer... (first request may take 60s to wake up server)"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": user_query},
                    timeout=120
                )
                result = response.json()
                st.session_state.history.append(result)
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

for i, result in enumerate(reversed(st.session_state.history)):
    st.markdown("---")
    st.subheader(f"Answer {len(st.session_state.history) - i}")
    st.write(result.get("answer"))
    col1, col2, col3 = st.columns(3)
    col1.metric("Confidence Score", result.get("confidence_score"))
    col2.metric("Confidence Level", result.get("confidence_level"))
    col3.metric("Grounded?", str(result.get("grounded_in_context")))
    st.markdown("### Sources")
    for src in result.get("sources", []):
        st.write(f"• Section {src.get('section_number')} – {src.get('section_title')}")