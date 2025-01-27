const recordButton = document.getElementById('startRecording');
const stopButton = document.getElementById('stopRecording');
const audioElement = document.getElementById('audioPlayback');
const transcriptionText = document.getElementById('transcribedText');
const recordingStatus = document.getElementById('recordingStatus');

let mediaRecorder;
let audioChunks = [];
let startTime;
let timerInterval;

function formatTime(time) {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Start recording audio
recordButton.addEventListener('click', () => {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();

      // Reset recording data and status
      audioChunks = [];
      recordingStatus.textContent = "Recording... Click 'Stop Recording' to finish.";
      startTime = Date.now();

      // Timer to show elapsed recording time
      timerInterval = setInterval(() => {
        const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
        recordingStatus.textContent = `Recording... ${formatTime(elapsedTime)}`;
      }, 1000);

      // Collect recorded audio chunks
      mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        clearInterval(timerInterval);
        recordingStatus.textContent = "Recording stopped. Processing audio...";

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioURL = URL.createObjectURL(audioBlob);
        audioElement.src = audioURL;

        // Send recorded audio to the server
        const formData = new FormData();
        formData.append('audio_data', audioBlob, 'recorded_audio.wav');

        fetch('/upload', {
          method: 'POST',
          body: formData
        })
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            if (data.transcript) {
              transcriptionText.textContent = `Transcription: ${data.transcript}`;
              recordingStatus.textContent = "Transcription completed successfully.";
            } else {
              transcriptionText.textContent = "No transcription available.";
              recordingStatus.textContent = "Failed to process transcription.";
            }
          })
          .catch(error => {
            console.error('Error uploading audio:', error);
            recordingStatus.textContent = "An error occurred during audio processing.";
          });
      };
    })
    .catch(error => {
      console.error('Error accessing microphone:', error);
      recordingStatus.textContent = "Microphone access denied.";
    });

  // Disable/Enable buttons during recording
  recordButton.disabled = true;
  stopButton.disabled = false;
});

// Stop recording audio
stopButton.addEventListener('click', () => {
  if (mediaRecorder) {
    mediaRecorder.stop();
  }

  // Disable/Enable buttons after stopping recording
  recordButton.disabled = false;
  stopButton.disabled = true;
});

// Initially disable the stop button
stopButton.disabled = true;
