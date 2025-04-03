from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
import os
import subprocess
import json
import time
import imageio_ffmpeg as ffmpeg

# Vertex AI Imports
import vertexai
from vertexai.generative_models import GenerativeModel, Part

app = Flask(__name__)

app.secret_key = 'cf3ec500710dc68a09a92a7f70c6991e'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

vertexai.init(project="project1-charlesbazile-cot5930", location="us-central1")
model = GenerativeModel("gemini-1.5-flash-001")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files(folder, extension_filter=None):
    files = [f for f in sorted(os.listdir(folder), reverse=True)]
    if extension_filter:
        files = [f for f in files if f.endswith(extension_filter)]
    return files

@app.route('/')
def index():
    audio_files = [
        (f, f.replace('.wav', '.txt') if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f.replace('.wav', '.txt'))) else None)
        for f in get_files(app.config['UPLOAD_FOLDER'], '.wav')
    ]
    return render_template('index.html', audio_files=audio_files)

def convert_to_linear16(input_path, output_path):
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_path, "-y", "-i", input_path, "-ar", "48000", "-ac", "1", "-acodec", "pcm_s16le", output_path
    ], check=True)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        return "No audio data", 400

    file = request.files['audio_data']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p")
        wav_filename = filename + '.wav'
        txt_filename = filename + '.txt'

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)
        file.save(file_path)

        converted_path = file_path.replace('.wav', '_converted.wav')
        convert_to_linear16(file_path, converted_path)

        transcript, sentiment = analyze_audio_with_llm(converted_path, wav_filename)
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)

        if transcript and sentiment:
            with open(text_path, 'w') as f:
                f.write(f"Original Audio File: {wav_filename}\n")
                f.write(f"Transcription:\n{transcript}\n\n")
                f.write(f"Sentiment Analysis:\n{sentiment}\n")
            return jsonify({"transcript": transcript, "sentiment": sentiment}), 200

    return jsonify({"error": "Invalid file type or LLM error"}), 400

def analyze_audio_with_llm(file_path, filename):
    try:
        with open(file_path, "rb") as audio_file:
            audio_data = audio_file.read()

        prompt = ("Please provide an exact transcript for the audio, followed by sentiment analysis.\n"
                  "Your response should follow the format:\n"
                  "Text: USERS SPEECH TRANSCRIPTION\n"
                  "Sentiment Analysis: positive|neutral|negative")

        audio_part = Part.from_data(audio_data, mime_type="audio/wav")

        time.sleep(1.5)  # short delay to reduce rate-limit or session errors

        for attempt in range(3):
            try:
                response = model.generate_content([prompt, audio_part])
                try:
                    result = response.text.strip()
                except Exception:
                    print("LLM response was blocked by safety filters.")
                    return None, "Gemini blocked this content due to safety filters."

                transcript = ""
                sentiment = ""
                for line in result.split('\n'):
                    if line.lower().startswith("text:"):
                        transcript = line.split("Text:", 1)[1].strip()
                    elif line.lower().startswith("sentiment"):
                        sentiment = line.split(":", 1)[1].strip()

                return transcript, sentiment

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)  # retry delay

        return None, "Model could not respond due to repeated errors."

    except Exception as e:
        print(f"Error analyzing audio with LLM: {e}")
        return None, None

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("Starting the Flask app...")
    app.run(host='0.0.0.0', port=5001, debug=True)
