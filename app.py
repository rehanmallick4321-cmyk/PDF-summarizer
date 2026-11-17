from groq import Groq
from pypdf import PdfReader
import streamlit as st

st.set_page_config(
    page_title="DocuBrief AI | Smart PDF Summarizer & Chat",
    page_icon="✨",
    layout="wide",
)

# Custom CSS for modern cards, spacing, and buttons
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    .hero-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 1.5rem;
    }
    .hero-box h1 {
        margin: 0;
        font-size: 2rem;
        color: #f8fafc;
    }
    .hero-box p {
        margin: 0.4rem 0 0 0;
        color: #94a3b8;
        font-size: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
    }
    .stButton > button:hover {
        opacity: 0.92;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero Header
st.markdown(
    """
    <div class="hero-box">
        <h1>✨ DocuBrief AI</h1>
        <p>Summarize lengthy PDFs and chat directly with your documents.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())


def ask_groq(messages):
    available = [m.id for m in client.models.list().data]
    preferred = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
    ]
    candidates = [m for m in preferred if m in available] + [
        m for m in available if m not in preferred
    ]
    last_error = None
    for model_id in candidates:
        try:
            res = client.chat.completions.create(
                messages=messages,
                model=model_id,
            )
            reply = res.choices.pop(0).message.content
            if reply:
                return reply
        except Exception as err:
            last_error = err
    raise RuntimeError(f"No working chat model found. Last error: {last_error}")


# Initialize session state so summary and chat persist across questions
for key, default in [
    ("doc_name", None),
    ("pdf_text", ""),
    ("num_pages", 0),
    ("word_count", 0),
    ("summary", ""),
    ("chat_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

left_col, right_col = st.columns([1, 1.4], gap="large")

with left_col:
    with st.container(border=True):
        st.subheader("1. Upload & Customize")
        uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

        # Extract text once when a new PDF is uploaded
        if uploaded_file is not None and uploaded_file.name != st.session_state.doc_name:
            reader = PdfReader(uploaded_file)
            extracted = "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()
            st.session_state.doc_name = uploaded_file.name
            st.session_state.pdf_text = extracted
            st.session_state.num_pages = len(reader.pages)
            st.session_state.word_count = len(extracted.split())
            st.session_state.summary = ""
            st.session_state.chat_history = []

        summary_style = st.selectbox(
            "Summary format",
            [
                "Key Bullet Points",
                "Short Executive Paragraph",
                "Study Notes & Action Items",
                "Simple Beginner Explanation",
            ],
        )

        detail_level = st.select_slider(
            "Summary length",
            options=["Brief", "Balanced", "Detailed"],
            value="Balanced",
        )

        language = st.selectbox(
            "Output language",
            ["English", "German", "Hindi", "Spanish", "French", "Arabic", "Japanese"],
        )

        generate_btn = st.button("✨ Generate Summary")

with right_col:
    with st.container(border=True):
        st.subheader("2. AI Summary")

        if uploaded_file is None:
            st.info("👈 Upload a PDF on the left to generate a summary and unlock **Chat with PDF**.")
        elif not st.session_state.pdf_text:
            st.error("Could not extract text from this PDF (it may be a scanned image).")
        else:
            m1, m2 = st.columns(2)
            m1.metric("Pages Read", st.session_state.num_pages)
            m2.metric("Words Extracted", f"{st.session_state.word_count:,}")
            st.divider()

            if generate_btn:
                with st.spinner("Analyzing document and crafting your summary..."):
                    try:
                        prompt = (
                            f"Summarize the following PDF text in {language}.\n"
                            f"Format: {summary_style}.\n"
                            f"Length/Depth: {detail_level}.\n"
                            f"Use clean headings and bullet points so it is easy to scan.\n\n"
                            f"{st.session_state.pdf_text[:20000]}"
                        )
                        st.session_state.summary = ask_groq(
                            [{"role": "user", "content": prompt}]
                        )
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

            if st.session_state.summary:
                st.markdown(st.session_state.summary)
                st.divider()
                st.download_button(
                    label="📥 Download Summary (.txt)",
                    data=st.session_state.summary,
                    file_name=f"{st.session_state.doc_name.rsplit('.', 1).pop(0)}_summary.txt",
                    mime="text/plain",
                )
            else:
                st.caption(f"Ready to summarize **{st.session_state.doc_name}**. Tap **Generate Summary** on the left.")

    # Chat with PDF section
    if uploaded_file is not None and st.session_state.pdf_text:
        with st.container(border=True):
            st.subheader("3. 💬 Chat with PDF")
            st.caption("Ask any follow-up question about the uploaded document.")

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_question = st.chat_input("Ask a question about this PDF...")
            if user_question:
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_question}
                )
                with st.chat_message("user"):
                    st.markdown(user_question)

                with st.chat_message("assistant"):
                    with st.spinner("Searching PDF for answer..."):
                        try:
                            system_prompt = (
                                f"You are a helpful document assistant. Answer the user's question in {language} "
                                f"based ONLY on the PDF content below. If the answer is not in the document, say so clearly.\n\n"
                                f"PDF CONTENT:\n{st.session_state.pdf_text[:20000]}"
                            )
                            api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history[-6:]
                            answer = ask_groq(api_messages)
                            st.markdown(answer)
                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": answer}
                            )
                        except Exception as e:
                            st.error(f"Something went wrong: {e}")

            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()

