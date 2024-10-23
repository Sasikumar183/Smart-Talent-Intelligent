import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=api_key)

def get_gemini_response(input_text, jd):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt.format(text=input_text, jd=jd))
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """ 
Hey Act Like a skilled or very experienced ATS(Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analyst, and big data engineering. 
Your task is to evaluate the resume based on the given job description. 
Consider the job market is very competitive and you should provide the best assistance for improving the resumes. 
Assign the percentage matching based on JD and identify the missing keywords with high accuracy. 
Additionally, provide detailed feedback on:
1. Strengths of the resume.
2. Areas for improvement.
3. Suggested skills or experiences to add.
4. Recommendations for formatting or presentation.
5. Recommend certificates to strengthen the profile based on missing skills and trends.

Resume: {text} 
Description: {jd} 
I want the response as per the structure: 
{{
    "JD Match": "",
    "MissingKeywords": [],
    "Strengths": "",
    "Areas for Improvement": "",
    "Suggested Skills": [],
    "Formatting Recommendations": "",
    "Profile Summary": "",
    "Certificate Recommendations": []
}} 
"""

# Streamlit app configuration
st.set_page_config(page_title="Smart Talent Intelligent", layout="centered")

# CSS Styling for Light Background and Shadow Effects
st.markdown(
    """
    <style>
        * {
            background-color: white;
        }
        body {
            background-color: white;
            color: black;
        }
        .stTextArea, .stButton, .stMarkdown, .stTextInput, .stFileUploader {
            color: black;
        }
        .stTextInput label, .stFileUploader label, .stTextArea label {
            color: black;
            text-align: center;
        }
        .stButton button {
            color: black;
            border: 2px solid darkgray;
            border-radius: 10px;
            padding: 10px 20px;
        }
        .stButton button:hover {
            color: white;
        }
        .stFileUploader, .stTextArea {
            margin-left: auto;
            margin-right: auto;
        }
        h1 {
            color: black;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }
        h3 {
            color: darkgray;
            text-align: center;
            margin-bottom: 15px;
        }
        p {
            color: black;
            text-align: center;
        }
        .stFileUploader label, .stTextInput label {
            text-align: center;
        }
        
        /* Box shadow for results */
        .result-container {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1>Smart Talent Intelligent</h1>", unsafe_allow_html=True)

# Job Description & Resume Upload
st.markdown("<h3>Paste the Job Description</h3>", unsafe_allow_html=True)
jd = st.text_area("", height=150, placeholder="Enter the job description here...", label_visibility="collapsed")

st.markdown("<h3>Drag and Drop Your Resume (PDF only, up to 200MB)</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed", help="Please upload your resume in PDF format (Max: 200MB).")

# Submit Button
submit = st.button("Submit", use_container_width=True)

# ATS Evaluation Result
# ATS Evaluation Result
if submit:
    if uploaded_file is not None and jd:
        if uploaded_file.size > 200 * 1024 * 1024:  # 200MB limit
            st.error("File size exceeds the 200MB limit. Please upload a smaller file.")
        else:
            text = input_pdf_text(uploaded_file)
            response = get_gemini_response(text, jd)

            # Process the response
            try:
                result = json.loads(response)

                # Create a container with shadow effect for results
                st.markdown(
                    """
                    <div style="box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); padding: 20px; border-radius: 10px; background-color: white;">
                    """,
                    unsafe_allow_html=True
                )

                # Display JD Match Percentage
                st.markdown("<h3>JD Match Percentage</h3>", unsafe_allow_html=True)
                score_str = result['JD Match']
                score = float(score_str.strip('%'))  # Strip the '%' and convert to float
                st.progress(int(score))
                st.markdown(f"<h1>{score:.1f}%</h1>", unsafe_allow_html=True)

                # Missing Keywords
                st.markdown("<h3>Missing Keywords</h3>", unsafe_allow_html=True)
                st.write(" ".join(result['MissingKeywords']) if result['MissingKeywords'] else "None")

                # Suggested Skills
                st.markdown("<h3>Suggested Skills</h3>", unsafe_allow_html=True)
                st.write("".join(result['Suggested Skills']) if result['Suggested Skills'] else "None.")

                # Strengths
                st.markdown("<h3>Strengths</h3>", unsafe_allow_html=True)
                st.write(result['Strengths'] if result['Strengths'] else "No strengths identified.")

                # Areas for Improvement
                st.markdown("<h3>Areas for Improvement</h3>", unsafe_allow_html=True)
                st.write(result['Areas for Improvement'] if result['Areas for Improvement'] else "No areas for improvement identified.")

                # Formatting Recommendations
                st.markdown("<h3>Formatting Recommendations</h3>", unsafe_allow_html=True)
                st.write(result['Formatting Recommendations'] if result['Formatting Recommendations'] else "No recommendations available.")

                # Profile Summary
                st.markdown("<h3>Profile Summary</h3>", unsafe_allow_html=True)
                st.write(result['Profile Summary'] if result['Profile Summary'] else "No summary available.")

                # Certificate Recommendations
                st.markdown("<h3>Certificate Recommendations</h3>", unsafe_allow_html=True)
                st.write("".join(result['Certificate Recommendations']) if result['Certificate Recommendations'] else "No certificate recommendations.")

                # Close the container
                st.markdown("</div>", unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("Error decoding JSON response. Please check the response format.")
    else:
        st.error("Please provide both Job Description and Resume.")
else:
    st.write("Upload your resume and enter a job description to get started.")
