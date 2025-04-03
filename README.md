
# Project Flask App

## 📌 Description
This Flask-based web application allows users to:
- 🎤 **Record audio** using their microphone and upload the recording for transcription and sentiment analysis using Google Cloud's **Vertex AI Multimodal LLM**.
- 📝 **View real-time sentiment feedback** directly from the LLM response.

🚫 **Text-to-Speech and separate APIs (Speech-to-Text, Natural Language)** were used in the previous version but have now been removed to simplify the experience.

## 🚀 Features (Current Version)
### ✅ **Unified Transcription & Sentiment Analysis**
- Record audio directly from the browser.
- Upload and analyze using **Vertex AI Gemini models**.
- A single API call returns both **transcription** and **sentiment analysis**.
- Results are saved in a `.txt` file alongside the `.wav` audio.
- Graceful handling for **quota issues**, **timeouts**, and **safety filter blocks**.

### ✅ **User Interface Enhancements**
- Modern layout with a clean recording interface.
- Displayed transcription and sentiment results side-by-side.
- Clear indicators when safety filters block the model’s response.

---

## 🧠 Features from Previous Version
Before the Project 3 changes, the app included:

### 🎙️ **Speech-to-Text using Google API**
- Audio recording from the browser
- Uploads were transcribed using the **Google Speech-to-Text API**
- Sentiment analysis was performed using **Google Natural Language API**

### 🗣️ **Text-to-Speech with Sentiment**
- User could enter text
- Text was converted to audio using **Google Text-to-Speech API**
- Sentiment was analyzed before conversion

### 🎨 **UI Enhancements**
- Color-coded sentiment labels (green for positive, red for negative, gray for neutral)
- Sections for both transcribed audio and text-generated speech

These features were removed or merged to simplify the current architecture.

---

## ⚙️ Setup Instructions

### 🔹 Prerequisites
- Python 3.x installed
- ffmpeg installed on your system
- Google Cloud Project with Vertex AI enabled
- A service account JSON key file with access to Vertex AI

### 🔹 Installation
```bash
git clone https://github.com/cbazile2021/ProjectFlaskApp.git
cd ProjectFlaskApp

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/key.json"
python main.py
```

---

## 🧪 How to Use the App

### 📌 Accessing the Application
Open a web browser and go to:  
🔗 [Live App](https://projectflaskapp-921157662827.us-central1.run.app/)

### 🎤 Record & Analyze Speech
1. Click **Start Recording**  
2. Speak clearly and click **Stop Recording**  
3. The app will:
   - Convert audio to WAV
   - Transcribe + analyze using Gemini
   - Display and save the results

---

## 📊 Understanding the Sentiment Results
- Sentiment labels: **Positive**, **Neutral**, **Negative**
- Model response may be blocked by safety filters
- The app shows a message if that happens

---

## 📉 Limitations & Reliability
- Safety filters may block some results
- Gemini APIs have usage quotas
- Retry logic + delay reduce failure rates

---

## 📂 File Storage Behavior
- `.wav` files stored in `uploads/`
- Each has a matching `.txt` with:
  - File name
  - Transcript
  - Sentiment analysis

---

## 🔁 Recent Changes (Project 3 Update)
| Change                         | Description                                               |
|-------------------------------|-----------------------------------------------------------|
| 🎯 Replaced 3 APIs             | Now uses a single Gemini LLM for transcription & sentiment |
| 🧹 Removed TTS                | Text-to-Speech feature removed                            |
| 🚦 Retry + Safety Handling    | App won't crash if Gemini blocks or times out             |
| 💾 Better File Management     | All outputs saved by filename with `.txt` extension       |

---

🚀 **You’re now ready to experience smarter, faster speech intelligence!** 🎉
