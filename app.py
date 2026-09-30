import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד ועיצוב בסיסי
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמה חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# שליפת מפתח API של Gemini
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ---------------------------------------------------------
# 2. ניהול Session State (מצבי מסכים, משתמשים והגדרות)
# ---------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "screen_1"  # screen_1, screen_2, screen_3, screen_4, screen_5, main_screen, profile_screen

if "show_password" not in st.session_state:
    st.session_state.show_password = False

# הגדרות עיצוב ומשתמש (סרגל כלים)
if "theme_color" not in st.session_state:
    st.session_state.theme_color = "כחול"
if "font_family" not in st.session_state:
    st.session_state.font_family = "Rubik"
if "language" not in st.session_state:
    st.session_state.language = "עברית"

# נתוני עסק וסביבת עבודה
if "business_name" not in st.session_state:
    st.session_state.business_name = "חד וחלק"
if "business_nature" not in st.session_state:
    st.session_state.business_nature = "חיתוך פלסטיק בלייזר"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# פונקציות עזר וסרגל כלים עליון (כפתור 35 + 42-46)
# ---------------------------------------------------------
def render_toolbar():
    """רכיב סרגל הכלים (35) המופיע במסך הראשי ובמסכים הפעילים"""
    st.markdown("---")
    tb_col1, tb_col2, tb_col3, tb_col4, tb_col5, tb_space, tb_biz, tb_logo = st.columns([1.5, 2, 2, 2, 1.5, 2, 2, 1])
    
    with tb_logo:
        # כפתור 26: לוגו התוכנה -> מחזיר למסך הראשי
        if st.button("🚀 OptiFlow", key="tb_logo_btn", use_container_width=True):
            st.session_state.screen = "main_screen"
            st.rerun()

    with tb_biz:
        # כפתור 27: דפדף בין עסקים
        st.selectbox("עסק פעיל (27):", [st.session_state.business_name, "עסק משני בע''מ"], label_visibility="collapsed")

    with tb_col1:
        # כפתור 42: הגדרות הלקוח (שפה, גופן, צבע)
        with st.popover("⚙️ הגדרות (42)"):
            st.session_state.language = st.selectbox("שפה:", ["עברית", "English", "العربية"])
            st.session_state.font_family = st.selectbox("גופן:", ["Rubik", "Segoe UI", "Arial"])
            st.session_state.theme_color = st.selectbox("צבע נושא:", ["כחול", "כהה", "ירוק"])

    with tb_col2:
        # כפתור 43: מעבר למסך פרטי הלקוח
        if st.button("👤 פרטי עסק (43)", use_container_width=True):
            st.session_state.screen = "profile_screen"
            st.rerun()

    with tb_col3:
        # כפתור 45: פתיחת עסק / תיקייה נוספת
        if st.button("➕ עסק נוסף (45)", use_container_width=True):
            st.toast("פתיחת עסק נוסף מותנית בהרחבת התוכנית העסקית.", icon="ℹ️")

    with tb_col4:
        # כפתור 46: צור קשר
        with st.popover("📞 צור קשר (46)"):
            st.write("**תמיכה טכנית ושירות לקוחות**")
            st.write("מייל: support@optiflow.ai")
            st.write("טלפון: 077-0000000")

    st.markdown("---")

# =========================================================
# מסך 1: התחברות ראשונית
# =========================================================
if st.session_state.screen == "screen_1":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        # 1. לוגו התוכנה (לחיצה מחזירה למסך ראשי אם מחובר)
        st.title("🚀 OptiFlow AI (1)")
        st.subheader("התחברות למערכת")

        # 2. שם משתמש
        username = st.text_input("שם משתמש (2):")

        # 3. סיסמה + לחצן עין לצפייה
        col_pass, col_eye = st.columns([5, 1])
        with col_pass:
            pwd_type = "text" if st.session_state.show_password else "password"
            password = st.text_input("סיסמה (3):", type=pwd_type)
        with col_eye:
            st.write("") # מרווח
            st.write("")
            if st.button("👁️", help="הצג/הסתר סיסמה"):
                st.session_state.show_password = not st.session_state.show_password
                st.rerun()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            # 5. התחברות
            if st.button("התחברות (5)", type="primary", use_container_width=True):
                if username and password:
                    st.session_state.screen = "main_screen"
                    st.rerun()
                else:
                    st.error("אנא הכנס שם משתמש וסיסמה תקינים.")

        with col_btn2:
            # 4. שכחתי שם משתמש או סיסמה -> מעביר למסך 2
            if st.button("שכחתי פרטים (4)", use_container_width=True):
                st.session_state.screen = "screen_2"
                st.rerun()

        st.markdown("---")
        # 6. הירשם -> מעביר למסך 3
        if st.button("לקוח חדש? הירשם כאן (6)", use_container_width=True):
            st.session_state.screen = "screen_3"
            st.rerun()

# =========================================================
# מסך 2: שחזור סיסמה ושליחת קוד
# =========================================================
elif st.session_state.screen == "screen_2":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🔑 שחזור סיסמה (מסך 2)")
        
        # 7. דוא"ל | 8. נייד
        email = st.text_input("דוא''ל (7):")
        mobile = st.text_input("נייד (8):")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            # 9. שליחת קוד במייל
            if st.button("שליחת קוד במייל (9)", use_container_width=True):
                st.info(f"קוד אימות נשלח לכתובת {email}")

        with col_s2:
            # 10. שליחת סיסמה בנייד (פותח שאילתא לבחירה)
            with st.popover("שליחת סיסמה בנייד (10)"):
                st.write("בחר אמצעי לקבלת הקוד:")
                if st.button("📱 SMS"):
                    st.success("קוד נשלח ב-SMS")
                if st.button("💬 WhatsApp"):
                    st.success("קוד נשלח ב-WhatsApp")
                if st.button("📞 שיחה טלפונית"):
                    st.success("שיחה קולית בדרך אליך")

        st.markdown("---")
        # 11. אימות סיסמה שנשלחה
        auth_code = st.text_input("הכנס קוד אימות שקיבלת (11):")
        if st.button("אמת קוד והמשך", type="primary", use_container_width=True):
            if auth_code == "1234" or len(auth_code) > 2:
                st.session_state.screen = "screen_5"
                st.rerun()
            else:
                st.error("סיסמה שגויה. נסה שנית או לחץ על שליחה מחדש.")

# =========================================================
# מסך 3: הרשמת לקוח חדש
# =========================================================
elif st.session_state.screen == "screen_3":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("📝 הרשמת לקוח חדש (מסך 3)")
        
        c1, c2 = st.columns(2)
        with c1:
            # 12. שם ושם משפחה | 13. נייד | 14. דוא"ל
            full_name = st.text_input("שם ושם משפחה (12):")
            mobile = st.text_input("נייד (13):")
            email = st.text_input("דוא''ל (14):")
        with c2:
            # 15. שם העסק | 16. מהות העסק | 17. כתובת
            biz_name = st.text_input("שם העסק (15):", value=st.session_state.business_name)
            biz_nature = st.text_input("מהות העסק (16):", value=st.session_state.business_nature)
            biz_address = st.text_input("כתובת העסק (17):")

        # 18. אישור והמשך -> מוביל למסך 4
        if st.button("אישור והמשך לבחירת תוכנית (18) ➔", type="primary", use_container_width=True):
            st.session_state.business_name = biz_name
            st.session_state.business_nature = biz_nature
            st.session_state.screen = "screen_4"
            st.rerun()

# =========================================================
# מסך 4: בחירת תוכנית וסליקה
# =========================================================
elif st.session_state.screen == "screen_4":
    st.title("💳 בחירת תוכנית שירות (מסך 4)")
    st.caption("סקיצה לבחירת מנוי ומעבר למערכת סליקה")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.subheader("תוכנית חודשית (19)")
        st.write("₪199 / חודש")
        if st.button("בחר חודשי מעבר לסליקה", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

    with p2:
        st.subheader("תוכנית שנתית (20)")
        st.write("₪1,990 / שנה")
        if st.button("בחר שנתי מעבר לסליקה", type="primary", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

    with p3:
        st.subheader("תוכנית פרימיום (21)")
        st.write("₪3,490 / שנה")
        if st.button("בחר פרימיום מעבר לסליקה", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

# =========================================================
# מסך 5: יצירת שם משתמש וסיסמה חדשים
# =========================================================
elif st.session_state.screen == "screen_5":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🔐 הגדרת פרטי התחברות חדשים (מסך 5)")
        
        # 22. שם משתמש חדש
        new_user = st.text_input("שם משתמש חדש (22):")

        # 23. סיסמה חדשה עם עין
        c_pass, c_eye = st.columns([5, 1])
        with c_pass:
            p_type = "text" if st.session_state.show_password else "password"
            new_pass = st.text_input("סיסמה חדשה (23):", type=p_type)
        with c_eye:
            st.write("")
            st.write("")
            if st.button("👁️", key="eye_5"):
                st.session_state.show_password = not st.session_state.show_password
                st.rerun()

        # 24. אימות סיסמה
        confirm_pass = st.text_input("אימות סיסמה חדשה (24):", type="password")

        # 25. אישור והמשך -> מחזיר למסך 1 להתחברות
        if st.button("אישור והמשך להתחברות (25)", type="primary", use_container_width=True):
            if new_pass == confirm_pass:
                st.success("הפרטים עודכנו בהצלחה! כעת ניתן להתחבר.")
                st.session_state.screen = "screen_1"
                st.rerun()
            else:
                st.error("הסיסמאות אינן תואמות.")

# =========================================================
# מסך ראשי: פאנל העבודה המרכזי (26-41)
# =========================================================
elif st.session_state.screen == "main_screen":
    render_toolbar() # 35: סרגל כלים עליון קבוע

    # גריד ראשי לפי התרשים של מסך ראשי
    row1_left, row1_mid, row1_right = st.columns([2, 1.5, 1.5])

    # 36. פתרונות + 37 + 38
    with row1_left:
        st.subheader("💡 פתרונות והמלצות (36)")
        st.info("כאן יוצגו הפתרונות המנותחים על ידי המערכת בהתאם לנתוני העסק.")
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            # 37. הצעת פתרונות נוספים (אותם פרמטרים)
            if st.button("הצעת פתרונות נוספים (37)", use_container_width=True):
                st.toast("מחשב פתרונות חלופיים באותם פרמטרים...")
        with btn_c2:
            # 38. חישוב מחדש (שינוי פרמטרים/תמונות)
            if st.button("חישוב מחדש (38)", type="primary", use_container_width=True):
                st.toast("מבצע חישוב מחדש לפי הנתונים המעודכנים!")

    # 32. כפתור / רכיב מבוסס AI להכוונה ושאלות
    with row1_mid:
        st.subheader("🤖 מנוע הכוונה AI (32)")
        st.write("מערכת השאלות החכמה לדיוק הנתונים:")
        st.text_area("שאלת הכוונה מה-AI:", value="מהו סוג החומר העיקרי שאתה חותך בלייזר, ומאיזה עובי מתחיל הליקוי?", height=120)
        st.button("שלח תשובה להכוונה", use_container_width=True)

    # 28, 29, 30, 31 - צד ימין
    with row1_right:
        # 28. תיקיות
        st.selectbox("בחירת תיקייה (28):", ["תיקייה ראשית", "פרויקט לייזר X", "תקלת מכונה B"])
        
        # 29. פרט את מהות הבעיה
        st.text_area("מהות הבעיה (29):", value="סדקים בשולי הפלסטיק בעת חיתוך בלייזר עוצמתי.", height=90)
        
        # 30. פרמטרים ונתונים
        st.text_input("פרמטרים ונתונים (30):", value="מהירות: 150mm/s, עוצמה: 80W")
        
        # 31. העלאת תמונות וקבצים
        st.file_uploader("העלאת תמונות וקבצים (31):", accept_multiple_files=True)

    st.markdown("---")

    # חלק תחתון: 39. חלון הצ'אט, 40. מעבר בין שיחות, 41. הגדלה
    c_chat, c_info = st.columns([2, 1])
    with c_chat:
        st.subheader("💬 חלון צ'אט AI (39)")
        
        col_ch1, col_ch2 = st.columns([3, 1])
        with col_ch1:
            # 40. אפשרות לעבור בין שיחות צ'אט שמורות
            st.selectbox("שיחות שמורות בתיקייה זו (40):", ["שיחה 1 - ניתוח חיתוך", "שיחה 2 - בדיקת פרמטרים"], label_visibility="collapsed")
        with col_ch2:
            # 41. הגדלת חלונית הצ'אט
            if st.button("🔍 הגדל צ'אט (41)", use_container_width=True):
                st.toast("תצוגת צ'אט מורחבת פעילה")

        # רכיב הצ'אט מול Gemini API
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("שאל את העוזר החכם בנוגע לבעיה...")
        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            if GEMINI_API_KEY:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"role": "user", "parts": [{"text": f"אתה יועץ עבור עסק {st.session_state.business_name} ({st.session_state.business_nature}). ענה בקצרה ומקצועיות: {user_input}"}]}]}
                    
                    res = requests.post(url, json=payload, headers=headers).json()
                    if "candidates" in res:
                        reply = res["candidates"][0]["content"]["parts"][0]["text"]
                        st.chat_message("assistant").markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"שגיאה בתקשורת: {e}")

# =========================================================
# מסך 43: מסך פרטי הלקוח והעסק (מתוך סרגל הכלים)
# =========================================================
elif st.session_state.screen == "profile_screen":
    render_toolbar()
    st.title("👤 מסך פרטי הלקוח והעסק (43)")
    st.caption("נתונים אלו משמשים את ה-AI לשליפה אוטומטית בכל פתיחת נושא חדש")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.session_state.business_name = st.text_input("שם העסק:", value=st.session_state.business_name)
        st.session_state.business_nature = st.text_input("מהות העסק:", value=st.session_state.business_nature)
        st.text_area("נתונים טכניים ומכשור:", value="מכונת חיתוך לייזר CO2 100W, תוכנת AutoCAD, תוכנת LightBurn")

    with col_p2:
        st.text_area("תוכנות וחיבורים היקפיים:", value="חיבור ל-CRM, מערכת ניהול מלאי מדף")
        st.checkbox("חיבור אוטומטי של פרטי העסק לכל נושא חדש", value=True)

    if st.button("💾 שמור נתונים וחזור למסך ראשי", type="primary"):
        st.success("הנתונים עודכנו בהצלחה!")
        st.session_state.screen = "main_screen"
        st.rerun()
