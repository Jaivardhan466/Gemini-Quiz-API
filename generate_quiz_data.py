import os
import json
from google import genai
from google.genai.errors import APIError

# User ke inputs (example ke liye)
USER_CLASS = "10th"
USER_SUBJECT = "Science"
USER_CHAPTER = "Life Processes"
USER_TOPIC = "Human Digestive System"  # Optional topic
USER_LANGUAGE = "Hinglish" 

# ----------------------------------------------------------------------
# 1. Structured JSON Output Schema Define Karna (FIXED)
# ----------------------------------------------------------------------

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
                                # FIX APPLIED: additionalProperties ki jagah 'properties' use kiya
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


# ----------------------------------------------------------------------
# 2. Dynamic Master Prompt Banana (REST OF THE CODE IS THE SAME)
# ----------------------------------------------------------------------

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

# ----------------------------------------------------------------------
# 3. Main Function (REST OF THE CODE IS THE SAME)
# ----------------------------------------------------------------------

def generate_content_for_game():
    """Gemini API ko call karke Notes aur Quiz data generate karta hai."""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable set nahi hai.")
        return

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"❌ ERROR: Client initialization failed: {e}")
        return

    master_prompt = create_master_prompt(
        USER_CLASS, USER_SUBJECT, USER_CHAPTER, USER_TOPIC, USER_LANGUAGE
    )
    
    print(f"✅ Master Prompt Ready. Content: {USER_CLASS}, {USER_SUBJECT}, {USER_TOPIC}")
    print("⏳ Gemini se data fetch kar rahe hain... (Ismein thoda waqt lag sakta hai)")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=master_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": OUTPUT_SCHEMA
            }
        )
        
        # 5. Output Parse aur Display karna
        quiz_data = json.loads(response.text)
        
        print("\n==============================================")
        print("✅ SUCCESS: NOTES AUR QUIZ DATA MIL GAYA HAI!")
        print("==============================================")
        
        # Notes ka ek chota sa summary dikhate hain
        print(f"\n📝 Notes Title: {quiz_data['notes']['title']}")
        print(f"   Total Sections: {len(quiz_data['notes']['sections'])}")
        
        # Quiz ka summary dikhate hain
        print(f"\n🧠 Quiz Title: {quiz_data['quiz']['quiz_title']}")
        print(f"   Total Questions: {len(quiz_data['quiz']['questions'])}")
        print("----------------------------------------------")
        
        # Optional: Print first question to verify
        first_q = quiz_data['quiz']['questions'][0]['question_text']
        print(f"First Question: {first_q}")


    except APIError as e:
        print(f"\n❌ API Error: Connection ya Quota mein issue hai. {e}")
    except json.JSONDecodeError:
        print("\n❌ JSON Parsing Error: AI ne sahi format mein output nahi diya.")
        print(f"AI Response (Raw): {response.text[:500]}...")
    except Exception as e:
        print(f"\n❌ An Unexpected Error Occurred: {e}")


# Run the main function
if __name__ == "__main__":
    generate_content_for_game()