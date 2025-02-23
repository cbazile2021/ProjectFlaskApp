from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import os
import subprocess
import json
import imageio_ffmpeg as ffmpeg
import subprocess
from google.cloud import language_v1



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

    tts_files = [
    {
        "filename": filename,
        "text": tts_records[filename]["text"] if filename in tts_records else "Unknown text",
        "sentiment": tts_records[filename]["sentiment"] if filename in tts_records else {"label": "Unknown", "score": 0, "magnitude": 0}
    }
    for filename in get_files(app.config['TTS_FOLDER'], '.mp3')
    ]


    return render_template('index.html', audio_files=audio_files, tts_files=tts_files)





def convert_to_linear16(input_path, output_path):
    # Use imageio_ffmpeg to locate ffmpeg
    ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    subprocess.run([
        ffmpeg_path, "-y", "-i", input_path, "-ar", "48000", "-ac", "1", "-acodec", "pcm_s16le", output_path
    ], check=True)


@app.route('/upload', methods=['POST'])
def upload_audio():
    """Handle audio upload, transcription, and sentiment analysis."""
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

        # Transcribe audio
        transcript = transcribe_audio(converted_path)
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)

        if transcript:
            # Perform Sentiment Analysis
            sentiment_result = analyze_sentiment(transcript)

            with open(text_path, 'w') as f:
                f.write(f"Original Audio File: {wav_filename}\n")
                f.write(f"Transcription:\n{transcript}\n\n")
                f.write(f"Sentiment Analysis:\n")
                f.write(f"Label: {sentiment_result['label']}\n")
                f.write(f"Score: {sentiment_result['score']}\n")
                f.write(f"Magnitude: {sentiment_result['magnitude']}\n")

            return jsonify({"transcript": transcript, "sentiment": sentiment_result}), 200

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
        print(f"Error in transcribe_audio: {e}")  # Debugging output
        return None


@app.route('/upload_text', methods=['POST'])
def upload_text():
    """Handle text input, generate audio, and perform sentiment analysis."""
    text = request.form['text']
    if text:
        filename = datetime.now().strftime("%Y%m%d-%I%M%S%p")
        mp3_filename = filename + '.mp3'
        txt_filename = filename + '.txt'

        # Save the text input
        text_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
        
        # Call Text-to-Speech API
        file_path = os.path.join(app.config['TTS_FOLDER'], mp3_filename)
        synthesize_speech(text, file_path)

        # Perform Sentiment Analysis
        sentiment_result = analyze_sentiment(text)

        # Save the text, sentiment, and MP3 link
        with open(text_path, 'w') as f:
            f.write(f"Generated Audio File: {mp3_filename}\n")
            f.write(f"Original Text:\n{text}\n\n")
            f.write(f"Sentiment Analysis:\n")
            f.write(f"Label: {sentiment_result['label']}\n")
            f.write(f"Score: {sentiment_result['score']}\n")
            f.write(f"Magnitude: {sentiment_result['magnitude']}\n")
            f.write(f"Listen to the audio: /tts/{mp3_filename}\n")

        # Save the record
        save_tts_record(mp3_filename, text, sentiment_result)

    return redirect('/')




TTS_RECORDS_FILE = "tts_records.json"

def save_tts_record(filename, text, sentiment):
    """Save the text-to-speech record with sentiment analysis to a JSON file."""
    records = {}

    # Load existing records
    if os.path.exists(TTS_RECORDS_FILE):
        try:
            with open(TTS_RECORDS_FILE, 'r') as f:
                records = json.load(f)
        except json.JSONDecodeError:
            print("JSONDecodeError: tts_records.json is empty or invalid. Resetting it.")
            records = {}

    # Add the new record with sentiment data
    records[filename] = {
        "text": text,
        "sentiment": sentiment
    }

    # Save back to JSON file
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
    
def analyze_sentiment(text):
    """Uses Google Cloud Natural Language API to analyze sentiment."""
    try:
        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = client.analyze_sentiment(request={"document": document})
        sentiment = response.document_sentiment

        # Custom logic for labeling sentiment
        if sentiment.score >= 0.5:
            label = "Positive"
        elif sentiment.score <= -0.5:
            label = "Negative"
        else:
            label = "Neutral"

        result = {
            "score": round(sentiment.score, 2),
            "magnitude": round(sentiment.magnitude, 2),
            "label": label
        }

        return result
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return None





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
