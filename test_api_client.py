import requests
import json

# Jo inputs hum Front-End App se bhejte
INPUT_DATA = {
    "class": "10th",
    "subject": "History",
    "chapter": "The Rise of Nationalism in Europe",
    "topic": "The French Revolution and the Idea of the Nation", # New topic to test!
    "language": "Hinglish"
}

# Humara local API endpoint
API_URL = "http://127.0.0.1:5000/generate_quiz"

print(f"🚀 Sending request for: {INPUT_DATA['topic']}...")
print("⏳ Waiting for AI to generate content...")

try:
    # POST request bhejo
    response = requests.post(API_URL, json=INPUT_DATA)

    # Status check karo
    if response.status_code == 200:
        # Success!
        data = response.json()
        
        print("\n==============================================")
        print("✅ API TEST SUCCESSFUL!")
        print("==============================================")
        print(f"📝 Notes Title: {data['notes']['title']}")
        print(f"🧠 Quiz Questions: {len(data['quiz']['questions'])} questions generated.")
        print(f"First Question: {data['quiz']['questions'][0]['question_text'][:50]}...")
        print("----------------------------------------------")
    else:
        # Error (jaise 500 ya 400)
        print(f"\n❌ API Failed with Status Code: {response.status_code}")
        print("Error Response:")
        print(response.json().get('error', 'No detailed error message.'))

except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR: Ensure 'app.py' server is running in another terminal.")
except Exception as e:
    print(f"\n❌ AN UNEXPECTED ERROR OCCURRED: {e}")