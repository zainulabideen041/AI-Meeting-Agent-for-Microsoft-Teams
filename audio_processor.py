import threading
import soundcard as sc
import numpy as np
import whisper
import anyascii
from notifier import send_alert
from resources import data, status_code
from utility import print_message

class AudioProcessor:
    def __init__(self):
        self.model_size = data.get('whisper_model_size', 'tiny')
        self.keywords = data.get('alert_keywords', ['attendance'])
        self.sample_rate = 16000
        self.chunk_duration = 7  # seconds to record before transcribing
        self.is_running = False
        self.model = None
        self.full_transcript = []  # List to store the complete meeting transcript

    def initialize_whisper(self):
        print_message(f"Loading Whisper {self.model_size} model...", status_code.LOADING)
        try:
            # We use the CPU specifically to save memory and avoid CUDA issues on VPS
            self.model = whisper.load_model(self.model_size, device="cpu")
            print_message(f"Whisper {self.model_size} model loaded.", status_code.SUCCESS)
            return True
        except Exception as e:
            print_message(f"Failed to load Whisper model: {e}", status_code.FAILED)
            return False

    def start_listening(self):
        if not self.initialize_whisper():
            return

        self.is_running = True
        print_message("Started listening for attendance (Multilingual)...", status_code.SUCCESS)

        # Start capturing from default speaker (loopback)
        try:
            with sc.default_speaker().recorder(samplerate=self.sample_rate) as recorder:
                while self.is_running:
                    # Record a chunk
                    frames_to_record = self.sample_rate * self.chunk_duration
                    chunk = recorder.record(numframes=frames_to_record)
                    
                    # Process the chunk in a separate thread to avoid blocks
                    threading.Thread(target=self._process_chunk, args=(chunk,)).start()
        except Exception as e:
            print(f"[AudioProcessor] Error during recording: {e}")
            self.is_running = False

    def _process_chunk(self, chunk):
        try:
            # Convert stereo to mono and ensure float32 for Whisper
            if chunk.ndim > 1:
                mono_audio = np.mean(chunk, axis=1).astype(np.float32)
            else:
                mono_audio = chunk.astype(np.float32)

            # Transcribe the audio
            # language=None allows Whisper to auto-detect the mixed language
            result = self.model.transcribe(mono_audio, fp16=False)
            original_text = result.get('text', '').strip()

            if original_text:
                # Transliterate to Roman Urdu/Hindi using anyascii
                roman_text = anyascii.anyascii(original_text)
                print(f"[Transcribed] {roman_text}")
                
                self.full_transcript.append(roman_text)
                self._check_keywords(roman_text)
        except Exception as e:
            print(f"[AudioProcessor] error processing chunk: {e}")

    def _check_keywords(self, text):
        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                print_message(f"Alert! Keyword '{keyword}' detected in transcription.", status_code.SUCCESS)
                send_alert(keyword, text)

    def stop(self):
        self.is_running = False

    def save_transcript(self):
        if not self.full_transcript:
            print("[AudioProcessor] Transcript is empty. Nothing to save.")
            return

        from datetime import datetime
        filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.full_transcript))
            print_message(f"Full transcript saved to {filename}", status_code.SUCCESS)
        except Exception as e:
            print(f"[AudioProcessor] Failed to save transcript: {e}")

def start_processor_background():
    processor = AudioProcessor()
    t = threading.Thread(target=processor.start_listening)
    t.daemon = True
    t.start()
    return processor

if __name__ == "__main__":
    # Test run
    p = AudioProcessor()
    p.start_listening()
