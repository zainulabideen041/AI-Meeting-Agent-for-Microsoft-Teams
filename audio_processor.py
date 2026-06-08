import threading
import warnings
import queue
import re
from datetime import datetime
from time import sleep
import soundcard as sc
import numpy as np
import whisper
from notifier import send_alert
from resources import data, status_code
from utility import print_message

# Arabic/Urdu Unicode ranges. If transcription output contains these we fall
# back to task="translate" (English) instead of leaving unreadable native script.
_ARABIC_SCRIPT_RE = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')

# Suppress soundcard discontinuity warnings
try:
    from soundcard.mediafoundation import SoundcardRuntimeWarning
    warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)
except ImportError:
    pass

class AudioProcessor:
    def __init__(self):
        self.model_size = data.get('whisper_model_size', 'tiny')
        self.keywords = data.get('alert_keywords', ['attendance'])
        self.sample_rate = 16000
        self.recorder_sample_rate = 44100 # More compatible rate for Windows loopback
        self.chunk_duration = 15  # seconds to record before transcribing
        self.is_running = False
        self.model = None
        self.full_transcript = []
        # Roman-Urdu + English seed: biases Whisper to emit Roman Urdu (Latin script)
        # for Urdu speech and English for English speech, instead of native Urdu script.
        self.initial_prompt = (
            "Assalam-o-alaikum, welcome to the meeting. Aaj ka topic important hai. "
            "Let me share my screen. Theek hai, agle slide pe chalte hain. "
            "Attendance lete hain please. Can everyone hear me? Haan bilkul, awaz aa rahi hai."
        )
        # Bounded queue + single worker — prevents per-chunk threads from piling
        # up when transcription is slower than chunk_duration.
        self.chunk_queue = queue.Queue(maxsize=3)
        self.worker_thread = None
        # Progressive transcript file: opened at start, appended per chunk so
        # output survives a crash. Final consolidated save still runs at end.
        self.transcript_file = None
        self.transcript_filename = None

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

    def _open_transcript_file(self):
        self.transcript_filename = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            self.transcript_file = open(self.transcript_filename, 'w', encoding='utf-8')
            self.transcript_file.write(
                f"# Meeting transcript — started {datetime.now().isoformat(timespec='seconds')}\n\n"
            )
            self.transcript_file.flush()
            print_message(f"Writing live transcript to {self.transcript_filename}", status_code.SUCCESS)
        except Exception as e:
            print(f"[AudioProcessor] Could not open transcript file: {e}")
            self.transcript_file = None

    def _worker_loop(self):
        while self.is_running:
            try:
                chunk = self.chunk_queue.get(timeout=1)
            except queue.Empty:
                continue
            if chunk is None:
                break
            self._process_chunk(chunk)

    def start_listening(self):
        if not self.initialize_whisper():
            return

        self.is_running = True
        self._open_transcript_file()

        # Single worker thread drains the queue — no more per-chunk thread spawning.
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        print_message("Started listening for attendance (Multilingual)...", status_code.SUCCESS)

        while self.is_running:
            try:
                # Start capturing from default speaker (loopback)
                speaker = sc.default_speaker()
                # We must use get_microphone with include_loopback=True to record what is played on speakers
                mic = sc.get_microphone(id=speaker.name, include_loopback=True)

                with mic.recorder(samplerate=self.recorder_sample_rate) as recorder:
                    while self.is_running:
                        # Record a chunk
                        frames_to_record = self.recorder_sample_rate * self.chunk_duration
                        chunk = recorder.record(numframes=frames_to_record)

                        # Hand off to worker via bounded queue. If the worker is
                        # falling behind, drop the oldest pending chunk and keep
                        # the newest — better than unbounded thread pile-up.
                        try:
                            self.chunk_queue.put_nowait(chunk)
                        except queue.Full:
                            try:
                                self.chunk_queue.get_nowait()
                            except queue.Empty:
                                pass
                            try:
                                self.chunk_queue.put_nowait(chunk)
                            except queue.Full:
                                pass
                            print("[AudioProcessor] Transcription falling behind — dropped a chunk.")
            except Exception as e:
                if self.is_running:
                    print(f"[AudioProcessor] Error during recording: {e}")
                    print("[AudioProcessor] Attempting to restart recorder in 5 seconds...")
                    sleep(5)
                else:
                    break

    def _process_chunk(self, chunk):
        try:
            if chunk is None or len(chunk) < 100:
                return

            # Convert stereo to mono and ensure float32
            if chunk.ndim > 1:
                mono_audio = np.mean(chunk, axis=1).astype(np.float32)
            else:
                mono_audio = chunk.astype(np.float32)

            # Check for silent or invalid chunks
            if not np.any(mono_audio) or not np.all(np.isfinite(mono_audio)):
                return
                
            # Basic volume check (RMS)
            rms = np.sqrt(np.mean(mono_audio**2))
            if rms < 0.002: # Skip near-silence
                return
            
            # Resample to 16kHz for Whisper if needed using a more robust method
            if self.recorder_sample_rate != self.sample_rate:
                duration = len(mono_audio) / self.recorder_sample_rate
                new_num_samples = int(duration * self.sample_rate)
                if new_num_samples <= 0:
                    return
                
                # Use simple linear interpolation
                x_old = np.linspace(0, 1, len(mono_audio))
                x_new = np.linspace(0, 1, new_num_samples)
                mono_audio = np.interp(x_new, x_old, mono_audio).astype(np.float32)

            # Whisper expects at least some duration of audio
            if len(mono_audio) < 1600: # Less than 0.1s
                return

            # Transcribe the audio
            # fp16=False is essential on CPU to avoid nan issues
            # We wrap this specifically to catch internal torch/whisper errors
            try:
                result = self.model.transcribe(
                    mono_audio,
                    fp16=False,
                    language="ur",
                    initial_prompt=self.initial_prompt,
                    condition_on_previous_text=False,
                )
            except:
                # Silently ignore internal tensor errors during silent/noisy periods
                return

            text = (result.get('text') or '').strip()

            # If Roman-Urdu biasing failed and we got native Urdu script, re-run
            # the same audio in translate mode so output is at least readable.
            if text and _ARABIC_SCRIPT_RE.search(text):
                try:
                    translated = self.model.transcribe(
                        mono_audio,
                        fp16=False,
                        language="ur",
                        task="translate",
                        condition_on_previous_text=False,
                    )
                    translated_text = (translated.get('text') or '').strip()
                    if translated_text:
                        text = translated_text
                except Exception:
                    pass

            if text and len(text) > 2:
                timestamp = datetime.now().strftime('%H:%M:%S')
                line = f"[{timestamp}] {text}"
                print(f"[Transcribed] {line}")
                self.full_transcript.append(line)
                if self.transcript_file is not None:
                    try:
                        self.transcript_file.write(line + "\n")
                        self.transcript_file.flush()
                    except Exception:
                        pass
                self._check_keywords(text)
        except Exception:
            # Generic error catch for the rest of the processing
            pass

    def _check_keywords(self, text):
        for keyword in self.keywords:
            if keyword.lower() in text.lower():
                print_message(f"Alert! Keyword '{keyword}' detected in transcription.", status_code.SUCCESS)
                send_alert(keyword, text)

    def stop(self):
        self.is_running = False
        # Unblock the worker if it's waiting on the queue.
        try:
            self.chunk_queue.put_nowait(None)
        except queue.Full:
            pass
        if self.worker_thread is not None:
            self.worker_thread.join(timeout=5)
        if self.transcript_file is not None:
            try:
                self.transcript_file.write(
                    f"\n# Meeting ended {datetime.now().isoformat(timespec='seconds')}\n"
                )
                self.transcript_file.close()
            except Exception:
                pass
            self.transcript_file = None

    def save_transcript(self):
        if not self.full_transcript:
            print("[AudioProcessor] Transcript is empty. Nothing to save.")
            return

        # Live file already contains every line. Also write a consolidated copy
        # so the user always has a single canonical artifact even if the live
        # file was missed (e.g. crash before _open_transcript_file ran).
        filename = f"transcript_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Meeting transcript (final) — {datetime.now().isoformat(timespec='seconds')}\n\n")
                f.write("\n".join(self.full_transcript))
                f.write("\n")
            print_message(f"Final transcript saved to {filename}", status_code.SUCCESS)
            if self.transcript_filename:
                print_message(f"Live transcript also available at {self.transcript_filename}", status_code.SUCCESS)
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
