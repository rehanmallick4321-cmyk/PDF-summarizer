import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AI PDF Summarizer", page_icon="📄")
st.title("📄 AI PDF Summarizer")
st.write("Upload a PDF document to generate a clear, structured summary.")

# Initialize the Gemini client using Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# File uploader and summary style selector
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
                pdf_bytes = uploaded_file.read()
                prompt = f"Summarize this PDF document as: {summary_style}. Keep it clear, accurate, and easy to scan."

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=pdf_bytes,
                            mime_type="application/pdf",
                        ),
                        prompt,
                    ],
                )

                st.subheader("Summary")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Something went wrong: {e}")
