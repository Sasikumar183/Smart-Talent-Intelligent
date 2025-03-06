import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import time
import re  # Added for safe JSON extraction

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


if not api_key:
    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_data
def input_pdf_text(uploaded_file):
    """Extracts text from uploaded PDF file."""
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def get_gemini_response(prompt):
    """Calls the Gemini API and ensures valid JSON response."""
    model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
    response = model.generate_content(prompt)

    if not response or not response.text:
        st.error("Error: Empty response from AI.")
        return None

    response_text = response.text.strip()

    # 🔹 Extract JSON part safely
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            st.error("Error decoding JSON. Raw AI Response:")
            st.code(response_text)
            return None
    else:
        st.error("AI did not return JSON. Raw AI Response:")
        st.code(response_text)
        return None

def generate_technical_questions(jd, resume):
    """Generates technical interview questions and answers."""
    prompt = f"""
    You are an expert technical interviewer. Analyze the following Job Description and Resume.
    
    Job Description: {jd}
    Resume: {resume}
    
    **Respond strictly in JSON format, nothing else.** Use the following structure:

    {{
        "questions": [
            {{
                "question": "Explain polymorphism in OOP.",
                "ideal_answer": "Polymorphism allows objects to be treated as instances of their parent class..."
            }},
            {{
                "question": "What is the time complexity of quicksort?",
                "ideal_answer": "Quicksort has an average time complexity of O(n log n)..."
            }}
        ]
    }}
    """

    response = get_gemini_response(prompt)
    return response.get("questions", []) if response else []

def generate_hr_questions(experience):
    """Generates HR & behavioral interview questions with detailed ideal answers."""
    prompt = f"""
    You are an experienced HR interviewer. Based on {experience} years of experience,
    generate 5 **behavioral and HR interview questions** with detailed answers.

    **Respond strictly in JSON format, nothing else.** Use the following structure:

    {{
        "questions": [
            {{
                "question": "Tell me about a time you handled a difficult situation.",
                "ideal_answer": "In my previous role, a critical project faced delays. I took initiative to adjust the timeline, reassign tasks, and communicate with stakeholders..."
            }},
            {{
                "question": "How do you handle conflicts in a team?",
                "ideal_answer": "I first understand each perspective, then facilitate open discussions to find a common solution..."
            }}
        ]
    }}
    """

    response = get_gemini_response(prompt)
    return response.get("questions", []) if response else []

def interview_page():
    """Main Interview Page"""
    st.title("AI-Powered Interview Preparation")
    
    # Step 1: Choose Interview Type
    interview_type = st.radio("Choose Interview Type", ["Technical Interview", "General HR Interview"])
    
    if interview_type == "Technical Interview":
        # Step 2: Input JD & Resume
        st.subheader("Enter Job Description")
        jd = st.text_area("Paste the Job Description here...")

        st.subheader("Upload Your Resume (PDF Only)")
        uploaded_file = st.file_uploader("Upload Resume", type="pdf")

        if uploaded_file:
            resume_text = input_pdf_text(uploaded_file)
        else:
            resume_text = None

        # Step 3: Generate Questions
        if st.button("Generate Questions"):
            if not jd or not resume_text:
                st.error("Please provide both Job Description and Resume.")
            else:
                questions = generate_technical_questions(jd, resume_text)
                st.session_state.questions = questions
                
                for q in questions:
                    st.markdown(f"**Q:** {q['question']}")
                    st.markdown(f"**Ideal Answer:** {q['ideal_answer']}")
                    st.write("---")

        # Step 4: More Questions Button
        if "questions" in st.session_state and st.session_state.questions:
            if st.button("More Questions"):
                st.session_state.questions = generate_technical_questions(jd, resume_text)
                for q in st.session_state.questions:
                    st.markdown(f"**Q:** {q['question']}")
                    st.markdown(f"**Ideal Answer:** {q['ideal_answer']}")
                    st.write("---")

    elif interview_type == "General HR Interview":
        # Step 2: Enter Experience
        experience = st.number_input("Enter Your Years of Experience", min_value=0, max_value=50, step=1)

        # Step 3: Generate HR Questions
        if st.button("Generate HR Questions"):
            if experience is None:
                st.error("Please enter your experience level.")
            else:
                hr_questions = generate_hr_questions(experience)
                st.session_state.hr_questions = hr_questions
                
                for q in hr_questions:
                    st.markdown(f"**Q:** {q['question']}")
                    st.markdown(f"**Ideal Answer:** {q['ideal_answer']}")
                    st.write("---")

        # Step 4: More HR Questions Button
        if "hr_questions" in st.session_state and st.session_state.hr_questions:
            if st.button("More HR Questions"):
                st.session_state.hr_questions = generate_hr_questions(experience)
                for q in st.session_state.hr_questions:
                    st.markdown(f"**Q:** {q['question']}")
                    st.markdown(f"**Ideal Answer:** {q['ideal_answer']}")
                    st.write("---")

# Run the Interview Page
if __name__ == "__main__":
    interview_page()
