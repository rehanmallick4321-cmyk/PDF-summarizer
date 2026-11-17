from groq import Groq
from pypdf import PdfReader
import streamlit as st

st.set_page_config(page_title="AI PDF Summarizer", page_icon="📄")
st.title("📄 AI PDF Summarizer")
st.write("Upload a PDF document to generate a clear, structured summary.")

if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
summary_style = st.selectbox(
    "Select summary format:",
    [
        "Key Bullet Points",
        "Short Executive Paragraph",
        "Study Notes & Action Items",
    ],
)

if uploaded_file is not None:
    if st.button("Summarize PDF"):
        with st.spinner("Reading and summarizing your PDF..."):
            try:
                reader = PdfReader(uploaded_file)
                pdf_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                ).strip()

                if not pdf_text:
                    st.error("Could not extract text from this PDF (it may be a scanned image).")
                    st.stop()

                prompt = f"Summarize the following PDF text as: {summary_style}. Keep it clear, accurate, and easy to scan.\n\n{pdf_text[:20000]}"

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
                    st.subheader("Summary")
                    st.markdown(summary)
                    st.download_button(
                        label="📥 Download Summary (.txt)",
                        data=summary,
                        file_name="summary.txt",
                        mime="text/plain",
                    )
                else:
                    st.error(f"No working chat model found. Last error: {last_error}")

            except Exception as e:
                st.error(f"Something went wrong: {e}")

