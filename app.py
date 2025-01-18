import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify
import os
import io
from audio import AudioTranscriber
from job_description_parser import parse_job_description
from resume_parser import parse_resume
import google.generativeai as genai

# Flask App
app = Flask(__name__)

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyBJRs8lWjYztXh9kPj9jkfbWMURO_4_sv0"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Global variables
transcriber = AudioTranscriber()

def parse_pdf(file):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(stream=file, filetype="pdf")  # Open the file directly from the stream
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {e}")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
    """Handle the start of an interview by processing the resume and job description."""
    resume_file = request.files.get('resume')
    job_description = request.form.get('job_description', '')

    if not resume_file or not job_description:
        return jsonify({"error": "Both resume and job description are required."}), 400

    try:
        if resume_file.filename.endswith('.pdf'):
            resume_text = parse_pdf(resume_file.read())
        else:
            return jsonify({"error": "Only PDF resumes are supported."}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing resume: {e}"}), 400

    # Parse job description
    try:
        parsed_job_description = parse_job_description(job_description)
    except Exception as e:
        return jsonify({"error": f"Error parsing job description: {e}"}), 400

    # Generate introduction using Gemini (from interviewee's perspective)
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        You are a job candidate preparing for an interview. Based on the following resume and job description, craft a professional and confident introduction for yourself as if you were speaking to the interviewer. Highlight your most relevant skills, experiences, and achievements that align with the job description.

        Resume: {resume_text}
        Job Description: {parsed_job_description}

        Your introduction should:
        1. Start with a greeting and a thank you.
        2. Briefly mention your background and key skills.
        3. Highlight 1-2 achievements or experiences that are most relevant to the job.
        4. Conclude with enthusiasm for the role and the company.

        Write the introduction in the first person (e.g., "I have experience in...").
        """
        introduction = model.generate_content(prompt).text
    except Exception as e:
        introduction = "Thank you for the opportunity to interview for this role. I’m excited to discuss how my skills and experiences align with the position."

    return render_template('interview.html', 
                           resume=resume_text, 
                           job_description=parsed_job_description,
                           introduction=introduction)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe audio from the user."""
    try:
        # Capture audio and transcribe
        transcription = transcriber.transcribe_audio()
        if transcription.get("success"):
            print("Transcription successful:", transcription.get("transcription"))  # Debugging
            return jsonify({"transcription": transcription.get("transcription")})
        else:
            print("Transcription failed:", transcription.get("error"))  # Debugging
            return jsonify({"error": transcription.get("error")}), 500
    except Exception as e:
        print("Error in /transcribe route:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST'])
def generate_response():
    """Generate a response to an interview question using Gemini."""
    try:
        # Extract data from the request
        question = request.json.get('question', '')
        resume_text = request.json.get('resume_text', '')
        job_description = request.json.get('job_description', '')

        if not question or not resume_text or not job_description:
            return jsonify({"error": "Question, resume text, and job description are required."}), 400

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        You are an interviewee in a job interview. Based on your resume and the job description, respond to the interviewer's question as if you were the candidate.

        Resume: {resume_text}
        Job Description: {job_description}

        Interviewer's Question: {question}

        Provide a concise and professional response as the interviewee:
        """
        print("Generated Prompt:", prompt)  # Debugging
        response = model.generate_content(prompt)
        print("Generated Response:", response.text)  # Debugging
        return jsonify({"response": response.text})
    except Exception as e:
        print("Error generating response:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)