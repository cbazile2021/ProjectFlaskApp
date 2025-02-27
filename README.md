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


   # How to Use the App

## 📌 Accessing the Application  
Open a web browser and navigate to the deployed application:  
🔗 [Live Application](https://projectflaskapp-921157662827.us-central1.run.app/)

---

## 🎤 Recording and Analyzing Speech  
1. Click on the **“Start Recording”** button.  
2. Speak into the microphone and click **“Stop Recording”** when finished.  
3. The recorded audio will be processed:  
   - The app will **transcribe your speech into text**.  
   - A **sentiment analysis** will be performed.  
   - The **transcription and sentiment data** will be **displayed and saved**.  

---

## 📝 Converting Text to Speech and Analyzing Sentiment  
1. Enter text into the **text input field**.  
2. Click on **“Convert to Audio”** to generate speech.  
3. The app will **analyze the sentiment** before conversion.  
4. Once processed, you can **listen to the generated speech** and **view the sentiment results**.  
5. The **text, audio, and sentiment data are stored together** for reference.  

---

## 📊 Understanding Sentiment Analysis Results  
The app assigns one of **three sentiment labels** to the input:  

- **Positive:** Indicates happy, uplifting, or optimistic content.  
- **Neutral:** Indicates neutral or factual statements.  
- **Negative:** Indicates sadness, frustration, or negative sentiment.  

Each sentiment analysis result includes:  
- **Sentiment Score**: Shows how strong the emotion is.  
- **Magnitude**: Reflects the **intensity of emotion** detected in the input.  

---

🚀 **Now you're ready to explore the app! Let me know if you need any modifications!** 🎉🔥

