import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
import re
from dotenv import load_dotenv
import ast  # For safer JSON parsing

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

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

def get_gemini_response(input_text, jd):
    """Calls the Gemini API for ATS evaluation."""
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt.format(text=input_text, jd=jd))
    return response.text

# Improved Prompt Template (Crucial!)
input_prompt = """ 
Hey, act like a skilled ATS (Application Tracking System) with deep expertise in tech fields like software engineering, data science, and big data. 
Evaluate the resume against the job description, assign a JD match percentage, and provide detailed feedback.

Resume: {text} 
Description: {jd} 

Response format (JSON):  Strictly adhere to the following JSON structure.  Do not include any text outside the JSON object.

```json
{{
    "JD Match": "Percentage (e.g., 85%)",  // Include the percentage symbol
    "MissingKeywords": ["keyword1", "keyword2", ...], // Array of strings
    "Strengths": "Summary of strengths", // String
    "Areas for Improvement": "Areas for improvement", // String
    "Suggested Skills": ["skill1", "skill2", ...], // Array of strings
    "Formatting Recommendations": "Formatting advice", // String
    "Profile Summary": "Summary of the profile", // String
    "Certificate Recommendations": ["cert1", "cert2", ...] // Array of strings
}}"""

def ats_page():
    """Streamlit UI for ATS Evaluation."""

    # CSS Styling
    st.markdown("""
        <style>
            h1, h3, p { text-align: center; }
            .result-container { padding: 20px; border-radius: 10px; background: #f8f9fa; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.markdown("<h1>Smart Talent Intelligent</h1>", unsafe_allow_html=True)

    # Job Description & Resume Upload
    st.markdown("<h3>Paste the Job Description</h3>", unsafe_allow_html=True)
    jd = st.text_area("", height=150, placeholder="Enter the job description here...", label_visibility="collapsed")

    st.markdown("<h3>Upload Your Resume (PDF only, max 200MB)</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed", help="Upload resume in PDF format (Max: 200MB).")

    # Submit Button
    submit = st.button("Submit", use_container_width=True)

    if submit:
        if uploaded_file and jd:
            if uploaded_file.size > 200 * 1024 * 1024:  # 200MB limit
                st.error("File size exceeds the 200MB limit. Please upload a smaller file.")
                return

            text = input_pdf_text(uploaded_file)
            if not text:
                st.error("Error extracting text from PDF. Please upload a valid document.")
                return

            response = get_gemini_response(text, jd)
            
            try:
                result = json.loads(response)

                # Result Display Container
                st.markdown('<div class="result-container">', unsafe_allow_html=True)

                # JD Match Percentage
                st.markdown("<h3>JD Match Percentage</h3>", unsafe_allow_html=True)
                score = re.sub(r'[^0-9.]', '', result.get('JD Match', '0'))  # Remove non-numeric chars
                score = float(score) if score else 0
                st.progress(int(score))
                st.markdown(f"<h1>{score:.1f}%</h1>", unsafe_allow_html=True)

                # Display Other Results
                sections = [
                    ("Missing Keywords", result.get("MissingKeywords", [])),
                    ("Suggested Skills", result.get("Suggested Skills", [])),
                    ("Strengths", result.get("Strengths", "No strengths identified.")),
                    ("Areas for Improvement", result.get("Areas for Improvement", "No areas identified.")),
                    ("Formatting Recommendations", result.get("Formatting Recommendations", "No recommendations.")),
                    ("Profile Summary", result.get("Profile Summary", "No summary available.")),
                    ("Certificate Recommendations", result.get("Certificate Recommendations", []))
                ]

                for title, content in sections:
                    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
                    st.write(", ".join(content) if isinstance(content, list) else content)

                # Close Container
                st.markdown("</div>", unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("Error decoding JSON response. Please check the response format.")
        else:
            st.error("Please provide both Job Description and Resume.")

