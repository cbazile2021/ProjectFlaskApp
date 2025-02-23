# Project Flask App

## 📌 Description
This Flask-based web application allows users to:
- 🎤 **Record audio** using their microphone and upload the recording for transcription using the Google **Speech-to-Text API**.
- 🔊 **Convert text input to speech** using the Google **Text-to-Speech API**.
- 📝 **Perform Sentiment Analysis** on both **transcribed speech and user-entered text** using the Google **Natural Language API**.
- 📊 **View sentiment results** for both recorded audio and generated speech.

## 🚀 Features
### ✅ **Speech-to-Text (Audio Recording & Transcription)**
- **Record audio** directly from the browser.
- **Upload and transcribe** recorded audio using **Google Speech-to-Text API**.
- **Sentiment Analysis** is performed on the transcribed text.
- Results include **sentiment label** (Positive, Negative, Neutral) with **score & magnitude**.
- Sentiment data is **saved to a file** along with the transcript.

### ✅ **Text-to-Speech (User Input to Audio)**
- **Enter text** in the input field and convert it to **speech audio**.
- **Sentiment Analysis** is performed on the text before conversion.
- Results include **sentiment label, score, and magnitude**.
- Sentiment data is **saved alongside the generated audio**.

### ✅ **User Interface Enhancements**
- **Improved UI layout** with structured sections.
- **Color-coded sentiment labels**:
  - 🟢 **Positive** (Green)
  - 🔴 **Negative** (Red)
  - ⚫ **Neutral** (Gray)
- **Organized Transcription & Sentiment Display** for a **better user experience**.

---

## ⚙️ **Setup Instructions**
### **🔹 Prerequisites**
- **Python 3.x** installed.
- **ffmpeg** installed on your system.
- **Google Cloud API credentials JSON file** for API access.

### **🔹 Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/cbazile2021/ProjectFlaskApp.git
   cd ProjectFlaskApp
