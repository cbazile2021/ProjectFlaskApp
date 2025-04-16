# 📚 Voice-to-Book Q&A Web App – by Charles Bazile

## 📌 Description
This Flask-based web application enables users to:
- 📘 **Upload a PDF book** for reference.
- 🎤 **Record a question using their voice**, which is transcribed and answered **using only the content of the uploaded book**.
- 🤖 Responses are generated using **Google Vertex AI's Gemini 2.5 multimodal model**.

🔁 All interactions (audio, transcript, answer) are processed and saved for reference.

> ✨ Previous APIs (Speech-to-Text, Natural Language, Text-to-Speech) were **replaced** with a single multimodal LLM call for efficiency and better performance.

---

## 🚀 Features (Current Version)

### ✅ **Gemini 2.5 Multimodal Q&A**
- Voice input recorded directly in the browser
- PDF book is uploaded and parsed as the knowledge source
- A single call to **Gemini 2.5**:
  - Transcribes the question
  - Answers based **only** on the uploaded PDF content
- Displays transcription and book-based answer
- Audio answer is generated with **Text-to-Speech** and played automatically

### ✅ **Streamlined User Interface**
- One-click book upload
- Clear recording controls
- Real-time feedback with:
  - Transcribed text
  - Answer content
  - Spoken answer via MP3 playback
- Visual status updates (uploading, processing, error handling)

---

## ⚙️ Setup Instructions

### 🔹 Prerequisites
- Python 3.8+
- `ffmpeg` installed
- Google Cloud project with **Vertex AI** and **Text-to-Speech** APIs enabled
- A **service account JSON key** with access to both APIs

### 🔹 Installation
```bash
git clone https://github.com/cbazile2021/ProjectFlaskApp.git
cd ProjectFlaskApp

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/key.json"
python main.py
