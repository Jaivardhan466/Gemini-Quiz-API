import os
import json
from flask import Flask, request, jsonify
from google import genai
from google.genai.errors import APIError

# Humari existing logic ko yahan paste karna hoga, ya import karna hoga.
# Abhi ke liye, hum Master Prompt aur Schema ko yahan copy kar rahe hain.

# Note: Acha practice yeh hai ki hum master_prompt aur OUTPUT_SCHEMA ko import karein, 
# lekin simplicity ke liye, abhi hum unhe yahan paste kar rahe hain.
# ORIGINAL CODE se copy karein:

# [COPY START: OUTPUT_SCHEMA se lekar create_master_prompt function tak ka sara code paste karein]
# (OUTPUT_SCHEMA aur create_master_prompt function ko yahan paste karein)
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "notes": {
            "type": "object",
            "description": "Structured study notes for the given topic.",
            "properties": {
                "title": {"type": "string", "description": "Notes ka main title."},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section_title": {"type": "string"},
                            "points": {
                                "type": "array",
                                "items": {"type": "string", "description": "Key facts in bullet points."}
                            }
                        },
                        "required": ["section_title", "points"]
                    }
                }
            },
            "required": ["title", "sections"]
        },
        "quiz": {
            "type": "object",
            "description": "10 Multiple Choice Questions (MCQs) based ONLY on the generated notes.",
            "properties": {
                "quiz_title": {"type": "string", "description": "Quiz ka title."},
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question_text": {"type": "string"},
                            "options": {
                                "type": "object",
                                "description": "A, B, C, D options",
                                "properties": { 
                                    "A": {"type": "string"},
                                    "B": {"type": "string"},
                                    "C": {"type": "string"},
                                    "D": {"type": "string"}
                                },
                                "required": ["A", "B", "C", "D"]
                            },
                            "correct_key": {"type": "string", "description": "Correct option key (A, B, C, ya D)"}
                        },
                        "required": ["question_text", "options", "correct_key"]
                    }
                }
            },
            "required": ["quiz_title", "questions"]
        }
    },
    "required": ["notes", "quiz"]
}

def create_master_prompt(class_val, subject_val, chapter_val, topic_val, lang_val):
    """Sare user inputs ko lekar ek detailed prompt banata hai."""
    topic_focus = f"aur specific topic **'{topic_val}'** par focus karo." if topic_val else "lekin poore chapter ko cover karo."

    prompt = f"""
    Aapko Class {class_val}, Subject {subject_val}, aur Chapter '{chapter_val}' se relevant information internet se nikaalni hai, {topic_focus}.

    Aapka output strictly **do JSON objects** mein hona chahiye (jaisa ki schema mein define kiya gaya hai):
    1. Ek object mein detailed, structured **Study Notes** honge.
    2. Doosre object mein, un **Notes** par based **10 Multiple Choice Questions (MCQs)** honge.

    Saara content (Notes, Questions, Options, Titles) **{lang_val}** mein hona chahiye.
    """
    return prompt
# [COPY END]

# ----------------------------------------------------------------------
# FLASK SERVER SETUP
# ----------------------------------------------------------------------

app = Flask(__name__)

# API Key Check
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("FATAL ERROR: GEMINI_API_KEY environment variable is NOT set.")
else:
    print("Flask server starting. API Key confirmed.")
    client = genai.Client(api_key=API_KEY)


@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    """Client (App) se JSON input lekar AI content generate karta hai."""
    
    # 1. Input Data Lena (From Front-End App)
    data = request.get_json()
    
    # Required Inputs
    class_val = data.get('class')
    subject_val = data.get('subject')
    chapter_val = data.get('chapter')
    lang_val = data.get('language', 'Hinglish') # Default to Hinglish
    
    # Optional Input
    topic_val = data.get('topic', '') 

    # Input Validation
    if not all([class_val, subject_val, chapter_val]):
        return jsonify({"error": "Missing class, subject, or chapter input."}), 400

    # 2. Master Prompt Banana
    master_prompt = create_master_prompt(class_val, subject_val, chapter_val, topic_val, lang_val)

    # 3. AI Call Karna
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=master_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": OUTPUT_SCHEMA
            }
        )
        
        # 4. JSON Output Ko Parse Karke Wapas Bhejna
        quiz_data = json.loads(response.text)
        return jsonify(quiz_data), 200 # Success, data client ko wapas bhejo

    except APIError as e:
        # Agar API key ya connection mein problem ho
        return jsonify({"error": f"API Error: {e}"}), 500
    except Exception as e:
        # Koi aur error (jaise JSON parsing)
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    # Server start karna
    print("Server running on http://127.0.0.1:5000/ - Ready to serve /generate_quiz")
    app.run(debug=True) # debug=True se changes automatically load ho jaate hain