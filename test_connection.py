import os
from google import genai

# API Key check kar rahe hain
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY environment variable set nahi hai.")
else:
    print("✅ API Key mili. Connection test kar rahe hain...")
    try:
        # Client initialize karna
        client = genai.Client(api_key=api_key)

        # Simple prompt
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Simple 5 words mein batao ki quiz game banana kaisa idea hai."
        )

        # Output
        print("\n--- Gemini Response ---")
        print(response.text.strip())
        print("-----------------------")

    except Exception as e:
        print(f"\n❌ ERROR during API call: {e}")
        print("Check karein ki aapki API Key sahi hai ya uski limit exceed toh nahi ho gayi.")