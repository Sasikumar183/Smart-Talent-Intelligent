import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
import re
from dotenv import load_dotenv

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

def get_gemini_response(input_text, jd):
    """Calls the Gemini API for ATS evaluation."""
    try:
        models = genai.list_models()  # Placeholder function to list models
        # Assuming you can list models
        # available_models = genai.list_models()  # Example function to list models
        # available_model_names = [model.name for model in available_models]
        # st.write(f"Available models: {available_model_names}")

        # model_names = [model.name for model in models]
        # if 'gemini' not in model_names:
        #     raise ValueError("gemini-pro model is not available.")
        
        model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')

        formatted_prompt = f"""
        Hey, act as a professional ATS (Application Tracking System) with deep expertise in software engineering and data science.
        Evaluate the resume against the job description and provide an ATS evaluation strictly in JSON format.

        Resume: {input_text}
        Job Description: {jd}

        You MUST respond **only** in JSON format with NO extra text. The JSON format is:

        {{
            "JD Match": "XX%",
            "MissingKeywords": ["keyword1", "keyword2"],
            "Strengths": "Your strengths here.",
            "Areas for Improvement": "Your improvement areas here.",
            "SuggestedSkills": ["skill1", "skill2"],
            "FormattingRecommendations": "Your formatting suggestions here.",
            "ProfileSummary": "Your profile summary here.",
            "CertificateRecommendations": ["certificate1", "certificate2"]
        }}
        """

        response = model.generate_content(formatted_prompt)

        if not response or not response.text:
            st.error("Error: Empty response from API.")
            return None

        # Extract JSON response safely
        try:
            response_text = response.text.strip()
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == -1:
                raise ValueError("JSON format not found in API response.")

            json_response = response_text[json_start:json_end]
            return json.loads(json_response)

        except (json.JSONDecodeError, ValueError) as e:
            st.error(f"Error parsing JSON response: {e}")
            st.text("Raw API Response for Debugging:")
            st.code(response_text)
            return None

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def ats_page():
    """Builds the ATS Evaluation Page UI."""
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
            if uploaded_file.size > 200 * 1024 * 1024:
                st.error("File size exceeds the 200MB limit. Please upload a smaller file.")
                return

            text = input_pdf_text(uploaded_file)
            if not text:
                st.error("Error extracting text from PDF. Please upload a valid document.")
                return

            response = get_gemini_response(text, jd)
            if not response:
                st.error("Failed to fetch or parse response from Gemini API.")
                return

            # Result Display
            st.markdown('<div class="result-container">', unsafe_allow_html=True)

            # JD Match
            st.markdown("<h3>JD Match Percentage</h3>", unsafe_allow_html=True)
            score = re.sub(r'[^0-9.]', '', response.get('JD Match', '0'))
            score = float(score) if score else 0
            st.progress(int(score))
            st.markdown(f"<h1>{score:.1f}%</h1>", unsafe_allow_html=True)

            # Display other sections
            sections = [
                ("Missing Keywords", response.get("MissingKeywords", [])),
                ("Suggested Skills", response.get("SuggestedSkills", [])),
                ("Strengths", response.get("Strengths", "No strengths identified.")),
                ("Areas for Improvement", response.get("Areas for Improvement", "No areas identified.")),
                ("Formatting Recommendations", response.get("FormattingRecommendations", "No recommendations.")),
                ("Profile Summary", response.get("ProfileSummary", "No summary available.")),
                ("Certificate Recommendations", response.get("CertificateRecommendations", []))
            ]

            for title, content in sections:
                st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
                st.write(", ".join(content) if isinstance(content, list) else content)

            # Close container
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.error("Please provide both Job Description and Resume.")
