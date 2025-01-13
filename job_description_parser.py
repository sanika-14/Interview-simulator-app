def parse_job_description(job_description_text):
    """Parses the job description text to extract key requirements and responsibilities."""
    # Placeholder for parsed data
    parsed_data = {
        "requirements": [],
        "responsibilities": []
    }
    
    # Simple parsing logic (to be improved)
    lines = job_description_text.splitlines()
    for line in lines:
        if "requirement" in line.lower():
            parsed_data["requirements"].append(line.strip())
        elif "responsibility" in line.lower():
            parsed_data["responsibilities"].append(line.strip())
    
    return parsed_data

def extract_keywords(job_description_text):
    """Extracts keywords from the job description for better matching."""
    # Placeholder for keyword extraction logic
    keywords = set()
    words = job_description_text.split()
    for word in words:
        if len(word) > 3:  # Simple filter for keywords
            keywords.add(word.lower())
    
    return list(keywords)