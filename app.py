import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד ועיצוב מקורי
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמת ייעוץ עסקי חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שליפת מפתח API מה-Secrets או מהסביבה
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))

# ---------------------------------------------------------
# 2. ניהול Session State (שפות, אזור אישי, ערכת נושא)
# ---------------------------------------------------------
if "language" not in st.session_state:
    st.session_state.language = "עברית"
if "user_role" not in st.session_state:
    st.session_state.user_role = "מנהל מערכת (Admin)"
if "workspace" not in st.session_state:
    st.session_state.workspace = "סביבת עבודה ראשית"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# 3. סרגל צד (Sidebar) המקורי: אזור אישי, שפות, פרמטרים
# ---------------------------------------------------------
with st.sidebar:
    st.title("👤 אזור אישי וסביבה")
    
    # הגדרות משתמש ושפה
    col_lang, col_role = st.columns(2)
    with col_lang:
        st.session_state.language = st.selectbox("🌐 שפה", ["עברית", "English", "العربية"])
    with col_role:
        st.session_state.user_role = st.selectbox("🔑 תפקיד", ["Admin", "Analyst", "Manager"])
    
    st.caption(f"מחובר כ: **ישראל ישראלי** ({st.session_state.user_role})")
    st.divider()

    # ניהול API Key
    st.subheader("⚙️ הגדרת חיבור API")
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = st.text_input(
            "הכנס Gemini API Key:",
            type="password",
            help="ניתן להוציא מפתח מ-https://aistudio.google.com/"
        )
    else:
        st.success("מפתח Gemini API מחובר ✅")

    st.divider()

    # הגדרות סביבת עבודה וסגמנטים
    st.subheader("🏢 ניהול סביבת עבודה")
    st.session_state.workspace = st.text_input("שם הסביבה:", value=st.session_state.workspace)
    
    st.subheader("🔗 חיבורי מערכות (Integrations)")
    crm_active = st.toggle("חיבור CRM", value=True)
    pos_active = st.toggle("חיבור קופות POS", value=True)
    erp_active = st.toggle("חיבור ERP / מלאי", value=True)

# ---------------------------------------------------------
# 4. כותרת מרכזית ודאשבורד
# ---------------------------------------------------------
st.title(f"🚀 OptiFlow AI - {st.session_state.workspace}")
st.caption("מערכת אופטימיזציה, ניתוח נתונים וייעוץ עסקי מבוססת AI")

# בדיקת מפתח API
if not GEMINI_API_KEY:
    st.warning("⚠️ **מפתח Gemini API אינו מוגדר.**")
    st.info("אנא הזן את המפתח בסרגל הצד (משמאל) כדי להפעיל את העוזר החכם.")

# ---------------------------------------------------------
# 5. טאבים ראשיים של המערכת
# ---------------------------------------------------------
tab_dash, tab_params, tab_chat, tab_settings = st.tabs([
    "📊 דאשבורד וניתוח", 
    "⚙️ ניהול פרמטרים וסגמנטים", 
    "💬 עוזר AI חכם (צ'אט)", 
    "🔌 אינטגרציות ואזור אישי"
])

# --- טאב 1: דאשבורד ---
with tab_dash:
    st.header("מבט על - ביצועים וערוצים")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("הכנסות חודשיות", "₪125,000", "+12%")
    m2.metric("יחס המרה", "3.4%", "+0.5%")
    m3.metric("סטטוס CRM", "פעיל" if crm_active else "מנותק")
    m4.metric("סטטוס POS", "פעיל" if pos_active else "מנותק")

# --- טאב 2: ניהול פרמטרים ---
with tab_params:
    st.header("הגדרת סגמנטים ויעדים עסקיים")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("שם העסק / החברה:", value="חברה אליפות בע''מ")
        st.number_input("תקציב שיווק חודשי (₪):", value=35000, step=1000)
    with col2:
        st.selectbox("תחום פעילות מרכזי:", ["קמעונאות וסחר", "שירותים מקצועיים", "הייטק ו-SaaS", "תעשייה וייצור"])
        st.multiselect("ערוצי פרסום פעילים:", ["Google Ads", "Facebook", "Instagram", "TikTok", "SEO"], default=["Google Ads", "Facebook"])

# --- טאב 3: הצ'אט החדש והחכם ---
with tab_chat:
    st.header("💬 עוזר AI חכם לייעוץ עסקי")
    st.caption("שאל שאלות, בקש ניתוחים או המלצות אופטימיזציה בזמן אמת")

    # הצגת היסטוריית הצ'אט
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # קלט משתמש
    user_prompt = st.chat_input("שאל את OptiFlow AI לגבי העסק...")

    if user_prompt:
        if not GEMINI_API_KEY:
            st.error("אנא הזן מפתח API בסרגל הצד כדי להתחיל בצ'אט.")
        else:
            st.chat_message("user").markdown(user_prompt)
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})

            with st.chat_message("assistant"):
                with st.spinner("מנתח נתונים ומנסח תשובה..."):
                    try:
                        system_context = f"אתה יועץ עסקי של מערכת OptiFlow AI. ענה בשפה {st.session_state.language}. הסביבה הנוכחית היא {st.session_state.workspace}."
                        
                        contents = [{"role": "user", "parts": [{"text": system_context}]}]
                        for msg in st.session_state.chat_history:
                            role = "user" if msg["role"] == "user" else "model"
                            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

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
                            error_msg = res_data.get("error", {}).get("message", "שגיאה בחיבור ל-Gemini")
                            st.error(f"שגיאה: {error_msg}")

                    except Exception as e:
                        st.error(f"אירעה שגיאה: {e}")

# --- טאב 4: אינטגרציות ואזור אישי ---
with tab_settings:
    st.header("הגדרות פרופיל ואינטגרציות")
    st.json({
        "User": "ישראל ישראלי",
        "Role": st.session_state.user_role,
        "Language": st.session_state.language,
        "Workspace": st.session_state.workspace,
        "Active Modules": {
            "CRM": crm_active,
            "POS": pos_active,
            "ERP": erp_active
        }
    })
