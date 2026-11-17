# ✨ DocuBrief AI — Smart PDF Summarizer

An AI-powered web application that turns lengthy PDF documents into clear, structured summaries in multiple languages within seconds.

🔗 **Live App:** [Open DocuBrief AI](https://streamlit.app)

---

## 🚀 Features
- **Multiple Summary Formats:** Choose between Key Bullet Points, Short Executive Paragraphs, Study Notes & Action Items, or Beginner Explanations.
- **Customizable Depth:** Adjust summary length (Brief, Balanced, Detailed) with an interactive slider.
- **Multi-Language Output:** Translate and summarize documents into **English, German, Hindi, Spanish, French, Arabic, and Japanese**.
- **Document Insights:** Displays page count and extracted word count automatically.
- **One-Click Export:** Download generated summaries directly as a `.txt` file.

---

## 🛠️ Tech Stack
- **Frontend & Deployment:** Python, Streamlit, Streamlit Community Cloud
- **AI & LLM Inference:** Groq API (Llama 3 / Qwen / GPT-OSS models)
- **PDF Parsing:** PyPDF & Cryptography

---

## ⚙️ Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com
   cd PDF-summarizer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Groq API key to `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
4. Launch the app:
   ```bash
   streamlit run app.py
   ```
