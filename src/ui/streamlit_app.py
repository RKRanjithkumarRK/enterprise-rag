"""
streamlit_app.py
----------------
Streamlit frontend for the Enterprise Policy RAG system.

Place this file at: project root (same level as requirements.txt)

Why at root level?
    Streamlit Cloud looks for your main app file at the root by default.
    Keeping it here avoids any path configuration in the Streamlit Cloud UI.
    The sys.path hack from the original version has been removed — it's not
    needed when the file is at root and the src/ package is structured correctly.
"""

import streamlit as st
from src.answering.answer_query import answer_query


# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Enterprise Policy RAG",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Enterprise Information Security Policy Assistant")
st.markdown("Grounded · Reranked · Confidence-Scored RAG System")


# ==============================
# SESSION MEMORY
# ==============================

# st.session_state persists across reruns within the same browser session.
# We store the full history of Q&A results so the user can scroll back.
if "history" not in st.session_state:
    st.session_state.history = []


# ==============================
# QUESTION INPUT
# ==============================

user_query = st.text_input("Ask a question about the policy document:")

if st.button("Submit"):

    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving and generating answer..."):
            try:
                result = answer_query(user_query)
                st.session_state.history.append(result)
            except Exception as e:
                st.error("Something went wrong while generating the answer.")
                st.exception(e)


# ==============================
# DISPLAY RESULTS
# ==============================

# We reverse the history so the most recent answer appears at the top.
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
        st.write(
            f"• Section {src.get('section_number')} – {src.get('section_title')}"
        )

    with st.expander("Debug Info (raw JSON output)"):
        st.json(result)