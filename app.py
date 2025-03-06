import streamlit as st
from ats_evaluation import ats_page
from interview_preparation import interview_page
from mock_interview import mock_interview_page
import time

st.set_page_config(page_title="Smart Talent Intelligent", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["ATS Evaluation", "Interview Preparation", "Mock Interview"])

# Load the selected page
if page == "ATS Evaluation":
    ats_page()
elif page == "Interview Preparation":
    def show_flash_message():
        # Display a flash message
        st.markdown("""
            <style>
            .flash-message {
                background-color: #ffcc00;
                padding: 10px;
                color: black;
                font-size: 18px;
                text-align: center;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: fadeInOut 3s ease-out;
            }

            @keyframes fadeInOut {
                0% { opacity: 1; }
                50% { opacity: 1; }
                100% { opacity: 0; }
            }
            </style>
            <div class="flash-message">
                Take notes for better understanding!
            </div>
        """, unsafe_allow_html=True)

        # Keep the message visible for 3 seconds
        time.sleep(3)

        # Hide the message after 3 seconds
        st.empty()
    show_flash_message()
    interview_page()
elif page == "Mock Interview":
    mock_interview_page()
