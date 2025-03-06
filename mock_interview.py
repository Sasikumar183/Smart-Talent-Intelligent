import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
from gtts import gTTS  # Google Text-to-Speech
import pygame  # For playing audio and animations
from PIL import Image, ImageSequence  # For animating the AI avatar

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=api_key)

# Initialize pygame for audio and animations
pygame.init()


def speak_text(text):
    """Convert text to speech using gTTS and play it with mouth animation."""
    # Generate speech audio
    tts = gTTS(text, lang="en")
    tts.save("ai_speech.mp3")

    # Play audio
    pygame.mixer.music.load("ai_speech.mp3")
    pygame.mixer.music.play()

    # Simulate mouth movement while audio is playing using GIF
    start_time = time.time()
    gif_url = "https://medjia0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXNqM3hjdXlyMHNtaGxjNjZvZGlxaWxmeXMwaThmcDR6M3dkZnh4YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1hB0xK2KOTe7QzdABC/giphy.gif"
    
    while pygame.mixer.music.get_busy():
        elapsed_time = time.time() - start_time
        if int(elapsed_time * 2) % 2 == 0:  # Show GIF
            st.image(gif_url, caption="AI Speaking", use_column_width=True)
        time.sleep(0.2)  # Control the speed of mouth movement


def get_mock_interview_question(job_role, company_name):
    """Generates concise AI-powered interview questions based on job role and company."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are an AI interviewer conducting an interview for a {job_role} position at {company_name}.
    
    Generate a single concise and clear interview question that is relevant to the role, with a short ideal expected answer.
    Format the response in JSON:

    {{
        "question": "What is your experience with cloud computing?",
        "ideal_answer": "Cloud computing involves using remote servers for storage and processing."
    }}
    """
    
    response = model.generate_content(prompt)

    try:
        return response.json()
    except:
        return {"question": "Tell me about your strengths.", "ideal_answer": "I am adaptable, a problem solver, and a team player."}

def get_mock_interview_feedback(question, answer):
    """AI evaluates the user's answer and provides concise feedback."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Evaluate the following interview response briefly:\n\n**Question:** {question}\n**Answer:** {answer}\n\nProvide short, clear feedback with strengths and areas for improvement."
    response = model.generate_content(prompt)
    return response.text.strip()  # Ensure no extra whitespace

def mock_interview_page():
    """AI Mock Interview with animated speaking AI."""
    st.title("🎭 AI Mock Interview")

    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
        st.session_state.responses = []
        st.session_state.current_question_number = 0

    if not st.session_state.interview_started:
        # Step 1: Gather Interview Details
        st.subheader("📄 Interview Setup")

        job_role = st.text_input("Enter Job Role (e.g., Software Engineer)")
        job_description = st.text_area("Paste Job Description")
        company_name = st.text_input("Enter Company Name")

        duration = st.selectbox("Select Interview Duration", ["5 min", "10 min", "15 min", "20 min", "Custom"])
        if duration == "Custom":
            custom_duration = st.number_input("Enter Custom Duration (in minutes)", min_value=1, max_value=60, step=1)
            duration = f"{custom_duration} min"

        if st.button("🚀 Start Interview"):
            if not job_role or not job_description or not company_name:
                st.error("Please fill in all fields before starting the interview.")
                return

            st.session_state.interview_started = True
            st.session_state.total_questions = int(duration.split()[0])  # Convert duration to number of questions
            st.session_state.current_question = None
            st.session_state.job_role = job_role
            st.session_state.company_name = company_name
            st.rerun()  # Refresh the page to hide setup and start interview

    else:
        # Step 2: Conduct the Mock Interview
        st.subheader("🎤 AI Mock Interview Session")
        interview_container = st.empty()  # Placeholder for interview UI

        with interview_container.container():
            if st.session_state.current_question_number < st.session_state.total_questions:
                if not st.session_state.current_question:
                    # Generate New Question
                    question_data = get_mock_interview_question(st.session_state.job_role, st.session_state.company_name)
                    st.session_state.current_question = question_data["question"]
                    st.session_state.ideal_answer = question_data["ideal_answer"]

                st.subheader(f"📝 Question {st.session_state.current_question_number + 1}")
                st.write(f"**{st.session_state.current_question}**")

                # AI Speaks the Question with Mouth Animation
                speak_text(st.session_state.current_question)

                # Allow Text or Voice Response
                user_answer = st.text_area("Enter Your Answer")

                if st.button("➡️ Submit Answer"):
                    if not user_answer:
                        st.error("Please provide an answer.")
                    else:
                        feedback = get_mock_interview_feedback(st.session_state.current_question, user_answer)
                        st.session_state.responses.append({
                            "question": st.session_state.current_question,
                            "user_answer": user_answer,
                            "feedback": feedback
                        })

                        # Display AI Feedback
                        st.subheader("🔍 AI Feedback")
                        st.write(feedback)
                        speak_text(feedback)  # AI speaks feedback with mouth animation

                        # Move to next question
                        st.session_state.current_question_number += 1
                        st.session_state.current_question = None  # Reset to generate new question
                        time.sleep(2)  # Pause before next question
                        st.rerun()  # Refresh for next question

            else:
                # Step 3: Interview Summary
                st.subheader("🎯 Interview Summary")
                for i, response in enumerate(st.session_state.responses):
                    st.markdown(f"**Q{i+1}: {response['question']}**")
                    st.markdown(f"**Your Answer:** {response['user_answer']}")
                    st.markdown(f"**AI Feedback:** {response['feedback']}")
                    st.write("---")

                st.subheader("🏆 Final Insights")
                st.write("**Key Strengths:** Based on your responses, you showed strong problem-solving skills and adaptability.")
                st.write("**Areas for Improvement:** Consider providing more structured answers with examples.")

                speak_text("The interview is now complete. Here are your final insights. Thank you for practicing!")

                # Reset Session State
                if st.button("🔄 Restart Interview"):
                    st.session_state.clear()
                    st.rerun()
