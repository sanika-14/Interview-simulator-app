import streamlit as st
import speech_recognition as sr
import pyaudio
import time

class AudioTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def list_microphones(self):
        """List all available microphones"""
        p = pyaudio.PyAudio()
        info = []
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Only input devices
                info.append(f"Index {i}: {device_info['name']}")
        p.terminate()
        return info
        
    def transcribe_audio(self, device_index=None):
        """Captures and transcribes live audio with detailed feedback"""
        try:
            # If device_index is specified, use that microphone
            if device_index is not None:
                mic = sr.Microphone(device_index=device_index)
            else:
                mic = sr.Microphone()
            
            with mic as source:
                # Visual feedback
                st.info("🎤 Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Add a progress bar for recording
                st.info("🎙️ Listening... Speak now!")
                progress_bar = st.progress(0)
                
                # Record audio with timeout
                max_duration = 30  # 30 seconds max
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=max_duration)
                    st.success("Recording complete! Transcribing...")
                    
                    # Attempt transcription
                    transcription = self.recognizer.recognize_google(audio)
                    return True, transcription
                    
                except sr.WaitTimeoutError:
                    return False, "No speech detected. Please try again and speak clearly."
                except Exception as e:
                    return False, f"Recording error: {str(e)}"
                
        except Exception as e:
            return False, f"Microphone error: {str(e)}"

# Streamlit UI components
def audio_interface():
    st.title("Audio Transcription")
    
    # Initialize transcriber
    transcriber = AudioTranscriber()
    
    # List available microphones
    st.subheader("Available Microphones")
    mics = transcriber.list_microphones()
    if mics:
        st.write("Detected microphones:")
        selected_mic = st.selectbox("Select Microphone:", 
                                  range(len(mics)), 
                                  format_func=lambda x: mics[x])
    else:
        st.error("No microphones detected!")
        return
    
    # Audio controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎤 Start Recording", key="record"):
            success, result = transcriber.transcribe_audio(selected_mic)
            
            if success:
                st.session_state.last_transcription = result
                st.success("Transcription successful!")
                st.write("Transcribed text:", result)
            else:
                st.error(result)
    
    with col2:
        if st.button("📝 Use Last Transcription"):
            if hasattr(st.session_state, 'last_transcription'):
                st.write("Using transcription:", st.session_state.last_transcription)
            else:
                st.warning("No previous transcription available")

# Use this in your main app
if __name__ == "__main__":
    audio_interface()