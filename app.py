import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify, redirect, session, flash
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
from firebase_config.firebase import signup_user, verify_token
import google.generativeai as genai
from audio import AudioTranscriber
from job_description_parser import parse_job_description
from resume_parser import parse_resume
from rich import _console
import firebase_admin

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "# Replace with your actual secret key"  

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

# Configure Gemini
GOOGLE_API_KEY = "# Replace with your actual API key"  
genai.configure(api_key=GOOGLE_API_KEY)

# Global variables
transcriber = AudioTranscriber()
@app.route("/", methods=["GET", "POST"])
def login_signup():
    """Login or Signup Page."""
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email")
        password = request.form.get("password")

        if action == "signup":
            result = signup_user(email, password)  # Ensure signup_user() is implemented properly
            if result["success"]:
                session["user_id"] = result["uid"]
                print("Session user_id:", session.get("user_id"))
                return redirect("/upload")
            else:
                return render_template("index.html", error=result["error"])

        elif action == "login":
            id_token = request.form.get("id_token")  # Frontend sends the Firebase ID token
            result = verify_token(id_token)
            if result["success"]:
                session["user_id"] = result["uid"]
                _console.log("Session user_id:", session.get("user_id"))
                return redirect("/upload")
            else:
                return render_template("index.html", error="Invalid credentials. Please try again.")

    return render_template("index.html")

@app.route("/verify_token", methods=["POST"])
def verify_token_route():
    """Verify Firebase token"""
    data = request.get_json()
    id_token = data.get("idToken")
    
    try:
        # Verify token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        
        # Store user_id in session
        session["user_id"] = user_id
        print("User ID in session:", session.get("user_id"))  # Debugging line
        
        return jsonify({"success": True})
    except Exception as e:
        print("Error verifying token:", e)  # Debugging line
        return jsonify({"success": False, "error": str(e)})

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle Forgot Password functionality"""
    if request.method == "POST":
        email = request.form["email"]
        
        try:
            # Send password reset email using Firebase
            auth.send_password_reset_email(email)
            flash("Password reset link sent to your email address.", "success")
            return redirect("/")
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/forgot-password")
        
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Handle Reset Password functionality"""
    if request.method == "POST":
        oob_code = request.form["oobCode"]
        new_password = request.form["new_password"]
        
        try:
            # Reset password using the reset code and new password
            auth.confirm_password_reset(oob_code, new_password)
            flash("Password has been successfully reset.", "success")
            return redirect("/login")
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/forgot-password")
    
    # Ensure the oobCode is passed as part of the query string
    oob_code = request.args.get('oobCode')
    if oob_code:
        return render_template("reset_password.html", oobCode=oob_code)
    else:
        flash("Invalid reset link.", "danger")
        return redirect("/forgot-password")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Resume and Job Description Upload Page."""
    if "user_id" not in session:
        return redirect("/")  # Redirect to login if not authenticated

    if request.method == "POST":
        resume_file = request.files.get("resume")
        job_description = request.form.get("job_description", "")

        if not resume_file or not job_description:
            return jsonify({"error": "Both resume and job description are required."}), 400

        try:
            if resume_file.filename.endswith(".pdf"):
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

        return render_template("dashboard.html", resume=resume_text, job_description=parsed_job_description)

    return render_template("dashboard.html")

@app.route("/start_interview", methods=["POST"])
def start_interview():
    """Handle the start of an interview by processing the resume and job description."""
    if "user_id" not in session:
        return redirect("/")  # Redirect to login if not authenticated

    resume_text = request.form.get("resume_text", "")
    job_description = request.form.get("job_description", "")

    # Generate introduction using Gemini (from interviewee's perspective)
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are a job candidate preparing for an interview. Based on the following resume and job description, craft a professional and confident introduction for yourself as if you were speaking to the interviewer. Highlight your most relevant skills, experiences, and achievements that align with the job description.

        Resume: {resume_text}
        Job Description: {job_description}

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

    return render_template(
        "interview.html",
        resume=resume_text,
        job_description=job_description,
        introduction=introduction,
    )

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        transcription = transcriber.transcribe_audio()
        if transcription.get("success"):
            return jsonify({"transcription": transcription.get("transcription")})  # Ensure transcription text is returned
        else:
            return jsonify({"error": "Could not transcribe audio."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST'])
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
        # Reduced prompt length to only necessary data
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    """Logout user."""
    session.pop("user_id", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

