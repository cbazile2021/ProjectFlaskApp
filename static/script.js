document.addEventListener('DOMContentLoaded', () => {
  console.log("📜 script.js is loaded");

  let mediaRecorder;
  let recordedChunks = [];

  const startBtn = document.getElementById('startRecording');
  const stopBtn = document.getElementById('stopRecording');
  const audioPlayback = document.getElementById('audioPlayback');
  const recordingStatus = document.getElementById('recordingStatus');
  const transcribedText = document.getElementById('transcribedText');
  const bookAnswer = document.getElementById('bookAnswer');
  const answerAudio = document.getElementById('answerAudio');

  startBtn.addEventListener('click', async () => {
      console.log("🎬 Start Recording button clicked");
      recordedChunks = [];
      recordingStatus.textContent = "🎙️ Recording...";
      startBtn.disabled = true;
      stopBtn.disabled = false;

      try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          console.log("🎤 Microphone stream received");

          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = (event) => {
              if (event.data.size > 0) {
                  recordedChunks.push(event.data);
                  console.log("📦 Chunk added");
              }
          };

          mediaRecorder.onstop = async () => {
              const blob = new Blob(recordedChunks, { type: 'audio/wav' });
              const url = URL.createObjectURL(blob);
              audioPlayback.src = url;

              const formData = new FormData();
              formData.append('audio_data', blob, 'question.wav');

              recordingStatus.innerHTML = "⏳ Uploading and analyzing... <span class='spinner'></span>";

              try {
                  const response = await fetch('/upload', {
                      method: 'POST',
                      body: formData
                  });

                  if (response.ok) {
                      const result = await response.json();
                      transcribedText.textContent = result.transcript || 'No transcript returned.';
                      bookAnswer.textContent = result.answer || 'No answer returned.';
                      if (result.audio_response) {
                          answerAudio.src = result.audio_response;
                          answerAudio.play();
                      }
                      recordingStatus.textContent = "✅ Answer received!";
                  } else {
                      transcribedText.textContent = 'Error occurred.';
                      bookAnswer.textContent = '';
                      recordingStatus.textContent = "❌ Something went wrong.";
                  }
              } catch (error) {
                  console.error("Upload failed:", error);
                  transcribedText.textContent = 'Upload failed.';
                  bookAnswer.textContent = '';
                  recordingStatus.textContent = "❌ Upload failed.";
              }
          };

          mediaRecorder.start();
          console.log("⏺️ MediaRecorder started");

      } catch (err) {
          console.error("❌ Failed to get microphone access:", err);
          alert("Failed to access the microphone. Please enable it in your browser settings.");
      }
  });

  stopBtn.addEventListener('click', () => {
      stopBtn.disabled = true;
      startBtn.disabled = false;
      recordingStatus.textContent = "🧠 Processing...";
      mediaRecorder.stop();
      console.log("🛑 MediaRecorder stopped");
  });

  // Drag-and-drop PDF upload
  const uploadForm = document.querySelector('form[action="/upload_book"]');
  const fileInput = uploadForm.querySelector('input[type="file"]');

  uploadForm.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadForm.style.border = '2px dashed #1a73e8';
  });

  uploadForm.addEventListener('dragleave', () => {
      uploadForm.style.border = '2px dashed #aaa';
  });

  uploadForm.addEventListener('drop', (e) => {
      e.preventDefault();
      fileInput.files = e.dataTransfer.files;
      uploadForm.style.border = '2px dashed #aaa';
  });
});
