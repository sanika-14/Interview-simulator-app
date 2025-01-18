import speech_recognition as sr
import pyaudio

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def list_microphones(self):
        """List all available microphones."""
        p = pyaudio.PyAudio()
        info = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Only input devices
                info.append(f"Index {i}: {device_info['name']}")
        p.terminate()
        return info

    def transcribe_audio(self, device_index=None):
        """Captures and transcribes live audio."""
        try:
            # Use the specified microphone or the default one
            if device_index is not None:
                mic = sr.Microphone(device_index=device_index)
            else:
                mic = sr.Microphone()

            with mic as source:
                print("Adjusting for ambient noise...")  # Debugging
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening... Speak now!")  # Debugging

                # Record audio with a timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=30)
                print("Recording complete! Transcribing...")  # Debugging

                # Attempt transcription
                transcription = self.recognizer.recognize_google(audio)
                print("Transcription:", transcription)  # Debugging
                return {"success": True, "transcription": transcription}

        except sr.WaitTimeoutError:
            print("No speech detected. Please try again and speak clearly.")  # Debugging
            return {"success": False, "error": "No speech detected."}
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")  # Debugging
            return {"success": False, "error": "Could not understand audio."}
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")  # Debugging
            return {"success": False, "error": "Service unavailable."}
        except Exception as e:
            print(f"Error during transcription: {e}")  # Debugging
            return {"success": False, "error": str(e)}