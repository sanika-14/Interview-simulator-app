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
GOOGLE_API_KEY = "Your API Key"  
genai.configure(api_key=GOOGLE_API_KEY)

# Global variables
transcriber = AudioTranscriber()

def parse_pdf(file):
    """Extract text from a PDF file."""
    doc = fitz.open(stream=file, filetype="pdf")  # Open the file directly from the stream
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
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
    parsed_job_description = parse_job_description(job_description)

    return render_template('interview.html', 
                           resume=resume_text, 
                           job_description=parsed_job_description)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        transcription = transcriber.transcribe_audio()
        if transcription.get("success"):
            return jsonify({"transcription": transcription.get("transcription")})  
        else:
            return jsonify({"error": "Could not transcribe audio."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST'])
# app.py (generate_response route)
def generate_response():
    question = request.json.get('question', '')
    resume_text = request.json.get('resume_text', '')
    job_description = request.json.get('job_description', '')

    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Respond to the following interview question:
        Question: {question}
        Skills: {resume_text}
        Job: {job_description}
        """
       
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
