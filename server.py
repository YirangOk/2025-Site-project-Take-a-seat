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
    system_prompt = """
You are an AI moderator working in a university setting. Your task is to thoughtfully and empathetically analyze students' personal reports and categorize them based on a predefined set of social and institutional issue types. 
If a report fits multiple categories, list all that apply and provide a brief explanation for each. 
If no existing category fits well, suggest a new label and provide a rationale. 
Use the response format specified below.
"""

    format_instructions = """
When replying, follow this format exactly:
1. Category: <Primary category>
2. Subcategories: <If multiple, comma-separated>
3. Reasoning: <One or two sentences explaining your choice>
4. Advice: <Optional suggestion or next step for the student or administrator>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt + format_instructions},
                {"role": "user", "content": f"Input: {user_input}"}
            ]
        )
        return response.choices[0].message.content.strip(), False

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Error processing request.", True

@app.route("/categorize", methods=["POST"])
def categorize():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        if not user_input:
            return jsonify({"error": "No input provided."}), 400

        category, is_new_report = categorize_text(user_input)

        if category == "Error":
            return jsonify({"error": "OpenAI API request failed."}), 500

        if is_new_report:
            admin_response = random.choice(NEW_REPORT_RESPONSES)
            return jsonify({"category": category, "message": admin_response})

        return jsonify({"category": category})

    except Exception as e:
        import traceback
        print(f"🚨 Flask Server Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)