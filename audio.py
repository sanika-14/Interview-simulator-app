import speech_recognition as sr
import pyaudio

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def list_microphones(self):
        p = pyaudio.PyAudio()
        info = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                info.append({"index": i, "name": device_info['name']})
        p.terminate()
        return info

    def transcribe_audio(self, device_index=None):
        try:
            if device_index is not None:
                mic = sr.Microphone(device_index=device_index)
            else:
                mic = sr.Microphone()
                
            with mic as source:
                
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                return {"success": True, "transcription": self.recognizer.recognize_google(audio)}
        except sr.UnknownValueError:
            return {"success": False, "error": "Could not understand audio."}
        except sr.RequestError as e:
            return {"success": False, "error": f"Service error: {e}"}
