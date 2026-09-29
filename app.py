import streamlit as st
import requests
import os

# הגדרת תצורת העמוד
st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖", layout="wide")

st.title("🤖 צ'אט AI עם Gemini")

# 1. שליפת המפתח מ-Secrets או מסרגל הצד
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

# 2. ניהול היסטוריית השיחה
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. קבלת קלט מהמשתמש ושליחה בבקשת HTTP ישירה ל-API של Gemini
user_prompt = st.chat_input("שאל את ה-AI בכל נושא...")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("חורז תשובה..."):
            try:
                # בניית ה-Contents עבור ה-API
                contents = []
                for msg in st.session_state.chat_history:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg["content"]}]
                    })

                # פנייה ישירה ל-REST API של גוגל
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": contents}

                response = requests.post(url, json=payload, headers=headers)
                res_data = response.json()

                if response.status_code == 200 and "candidates" in res_data:
                    ai_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(ai_text)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_text})
                else:
                    error_msg = res_data.get("error", {}).get("message", "שגיאה בלתי צפויה מ-Google API")
                    st.error(f"שגיאת API: {error_msg}")

            except Exception as e:
                st.error(f"אירעה שגיאה בתקשורת: {e}")
