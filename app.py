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

                # Automatically pick an active text model enabled on your Groq account
                models = [
                    m.id for m in client.models.list().data
                    if "whisper" not in m.id.lower()
                    and "guard" not in m.id.lower()
                    and "tts" not in m.id.lower()
                ]
                chosen_model = next(
                    (m for m in models if "llama" in m.lower() or "8b" in m.lower() or "instant" in m.lower()),
                    models[0],
                )

                prompt = f"Summarize the following PDF text as: {summary_style}. Keep it clear, accurate, and easy to scan.\n\n{pdf_text[:20000]}"

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=chosen_model,
                )

                summary = chat_completion.choices[0].message.content
                st.subheader("Summary")
                st.markdown(summary)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

