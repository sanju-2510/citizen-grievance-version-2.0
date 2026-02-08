import re

SECTOR_KEYWORDS = {
    'Roads': ['road', 'pothole', 'street', 'highway', 'traffic', 'paving', 'tar'],
    'Electricity': ['power', 'electricity', 'light', 'current', 'transformer', 'voltage', 'blackout', 'wire'],
    'Water': ['water', 'drainage', 'sewage', 'leak', 'pipe', 'pipeline', 'tank', 'drinking'],
    'Health': ['hospital', 'doctor', 'medicine', 'disease', 'outbreak', 'clinic', 'medical', 'emergency', 'ambulance'],
    'Education': ['school', 'college', 'teacher', 'student', 'book', 'scholarship', 'university', 'education'],
    'Welfare': ['pension', 'ration', 'subsidy', 'scheme', 'poverty', 'low income', 'housing'],
    'Law & Order': ['police', 'crime', 'theft', 'safety', 'harassment', 'security', 'patrol', 'illegal']
}

PRIORITY_RULES = {
    'High': ['emergency', 'danger', 'death', 'accident', 'blood', 'outbreak', 'crime', 'safety', 'immediate', 'urgent', 'critical'],
    'Medium': ['blocked', 'leak', 'broken', 'repair', 'issue', 'not working', 'daily', 'infrastructure', 'utility'],
    'Low': ['feedback', 'suggestion', 'request', 'improvement', 'information', 'delay']
}

def detect_sector(text):
    if not text or not isinstance(text, str):
        return "Welfare"
    text = text.lower()
    scores = {sector: 0 for sector in SECTOR_KEYWORDS}
    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', text):
                scores[sector] += 1
    
    max_score = max(scores.values())
    if max_score > 0:
        return [s for s, score in scores.items() if score == max_score][0]
    return "Welfare" # Default

def detect_priority(text):
    if not text or not isinstance(text, str):
        return "Medium"
    text = text.lower()
    for priority, keywords in PRIORITY_RULES.items():
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', text):
                return priority
    return "Medium" # Default

def get_cluster_id(pincode, sector):
    # Simple cluster ID generation
    return f"CL-{pincode}-{sector.replace(' ', '').upper()}"
