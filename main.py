from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
import os
import subprocess
import json
import time
import imageio_ffmpeg as ffmpeg
import pdfplumber
from google.cloud import texttospeech
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# === Flask Setup ===
app = Flask(__name__)
app.secret_key = 'cf3ec500710dc68a09a92a7f70c6991e'

UPLOAD_FOLDER = 'uploads'
BOOK_FOLDER = 'books'
ANSWER_FOLDER = 'answers'
ALLOWED_AUDIO_EXTENSIONS = {'wav'}
ALLOWED_BOOK_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BOOK_FOLDER'] = BOOK_FOLDER
app.config['ANSWER_FOLDER'] = ANSWER_FOLDER

for folder in [UPLOAD_FOLDER, BOOK_FOLDER, ANSWER_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# === Vertex AI Initialization ===
vertexai.init(project="project1-charlesbazile-cot5930", location="us-central1")
model = GenerativeModel("gemini-2.5-pro-exp-03-25")

# === Google Cloud TTS Client ===
tts_client = texttospeech.TextToSpeechClient()

# === Utility Functions ===
def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def get_latest_book_path():
    pdfs = sorted([f for f in os.listdir(BOOK_FOLDER) if f.endswith(".pdf")], reverse=True)
    return os.path.join(BOOK_FOLDER, pdfs[0]) if pdfs else None

def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text[:5000]  # Reduce size for safety

def convert_to_linear16(input_path, output_path):
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_path, "-y", "-i", input_path, "-ar", "48000", "-ac", "1", "-acodec", "pcm_s16le", output_path
    ], check=True)

def synthesize_speech(text, output_path):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

# === Routes ===
@app.route('/')
def index():
    audio_files = [
        (f, f.replace('.wav', '.txt') if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f.replace('.wav', '.txt'))) else None)
        for f in sorted(os.listdir(UPLOAD_FOLDER), reverse=True) if f.endswith('.wav')
    ]
    book_files = sorted(os.listdir(BOOK_FOLDER), reverse=True)
    answer_files = sorted(os.listdir(ANSWER_FOLDER), reverse=True)
    return render_template('index.html', audio_files=audio_files, book_files=book_files, answer_files=answer_files)

@app.route('/upload_book', methods=['POST'])
def upload_book():
    if 'book_file' not in request.files:
        return "No file uploaded", 400

    file = request.files['book_file']
    if file and allowed_file(file.filename, ALLOWED_BOOK_EXTENSIONS):
        filename = datetime.now().strftime("%Y%m%d-%H%M%S") + "_" + file.filename
        file_path = os.path.join(BOOK_FOLDER, filename)
        file.save(file_path)
        return redirect('/')
    return "Invalid file", 400

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        if 'audio_data' not in request.files:
            return "No audio data", 400

        file = request.files['audio_data']
        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
            filename = datetime.now().strftime("%Y%m%d-%I%M%S%p")
            wav_filename = filename + '.wav'
            txt_filename = filename + '.txt'

            file_path = os.path.join(UPLOAD_FOLDER, wav_filename)
            file.save(file_path)

            converted_path = file_path.replace('.wav', '_converted.wav')
            convert_to_linear16(file_path, converted_path)

            print("Calling analyze_question_with_llm")
            transcript, answer = analyze_question_with_llm(converted_path)

            if not transcript or not answer:
                return jsonify({"error": "Processing failed"}), 500

            text_path = os.path.join(UPLOAD_FOLDER, txt_filename)
            answer_path = os.path.join(ANSWER_FOLDER, filename + '.mp3')

            with open(text_path, 'w') as f:
                f.write(f"Original Audio File: {wav_filename}\n")
                f.write(f"Transcription:\n{transcript}\n\n")
                f.write(f"Answer from Book:\n{answer}\n")

            synthesize_speech(answer, answer_path)

            return jsonify({
                "transcript": transcript,
                "answer": answer,
                "audio_response": f"/answers/{filename}.mp3"
            }), 200

        return jsonify({"error": "Invalid file"}), 400
    except Exception as e:
        print(f"Upload route error: {e}")
        return jsonify({"error": "Exception occurred in processing"}), 500

def analyze_question_with_llm(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()

        book_path = get_latest_book_path()
        if not book_path:
            return None, "No book uploaded."

        book_text = extract_text_from_pdf(book_path)[:5000]  # Trim for LLM input

        prompt = (
            "You are a helpful assistant. Answer the user's question using ONLY the contents of the following book.\n\n"
            "BOOK CONTENT:\n"
            f"{book_text}\n\n"
            "QUESTION:"
        )

        audio_part = Part.from_data(audio_data, mime_type="audio/wav")

        for attempt in range(3):
            try:
                response = model.generate_content([prompt, audio_part])

                # ✨ Check if response was blocked
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    print("⚠️ Gemini blocked the request:", response.prompt_feedback.block_reason)
                    return "Blocked for safety", "Gemini blocked the content due to safety filters."

                return "Transcribed question (auto)", response.text.strip()
            except Exception as e:
                print(f"Retry {attempt + 1} failed:", e)
                time.sleep(2)

        return None, "Failed to get LLM response."

    except Exception as e:
        print(f"LLM Analysis Error: {e}")
        return None, None


@app.route('/answers/<filename>')
def get_answer_audio(filename):
    return send_from_directory(ANSWER_FOLDER, filename)

@app.route('/uploads/<filename>')
def get_uploaded_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/books/<filename>')
def get_uploaded_book(filename):
    return send_from_directory(BOOK_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"\U0001F4E6 Flask App Running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
