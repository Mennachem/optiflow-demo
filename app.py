import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד ועיצוב
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמה חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# טעינת מפתח API מ-Secrets או מהסביבה
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ---------------------------------------------------------
# 2. אתחול Session State
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # מוגדר ל-True לטובת בדיקת הממשק
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "current_screen" not in st.session_state:
    st.session_state.current_screen = "folders" # folders / case_details / ai_analysis / summary
if "selected_folder" not in st.session_state:
    st.session_state.selected_folder = "תיקייה א'"
if "selected_case" not in st.session_state:
    st.session_state.selected_case = "תיק לקוח #101"

# הגדרות נראות ושפה (מתוך דרישות הסרגל העליון)
if "language" not in st.session_state:
    st.session_state.language = "עברית"
if "font_size" not in st.session_state:
    st.session_state.font_size = "רגיל"
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "בהיר"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# 3. סרגל עליון קבוע (Header, Breadcrumbs & Top Actions)
# ---------------------------------------------------------
top_col1, top_col2, top_col3 = st.columns([4, 3, 3])

with top_col1:
    # Breadcrumbs - נתיב ניווט
    st.markdown(f"📂 **מיקום:** ראשי ➔ `{st.session_state.selected_folder}` ➔ `{st.session_state.selected_case}`")

with top_col2:
    # כפתור שמירה קבוע בסרגל העליון
    if st.button("💾 שמור שינויים", use_container_width=True):
        st.toast("הנתונים שנשמרו בהצלחה!", icon="✅")

with top_col3:
    # הגדרות משתמש עליונות: שפה, גופן, עיצוב
    with st.popover("⚙️ הגדרות תצוגה ומשתמש"):
        st.session_state.language = st.selectbox("🌐 שפה", ["עברית", "English", "العربية"])
        st.session_state.font_size = st.selectbox("🔤 גודל גופן", ["רגיל", "גדול", "ענק"])
        st.session_state.theme_mode = st.radio("🎨 ערכת נושא", ["בהיר", "כהה"], horizontal=True)
        st.divider()
        if not GEMINI_API_KEY:
            GEMINI_API_KEY = st.text_input("הכנס Gemini API Key:", type="password")

st.divider()

# ---------------------------------------------------------
# 4. ניהול מסכים לפי הסקיצות
# ---------------------------------------------------------

# --- מסך התחברות / הרשמה (מסך 1 בסקיצה) ---
if not st.session_state.logged_in:
    st.title("🔑 התחברות למערכת OptiFlow AI")
    
    col_auth1, col_auth2 = st.columns(2)
    
    with col_auth1:
        st.subheader("התחברות")
        username = st.text_input("שם משתמש")
        password = st.text_input("סיסמה", type="password")
        if st.button("התחבר", type="primary"):
            st.session_state.logged_in = True
            st.rerun()

    with col_auth2:
        st.subheader("הרשמה למשתמש חדש")
        with st.form("register_form"):
            reg_name = st.text_input("שם מלא")
            reg_email = st.text_input("אימייל")
            reg_phone = st.text_input("נייד")
            reg_pass = st.text_input("סיסמה חדשה", type="password")
            reg_pass_confirm = st.text_input("אימות סיסמה", type="password")
            if st.form_submit_button("צור חשבון"):
                st.success("החשבון נוצר בהצלחה! כעת ניתן להתחבר.")

# --- מסכים לאחר התחברות ---
else:
    # ניווט מהיר בין שלבי העבודה
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    with nav_col1:
        if st.button("📁 1. תצוגת תיקיות", use_container_width=True):
            st.session_state.current_screen = "folders"
    with nav_col2:
        if st.button("📝 2. פרטי התיק והבעיה", use_container_width=True):
            st.session_state.current_screen = "case_details"
    with nav_col3:
        if st.button("💬 3. ניתוח AI וצ'אט", use_container_width=True):
            st.session_state.current_screen = "ai_analysis"
    with nav_col4:
        if st.button("📊 4. סיכום וחיבור לצוות", use_container_width=True):
            st.session_state.current_screen = "summary"

    st.markdown("---")

    # =========================================================
    # מסך 1: תצוגת תיקיות וצור תיקייה חדשה
    # =========================================================
    if st.session_state.current_screen == "folders":
        st.header("📂 תיקיות ותיקים פעילים")
        
        c1, c2 = st.columns([3, 1])
        with c2:
            st.subheader("צור תיקייה חדשה")
            new_folder_name = st.text_input("שם התיקייה:")
            if st.button("➕ צור תיקייה"):
                if new_folder_name:
                    st.success(f"התיקייה '{new_folder_name}' נוצרה!")

        with c1:
            st.subheader("התיקיות שלי")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                st.info("📂 **תיקייה א' - ייעוץ עסקי**")
                if st.button("פתח תיקייה א'"):
                    st.session_state.selected_folder = "תיקייה א'"
                    st.session_state.current_screen = "case_details"
                    st.rerun()

            with col_f2:
                st.info("📂 **תיקייה ב' - אופטימיזציית שיווק**")
                if st.button("פתח תיקייה ב'"):
                    st.session_state.selected_folder = "תיקייה ב'"
                    st.session_state.current_screen = "case_details"
                    st.rerun()

    # =========================================================
    # מסך 2 & 3: פרטי התיק והזנת הבעיה
    # =========================================================
    elif st.session_state.current_screen == "case_details":
        st.header(f"📝 עריכת תיק: {st.session_state.selected_case}")
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("תיאור חופשי של הבעיה / הנושא")
            problem_text = st.text_area("הכנס פירוט מלא של הנושא, האתגרים והנתונים העסקיים:", height=200, value="הלקוח מדווח על ירידה בהמרות בערוצי הפרסום וקושי במעקב אחר מלאי.")
            
            if st.button("שמור ועבור לניתוח AI ➔", type="primary"):
                st.session_state.current_screen = "ai_analysis"
                st.rerun()

        with col_side:
            st.subheader("חיווי ודגשים")
            st.warning("⚠️ יש לוודא שהוזנו כל נתוני התקציב.")
            st.success("✅ חיבור ל-CRM תקין.")

    # =========================================================
    # מסך 3: ניתוח AI וצ'אט חכם (מתוקן ללא שגיאת API)
    # =========================================================
    elif st.session_state.current_screen == "ai_analysis":
        st.header("💬 הצעות וניתוח חכם מבוסס AI")
        
        col_chat, col_insights = st.columns([2, 1])

        with col_insights:
            st.subheader("הצעות ופתרונות מהירים")
            st.write("• אופטימיזציה של תקציב הפרסום")
            st.write("• סנכרון אוטומטי של המלאי מול ה-POS")
            st.write("• שיפור תהליכי שירות לקוחות")
            
            if st.button("הצג תמונת מצב מלאה"):
                st.session_state.current_screen = "summary"
                st.rerun()

        with col_chat:
            st.subheader("צ'אט מיידי מול העוזר החכם")
            
            # הצגת היסטוריית השיחה
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_prompt = st.chat_input("שאל שאלות או הצעת פתרון...")

            if user_prompt:
                if not GEMINI_API_KEY:
                    st.error("אנא הזן מפתח Gemini API בהגדרות העליונות (⚙️).")
                else:
                    st.chat_message("user").markdown(user_prompt)
                    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

                    with st.chat_message("assistant"):
                        with st.spinner("מנתח נתונים ומכין תשובה..."):
                            try:
                                # פנייה תקינה ל-REST API של Gemini (תואם v1beta ללא שגיאות)
                                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                                headers = {"Content-Type": "application/json"}
                                
                                contents = []
                                for msg in st.session_state.chat_history:
                                    role = "user" if msg["role"] == "user" else "model"
                                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                                payload = {"contents": contents}

                                response = requests.post(url, json=payload, headers=headers)
                                res_data = response.json()

                                if response.status_code == 200 and "candidates" in res_data:
                                    ai_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                                    st.markdown(ai_text)
                                    st.session_state.chat_history.append({"role": "assistant", "content": ai_text})
                                else:
                                    error_msg = res_data.get("error", {}).get("message", "שגיאה בגישה ל-Gemini API")
                                    st.error(f"שגיאת API: {error_msg}")

                            except Exception as e:
                                st.error(f"אירעה שגיאה בחיבור: {e}")

    # =========================================================
    # מסך 4 & 5: סיכום תוצאות, חיבור לצוות ואינטגרציות
    # =========================================================
    elif st.session_state.current_screen == "summary":
        st.header("📊 סיכום פתרונות וחיבורים")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.subheader("סיכום הצעות והמלצות")
            st.info("1. עדכון קמפיינים פעילים ב-Google Ads.\n2. הגדרת התראות מלאי נמוך ב-POS.\n3. חיבור צוות המכירות למערכת.")
            
            st.subheader("סימון צוות לטיפול")
            st.multiselect("שייך אנשי צוות לתיק זה:", ["ישראל ישראלי", "משה כהן", "רחל לוי"], default=["ישראל ישראלי"])

        with col_res2:
            st.subheader("סטטוס חיבורי מערכות")
            st.success("CRM: מחובר ✅")
            st.success("POS: מחובר ✅")
            st.warning("ERP: ממתין למפתח גישה ⚠️")
            
            st.divider()
            if st.button("🔄 חזרה לתיקייה הראשית", type="secondary"):
                st.session_state.current_screen = "folders"
                st.rerun()
