import os
import openai
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv(override=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ✅ Get OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️ ERROR: OpenAI API key is missing! Check your .env file.")
    exit(1)

print(f"✅ OpenAI API Key Loaded: {OPENAI_API_KEY[:5]}********")

# ✅ Initialize OpenAI Client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ✅ Define 12 Category Groups with Subcategories
CATEGORIES = {
    "Academics & Assessment": ["Assessment", "Examination", "Class, tuition fee"],
    "Workplace & Organization": ["Conflict of Interest", "Executive Board", "Procurement", "Supplier", "Staff"],
    "Discrimination & Hate": ["Discrimination", "Racism", "Ethnicity, race", "Gender", "Neurodiversity", "Ability", "Duch culture"],
    "Sexual Issues": ["Consensual", "Sexuality", "Sexual", "Harassment"],
    "Violence & Threats": ["Abuse", "Bullying", "Threats", "Violence"],
    "Legal & Ethical Issues": ["Fraud", "Theft", "Violation"],
    "Power & Authority Abuse": ["Power", "Invitation", "Gift"],
    "Religion & Beliefs": ["Religion"],
    "Privacy & Confidentiality": ["Privacy", "Confidential"],
    "Substance Use": ["Alcohol", "Drugs"],
    "Communication & Language": ["Language", "Gossip", "Report"],
    "Relationships & Interpersonal": ["Relationship"]
}

# ✅ Flatten category list for AI classification
FLATTENED_CATEGORIES = [item for sublist in CATEGORIES.values() for item in sublist]

# ✅ New Report Responses (Randomized)
NEW_REPORT_RESPONSES = [
    "This issue does not fall under our predefined categories and will be forwarded to the administrative office.",
    "This matter requires additional review. Please submit an official report to the student affairs department.",
    "Your concern does not match any existing category. A new case file will be created.",
    "The administration team will assess this issue and take appropriate action.",
    "Further verification is needed. Kindly submit this through the official reporting system."
]

@app.after_request
def after_request(response):
    """✅ Enable CORS"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/")
def home():
    """✅ Serve HTML for the homepage"""
    return render_template("index.html")

def categorize_text(user_input):
    """✅ AI-based text categorization"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that classifies user inputs into predefined categories. If the input does not fit any category, return 'New Report Required'."
                },
                {
                    "role": "user",
                    "content": f"Classify this text into one of the predefined categories: {', '.join(FLATTENED_CATEGORIES)}. If it doesn't fit, return 'New Report Required'. Input: {user_input}"
                }
            ]
        )
        category = response.choices[0].message.content.strip()

        if category in FLATTENED_CATEGORIES:
            return category, False  # ✅ Existing category
        else:
            return "The student has reported a situation that is of personal and institutional significance but does not match any existing reporting category. The concern appears to involve issues related to student experience, policy enforcement, or interpersonal conflicts that do not fit neatly into the established areas of academic, administrative, or disciplinary matters. Due to the nature of the report, further verification and assessment are required before any institutional action can be considered.", True  # ✅ New report needed

    except Exception as e:
        print(f"🚨 OpenAI API Error: {e}")
        return "Error", True

@app.route("/categorize", methods=["POST"])
def categorize():
    """✅ API Endpoint for Text Categorization"""
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        if not user_input:
            return jsonify({"error": "No input provided."}), 400

        category, is_new_report = categorize_text(user_input)

        if category == "Error":
            return jsonify({"error": "OpenAI API request failed."}), 500

        # ✅ If New Report is Required, return a random administrative message
        if is_new_report:
            admin_response = random.choice(NEW_REPORT_RESPONSES)
            return jsonify({"category": category, "message": admin_response})

        return jsonify({"category": category})

    except Exception as e:
        import traceback
        print(f"🚨 Flask Server Error: {e}")
        traceback.print_exc()  # 전체 에러 스택 트레이스 출력
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)