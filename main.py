from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import os
import subprocess
import json
import imageio_ffmpeg as ffmpeg
import subprocess


app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'cf3ec500710dc68a09a92a7f70c6991e'

# Configure upload folders
UPLOAD_FOLDER = 'uploads'
TTS_FOLDER = 'tts'
ALLOWED_EXTENSIONS = {'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TTS_FOLDER'] = TTS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files(folder, extension_filter=None):
    """Get a list of files in a folder, optionally filtered by extension."""
    files = [f for f in sorted(os.listdir(folder), reverse=True)]
    if extension_filter:
        files = [f for f in files if f.endswith(extension_filter)]
    return files

@app.route('/')
def index():
    """Display the homepage with audio and text files."""
    audio_files = [
        (f, f.replace('.wav', '.txt') if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f.replace('.wav', '.txt'))) else None)
        for f in get_files(app.config['UPLOAD_FOLDER'], '.wav')
    ]
    tts_records = load_tts_records()
    tts_files = [(filename, tts_records.get(filename, "Unknown text")) for filename in get_files(app.config['TTS_FOLDER'], '.mp3')]
    return render_template('index.html', audio_files=audio_files, tts_files=tts_files)





def convert_to_linear16(input_path, output_path):
    # Use imageio_ffmpeg to locate ffmpeg
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_path, "-y", "-i", input_path, "-ar", "48000", "-ac", "1", "-acodec", "pcm_s16le", output_path
    ], check=True)


# def convert_to_linear16(input_path, output_path):
#     """Force audio to LINEAR16 format with 48000 Hz sample rate."""
#     subprocess.run([
#         "ffmpeg", "-y", "-i", input_path, "-ar", "48000", "-ac", "1", "-acodec", "pcm_s16le", output_path
#     ], check=True)

@app.route('/upload', methods=['POST'])
def upload_audio():
    """Handle audio upload and transcription."""
    if 'audio_data' not in request.files:
        return "No audio data", 400

    file = request.files['audio_data']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Convert the file to LINEAR16 format
        converted_path = file_path.replace('.wav', '_converted.wav')
        convert_to_linear16(file_path, converted_path)

        # Transcribe the converted file
        transcript = transcribe_audio(converted_path)
        if transcript:
            transcript_path = converted_path.replace('.wav', '.txt')
            with open(transcript_path, 'w') as f:
                f.write(transcript)

            # Return the transcript as JSON
            return jsonify({"transcript": transcript}), 200
        else:
            return jsonify({"error": "Transcription failed"}), 500

    return jsonify({"error": "Invalid file type"}), 400

def transcribe_audio(file_path):
    """Uses Google Speech-to-Text API to transcribe audio."""
    try:
        client = speech.SpeechClient()
        with open(file_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code="en-US",
        )
        
        response = client.recognize(config=config, audio=audio)
        if not response.results:
            print("No transcription results returned.")
            return None
        
        return "\n".join(result.alternatives[0].transcript for result in response.results)
    
    except Exception as e:
        print(f"Error in transcribe_audio: {e}")
        return None
    
@app.route('/upload_text', methods=['POST'])
def upload_text():
    """Handle text input and generate audio."""
    text = request.form['text']
    if text:
        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.mp3'
        file_path = os.path.join(app.config['TTS_FOLDER'], filename)

        # Call the Text-to-Speech API
        synthesize_speech(text, file_path)

        # Save the record
        save_tts_record(filename, text)

    return redirect('/')


TTS_RECORDS_FILE = "tts_records.json"

def save_tts_record(filename, text):
    """Save the text-to-speech record to a JSON file."""
    records = {}
    # Check if the file exists and load records if valid
    if os.path.exists(TTS_RECORDS_FILE):
        try:
            with open(TTS_RECORDS_FILE, 'r') as f:
                records = json.load(f)
        except json.JSONDecodeError:
            print("JSONDecodeError: tts_records.json is empty or invalid. Overwriting with new record.")
            records = {}  # Reset to an empty dictionary if the file is invalid

    # Add the new record and save
    records[filename] = text
    with open(TTS_RECORDS_FILE, 'w') as f:
        json.dump(records, f, indent=4)


def load_tts_records():
    """Load the text-to-speech records from a JSON file."""
    if os.path.exists(TTS_RECORDS_FILE):
        try:
            with open(TTS_RECORDS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("JSONDecodeError: tts_records.json is empty or invalid. Returning an empty dictionary.")
            return {}
    return {}



def synthesize_speech(text, output_path):
    """Uses Google Text-to-Speech API to generate audio from text."""
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded audio files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/tts/<filename>')
def tts_file(filename):
    """Serve text-to-speech generated audio files."""
    return send_from_directory(app.config['TTS_FOLDER'], filename)

if __name__ == '__main__':
    print("Starting the Flask app...")
    app.run(host='0.0.0.0', port=5001, debug=True)
