def parse_resume(resume_text):
    """Parses the resume text to extract relevant information such as skills, experiences, and qualifications."""
    # Placeholder for parsed data
    parsed_data = {
        "skills": [],
        "experiences": [],
        "qualifications": []
    }
    
    # Example parsing logic (to be implemented)
    lines = resume_text.splitlines()
    for line in lines:
        if "Skill:" in line:
            parsed_data["skills"].append(line.replace("Skill:", "").strip())
        elif "Experience:" in line:
            parsed_data["experiences"].append(line.replace("Experience:", "").strip())
        elif "Qualification:" in line:
            parsed_data["qualifications"].append(line.replace("Qualification:", "").strip())
    
    return parsed_data

def extract_skills(parsed_resume):
    """Extracts skills from the parsed resume data."""
    return parsed_resume.get("skills", [])

def extract_experience(parsed_resume):
    """Extracts experience from the parsed resume data."""
    return parsed_resume.get("experiences", [])

def extract_qualifications(parsed_resume):
    """Extracts qualifications from the parsed resume data."""
    return parsed_resume.get("qualifications", [])