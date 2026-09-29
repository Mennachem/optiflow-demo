import streamlit as st
import requests
import json
import os

# הגדרת תצורת העמוד והעיצוב
st.set_page_config(page_title="OptiFlow AI - Multi-Tenant SaaS", page_icon="🚀", layout="wide")

# טעינת מפתח ה-API מ-Secrets או מסרגל הצד
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

# ניהול בסיס נתונים מקומי לבידוד סביבות עבודה (Multi-Tenancy)
DATA_FILE = "data_store.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"workspaces": {}, "users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# ניהול משתמשים וסביבת עבודה ב-Session
if "user" not in st.session_state:
    st.session_state.user = "DemoUser"
if "workspace" not in st.session_state:
    st.session_state.workspace = "Default_Workspace"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- סרגל צד: ניהול הגדרות, מפתח API וסביבות עבודה ---
with st.sidebar:
    st.title("⚙️ ניהול סביבה וחיבורים")
    
    # 1. הזנת API Key במידה ולא הוגדר ב-Secrets
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = st.text_input(
            "הכנס Gemini API Key:",
            type="password",
            help="ניתן להוציא מפתח בחינם מ-https://aistudio.google.com/"
        )
    else:
        st.success("מפתח API מחובר ✅")

    st.divider()

    # 2. הפרדת workspaces
    st.subheader("🏢 סביבת עבודה (Workspace)")
    current_workspace = st.text_input("שם סביבת עבודה נוכחית:", value=st.session_state.workspace)
    if current_workspace != st.session_state.workspace:
        st.session_state.workspace = current_workspace
        st.session_state.chat_history = [] # איפוס צ'אט במעבר סביבה
        st.rerun()

    st.divider()

    # 3. אינטגרציות מערכות חיצוניות (CRM / POS / Inventory)
    st.subheader("🔗 חיבורי מערכות")
    enable_crm = st.checkbox("חיבור CRM", value=True)
    enable_pos = st.checkbox("חיבור POS", value=True)
    enable_inventory = st.checkbox("חיבור מלאי", value=True)

# --- גוף האתר המרכזי ---
st.title(f"🚀 OptiFlow AI - סביבת עבודה: {st.session_state.workspace}")
st.caption("פלטפורמת B2B לייעוץ עסקי חכם ואוטומציה")

# בדיקה אם קיים מפתח API
if not GEMINI_API_KEY:
    st.warning("⚠️ **מפתח Gemini API אינו מוגדר.**")
    st.info("אנא הזן את מפתח ה-API בסרגל הצד משמאל כדי להפעיל את העוזר החכם.")
    st.stop()

# טאבים לניווט בין חלקי המערכת
tab_dashboard, tab_integrations, tab_chat = st.tabs(["📊 דאשבורד ופרמטרים", "🔌 מודולי אינטגרציה", "💬 עוזר AI דינמי"])

# --- טאב 1: דאשבורד וניהול פרמטרים ---
with tab_dashboard:
    st.header("הגדרות וסגמנטים עסקיים")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("שם החברה / לקוח:", value="חברה אליפות בע''מ")
        st.number_input("תקציב חודשי משוער (₪):", value=50000, step=1000)
    with col2:
        st.selectbox("תחום פעילות:", ["קמעונאות", "שירותים", "הייטק", "ייצור"])
        st.multiselect("ערוצי שיווק פעילים:", ["Google Ads", "Facebook", "Instagram", "SEO"], default=["Google Ads"])

# --- טאב 2: אינטגרציות ומודולים ---
with tab_integrations:
    st.header("סטטוס מודולים מחוברים")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("CRM Status", "מחובר" if enable_crm else "מנותק", delta="Active" if enable_crm else "Disabled")
    with col_b:
        st.metric("POS Status", "מחובר" if enable_pos else "מנותק", delta="Active" if enable_pos else "Disabled")
    with col_c:
        st.metric("Inventory Status", "מחובר" if enable_inventory else "מנותק", delta="Active" if enable_inventory else "Disabled")

# --- טאב 3: הצ'אט החכם מבוסס Gemini ---
with tab_chat:
    st.header("צ'אט ייעוץ עסקי בזמן אמת")

    # הצגת היסטוריית השיחה
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # קלט משתמש
    user_prompt = st.chat_input("שאל את OptiFlow AI לגבי אופטימיזציה של העסק...")

    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("מנתח נתונים ומכין תשובה..."):
                try:
                    # הנחיית מערכת (System Prompt) להקשר העסקי
                    system_context = f"אתה יועץ עסקי חכם של פלטפורמת OptiFlow AI. אתה עונה עבור סביבת העבודה {st.session_state.workspace}. תן תשובות ממוקדות, מקצועיות ועסקיות."
                    
                    contents = [{"role": "user", "parts": [{"text": system_context}]}]
                    for msg in st.session_state.chat_history:
                        role = "user" if msg["role"] == "user" else "model"
                        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                    # פנייה ל-API
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
                        error_msg = res_data.get("error", {}).get("message", "שגיאה בתקשורת עם Gemini")
                        st.error(f"שגיאת API: {error_msg}")

                except Exception as e:
                    st.error(f"אירעה שגיאה: {e}")
