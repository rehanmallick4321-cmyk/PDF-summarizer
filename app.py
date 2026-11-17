from groq import Groq
from pypdf import PdfReader
import streamlit as st

st.set_page_config(
    page_title="DocuBrief AI | Smart PDF Summarizer",
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
        <p>Turn lengthy PDFs into crisp, structured insights in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

# Two-column layout: Controls on the left, Output on the right
left_col, right_col = st.columns([1, 1.4], gap="large")

with left_col:
    with st.container(border=True):
        st.subheader("1. Upload & Customize")
        uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

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
            st.info("👈 Upload a PDF on the left and click **Generate Summary** to see your results here.")
        elif generate_btn:
            with st.spinner("Analyzing document and crafting your summary..."):
                try:
                    reader = PdfReader(uploaded_file)
                    num_pages = len(reader.pages)
                    pdf_text = "\n".join(
                        page.extract_text() or "" for page in reader.pages
                    ).strip()

                    if not pdf_text:
                        st.error("Could not extract text from this PDF (it may be a scanned image).")
                        st.stop()

                    word_count = len(pdf_text.split())

                    # Document metrics bar
                    m1, m2 = st.columns(2)
                    m1.metric("Pages Read", num_pages)
                    m2.metric("Words Extracted", f"{word_count:,}")
                    st.divider()

                    prompt = (
                        f"Summarize the following PDF text in {language}.\n"
                        f"Format: {summary_style}.\n"
                        f"Length/Depth: {detail_level}.\n"
                        f"Use clean headings and bullet points so it is easy to scan.\n\n"
                        f"{pdf_text[:20000]}"
                    )

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

                    summary = None
                    last_error = None
                    for model_id in candidates:
                        try:
                            res = client.chat.completions.create(
                                messages=[{"role": "user", "content": prompt}],
                                model=model_id,
                            )
                            summary = res.choices.pop(0).message.content
                            if summary:
                                break
                        except Exception as err:
                            last_error = err

                    if summary:
                        st.markdown(summary)
                        st.divider()
                        st.download_button(
                            label="📥 Download Summary (.txt)",
                            data=summary,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_summary.txt",
                            mime="text/plain",
                        )
                    else:
                        st.error(f"No working chat model found. Last error: {last_error}")

                except Exception as e:
                    st.error(f"Something went wrong: {e}")
        else:
            st.caption(f"Ready to summarize **{uploaded_file.name}**. Tap **Generate Summary** on the left.")

