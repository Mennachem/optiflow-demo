import streamlit as st
import google.generativeai as genai
import os

# הגדרת תצורת העמוד
st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖", layout="wide")

st.title("🤖 צ'אט AI עם Gemini")

# 1. ניסיון שליפת המפתח מ-Secrets או מ-Environment Variables
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

# אם המפתח עדיין לא הוגדר ב-Secrets, מאפשרים הזנה בסרגל הצד (Sidebar)
if not GEMINI_API_KEY:
    with st.sidebar:
        st.header("⚙️ הגדרת מפתח API")
        GEMINI_API_KEY = st.text_input(
            "הכנס את מפתח ה-Gemini API Key שלך:",
            type="password",
            help="ניתן להוציא מפתח בחינם מ-https://aistudio.google.com/"
        )

# אם אין מפתח - עצירת האפליקציה והצגת הנחיה
if not GEMINI_API_KEY:
    st.warning("⚠️ **מפתח Gemini API אינו מוגדר.**")
    st.info("כדי להשתמש בצ'אט, הוסף את המפתח ב-Streamlit Secrets או הזן אותו בסרגל הצד (Sidebar) משמאל.")
    st.stop()

# 2. הגדרת חיבור ה-API מול גוגל
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"שגיאה בהגדרת ה-API: {e}")
    st.stop()

# 3. ניהול היסטוריית השיחה (Session State)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# הצגת כל ההודעות הקודמות בצ'אט
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. קבלת קלט מהמשתמש ושליחה ל-Gemini
user_prompt = st.chat_input("שאל את ה-AI בכל נושא...")

if user_prompt:
    # הצגת הודעת המשתמש בחלון הצ'אט
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # שליחת ההודעה ל-Gemini וקבלת תשובה בזמן אמת
    with st.chat_message("assistant"):
        with st.spinner("חורז תשובה..."):
            try:
                # המרת ההיסטוריה לפורמט הנדרש על ידי גוגל
                formatted_history = [
                    {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
                    for msg in st.session_state.chat_history[:-1]
                ]
                
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_prompt)
                
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"אירעה שגיאה בקבלת תשובה: {e}")
