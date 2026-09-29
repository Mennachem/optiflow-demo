import streamlit as st
from google import genai
import os

# הגדרת תצורת העמוד
st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖", layout="wide")

st.title("🤖 צ'אט AI עם Gemini")

# שליפת המפתח מ-Secrets או מהמשתמש
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

if not GEMINI_API_KEY:
    with st.sidebar:
        st.header("⚙️ הגדרת מפתח API")
        GEMINI_API_KEY = st.text_input(
            "הכנס את מפתח ה-Gemini API Key שלך:",
            type="password",
            help="ניתן להוציא מפתח בחינם מ-https://aistudio.google.com/"
        )

if not GEMINI_API_KEY:
    st.warning("⚠️ **מפתח Gemini API אינו מוגדר.**")
    st.info("כדי להשתמש בצ'אט, הוסף את המפתח ב-Streamlit Secrets או הזן אותו בסרגל הצד (Sidebar) משמאל.")
    st.stop()

# יצירת הלקוח של גוגל
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"שגיאה בהתחברות ל-API: {e}")
    st.stop()

# ניהול היסטוריית השיחה
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# קבלת קלט ושליחה
user_prompt = st.chat_input("שאל את ה-AI בכל נושא...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("חורז תשובה..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt
                )
                
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"אירעה שגיאה בקבלת תשובה: {e}")
