def parse_job_description(job_description_text):
    """Parses the job description text to extract key requirements and responsibilities."""
    
    parsed_data = {
        "requirements": [],
        "responsibilities": []
    }
    
    
    lines = job_description_text.splitlines()
    for line in lines:
        if "requirement" in line.lower():
            parsed_data["requirements"].append(line.strip())
        elif "responsibility" in line.lower():
            parsed_data["responsibilities"].append(line.strip())
    
    return parsed_data

def extract_keywords(job_description_text):
    """Extracts keywords from the job description for better matching."""
 
    keywords = set()
    words = job_description_text.split()
    for word in words:
        if len(word) > 3:  
            keywords.add(word.lower())
    
    return list(keywords)
