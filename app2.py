import streamlit as st
import fitz  # PyMuPDF
import speech_recognition as sr
import google.generativeai as genai
import time
from collections import deque

# Configure Gemini
GOOGLE_API_KEY = "your api key"  # Your API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Session state for storing resume text, chat history, and interview state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = deque(maxlen=10)  # Store last 10 interactions
if 'interview_active' not in st.session_state:
    st.session_state.interview_active = False

def parse_pdf(file_content):
    """Extracts text from a PDF file using BytesIO."""
    try:
        document = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(len(document)):
            page = document[page_num]
            text += page.get_text()
        document.close()
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def transcribe_audio():
    """Captures and transcribes live audio continuously."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            st.info("Listening... Speak now!")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)  # Listen indefinitely
            transcription = recognizer.recognize_google(audio)
            return transcription
        except sr.WaitTimeoutError:
            return None  # No speech detected
        except sr.UnknownValueError:
            return None  # Could not understand the audio
        except sr.RequestError as e:
            return f"Could not request results: {e}"

def generate_response(question: str, resume_text: str = "", job_description: str = "") -> str:
    """Generate a response using the Gemini API, assuming the role of the interviewee."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Hardcoded prompt for the AI to act as the interviewee
        prompt = f"""
        You are a candidate in a job interview. The interviewer has asked you the following question:

        Question: {question}

        Your resume information is as follows:
        {resume_text}

        The job description for the role you are applying for is:
        {job_description}

        Please respond to the interviewer's question in the first person, as if you are the candidate. 
        Use the information from your resume and the job description to craft a detailed and professional response.
        Be concise, clear, and confident in your answers. If the question is about your resume, provide specific examples 
        from your experience, education, or projects. If the question is about your skills, highlight relevant skills 
        from your resume that match the job description.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Streamlit UI
st.title("AI Interview Simulator")

# Upload Resume PDF
uploaded_file = st.file_uploader("Upload Resume PDF", type="pdf")
if uploaded_file is not None:
    resume_text = parse_pdf(uploaded_file.read())
    if resume_text.startswith("Error"):
        st.error(resume_text)
    else:
        st.session_state.resume_text = resume_text
        st.success("Resume uploaded successfully.")

# Job Description Input
job_description = st.text_area("Enter Job Description")

# Start/Stop Interview Buttons
if not st.session_state.interview_active:
    if st.button("Start Interview"):
        st.session_state.interview_active = True
        st.session_state.chat_history = deque(maxlen=10)  # Reset chat history
        st.write("Interview started. Speak into your microphone...")

if st.session_state.interview_active:
    if st.button("Stop Interview"):
        st.session_state.interview_active = False
        st.write("Interview stopped. You can start again if needed.")

# Continuously listen and respond during the interview
if st.session_state.interview_active:
    while st.session_state.interview_active:
        # Transcribe audio
        transcription = transcribe_audio()
        if transcription:
            # Add the question to chat history
            st.session_state.chat_history.append(("Interviewer", transcription))
            
            # Generate AI response (as the interviewee)
            response = generate_response(
                transcription, 
                st.session_state.get('resume_text', ''), 
                job_description
            )
            # Add AI's response to chat history
            st.session_state.chat_history.append(("Candidate", response))

            # Display only the AI's response (as the interviewee)
            st.write(f"**Candidate:** {response}")

        # Add a small delay to avoid overloading the app
        time.sleep(1)

# Option to start the interview again after stopping
if not st.session_state.interview_active:
    if st.button("Start Interview Again"):
        st.session_state.interview_active = True
        st.session_state.chat_history = deque(maxlen=10)  # Reset chat history
        st.write("Interview started again. Speak into your microphone...")
