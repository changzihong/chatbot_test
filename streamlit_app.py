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
    st.write("Hey there! I'm Alex. Ask me anything about university life!")

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
        # This part handles super common questions fast and accurately.
        faq = {
            "what are the best study spots": "🤫 The library's quiet zones are great, especially the ones on the top floor. But if you need some background noise, I love studying at the campus coffee shop!",
            "how do i join a club": "🎉 You can find all the clubs at the annual Clubs & Societies Fair during orientation week. It's a bit overwhelming, but it's the best way to see all the options and sign up!",
            "where can i find cheap food": "🍕 The food court near the West Gate is known for its affordable and diverse stalls. The pizza place there is a personal favorite for a quick and cheap slice!",
            "how do i meet new people": "🤝 Honestly, just by showing up! Join a club or a sports team, volunteer for an event, or just hang out in the common areas. Everyone is in the same boat, so just be open and friendly!",
            "what is the campus shuttle schedule": "🚌 The campus shuttle runs pretty often on weekdays, but the schedule can be a bit tricky to memorize. I usually just check the university's official app for the live tracker. It saves a ton of time!",
            "how do i talk to my professor": "🤔 Don't be intimidated! Most professors have office hours and they're usually happy to help. Just send them a quick email to ask if you can stop by to chat about the class or a topic you're interested in.",
            "what should i do if i feel homesick": "🫂 It's totally normal to feel that way! I felt it too. My advice? Call your family, video chat with old friends, and get involved in campus life. Distracting yourself by trying something new can really help."
        }

        response = None
        for q, ans in faq.items():
            if q in user_input.lower():
                response = ans
                break

        # --- If no custom answer, fallback to Gemini ---
        if not response:
            try:
                # This is where we tell the AI to act like me (Alex) and stay on topic.
                prompt_with_persona = (
                    "You are an experienced and empathetic university student named Alex. "
                    "Your purpose is to provide guidance, advice, and support to new and current university students. "
                    "You have a friendly, encouraging, and knowledgeable tone. You can draw from your own 'experiences' "
                    "to offer realistic and practical advice. If the user asks a question that is not related to "
                    "university life, politely but firmly inform them that you can only answer questions "
                    "about university life, as that's your area of expertise."
                    f"The user's question is: '{user_input}'"
                )
                response = model.generate_content(prompt_with_persona).text
            except Exception as e:
                response = f"⚠️ Error using Gemini API: {str(e)}"

        # Display bot message
        with st.chat_message("assistant"):
            st.markdown(response)

        # Save to history
        st.session_state["history"].append({"user": user_input, "bot": response})