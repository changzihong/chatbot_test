import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# --- Load .env locally (ignored on Streamlit Cloud) ---
load_dotenv()

# --- Get API Key from .env or Streamlit Secrets ---
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ No API key found. Please set GOOGLE_API_KEY in .env (local) or in Streamlit Cloud → Secrets.")
else:
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # --- Streamlit UI ---
    st.set_page_config(page_title="University Chatbot", page_icon="🎓")

    st.title("🎓 University Life Chatbot")
    st.write("Ask me anything about university life!")

    # Store chat history
    if "history" not in st.session_state:
        st.session_state["history"] = []

    # --- Display existing chat history ---
    for chat in st.session_state["history"]:
        with st.chat_message("user"):
            st.markdown(chat["user"])
        with st.chat_message("assistant"):
            st.markdown(chat["bot"])

    # --- New user input (chat style) ---
    user_input = st.chat_input("Type your question...")

    if user_input:
        # Display user message instantly
        with st.chat_message("user"):
            st.markdown(user_input)

        # --- Custom Knowledge (Rule-based first) ---
        faq = {
            "where is the library": "📚 The library is located in the Main Building, 2nd floor.",
            "how do i register for exams": "📝 You can register for exams via the Student Portal under 'Academics > Exam Registration'.",
            "what is the cafeteria menu": "🍽️ The cafeteria offers both vegetarian and non-vegetarian meals, updated daily on the portal.",
            "who is the dean": "🎓 The Dean is Prof. Dr. Sarah Tan from the Faculty of Information Technology.",
            "how do i access wifi": "📶 Connect to 'Campus-WiFi' and log in using your student ID and password."
        }

        response = None
        for q, ans in faq.items():
            if q in user_input.lower():
                response = ans
                break

        # --- If no custom answer, fallback to Gemini ---
        if not response:
            try:
                response = model.generate_content(user_input).text
            except Exception as e:
                response = f"⚠️ Error using Gemini API: {str(e)}"

        # Display bot message
        with st.chat_message("assistant"):
            st.markdown(response)

        # Save to history
        st.session_state["history"].append({"user": user_input, "bot": response})
