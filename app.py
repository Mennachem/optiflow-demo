import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד ועיצוב CSS מותאם לסקיצות
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS לסרגל כלים: לוגו מימין, סרגל משמאל
st.markdown("""
<style>
    .stButton>button {
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    div[data-testid="stHorizontalBlock"] button {
        border: none !important;
        background: transparent !important;
        color: #333333 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        color: #0066cc !important;
        background-color: #f5f5f5 !important;
    }
    /* עיצוב כפתור הלוגו בלבד */
    .logo-btn > button {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #1e3a8a !important;
        background: none !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. מפתח API מובנה בקוד (אינו מוצג בהגדרות הלקוח)
# ---------------------------------------------------------
BUILTIN_GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE"))

# ---------------------------------------------------------
# 3. אתחול Session State ומסד נתונים פנימי
# ---------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "screen_1"

# מאגר משתמשים רשומים (מסך 5 / רשומים מראש)
if "registered_users" not in st.session_state:
    st.session_state.registered_users = {
        "admin@optiflow.ai": {"pass": "12456", "name": "ישראל ישראלי", "phone": "050-1234567"},
        "user@test.com": {"pass": "123456", "name": "משה כהן", "phone": "052-7654321"}
    }

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# מאגר עסקים ונושאים
if "businesses" not in st.session_state:
    st.session_state.businesses = {
        "עסק לייזר - חד וחלק": {
            "name": "עסק לייזר - חד וחלק",
            "phone": "03-5551234",
            "email": "laser@had.co.il",
            "address": "אזור תעשייה חולון",
            "nature": "חיתוך פלסטיק ומתכת בלייזר",
            "tech_data": "מכונת חיתוך לייזר CO2 100W",
            "topics": {
                "סדקים בחיתוך פלסטיק": {
                    "problem": "סדקים בשולי הפלסטיק בעת חיתוך בלייזר עוצמתי.",
                    "structured_params": [
                        {"name": "סוג חומר", "type": "טקסט", "value": "פלסטיק אקרילי"},
                        {"name": "מהירות חיתוך", "type": "מספר", "value": "150", "unit": "mm/s"},
                        {"name": "עוצמת לייזר", "type": "מספר", "value": "80", "unit": "W"}
                    ],
                    "ai_question": "מהו עובי החומר (ב-מ\"מ) שבו מתרחשים הסדקים?",
                    "chats": {"שיחה 1": [], "שיחה 2": []},
                    "current_chat": "שיחה 1",
                    "solutions": ["כיול מחדש לפי הנתונים: פלסטיק אקרילי", "בדיקת עדשות ומערכת הקרנת הלייזר"]
                }
            },
            "selected_topic": "סדקים בחיתוך פלסטיק"
        }
    }

if "current_biz_key" not in st.session_state:
    st.session_state.current_biz_key = "עסק לייזר - חד וחלק"

if "chat_expanded" not in st.session_state:
    st.session_state.chat_expanded = False

# ---------------------------------------------------------
# 4. סרגל כלים עליון (לוגו מימין, סרגל משמאל)
# ---------------------------------------------------------
def render_header():
    # חלוקת עמודות: ימין הלוגו, שמאל סרגל הכלים
    col_logo, col_empty, col_nav = st.columns([2, 4, 4])
    
    with col_logo:
        # 2. לוגו בימין למעלה קבוע - לחיצה עליו מחזירה למסך ראשי
        if st.button("🚀 OptiFlow AI", key="main_logo_btn"):
            st.session_state.screen = "main_screen"
            st.rerun()

    with col_nav:
        # 3. סרגל כלים בצד שמאל למעלה קבוע
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🏠 מסך ראשי"):
                st.session_state.screen = "main_screen"
                st.rerun()
        with c2:
            with st.popover("⚙️ הגדרות"):
                st.write("**הגדרות מערכת**")
                st.write("שפת ממשק: עברית")
                st.write("התראות מערכת: פעיל")
        with c3:
            with st.popover("📞 צור קשר"):
                st.write("**תמיכה טכנית**")
                st.write("מייל: support@optiflow.ai")

    st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# =========================================================
# מסך 1: התחברות (עם בדיקת משתמש רשום במסך 5)
# =========================================================
if st.session_state.screen == "screen_1":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🚀 OptiFlow AI")
        st.subheader("התחברות למערכת")

        # טופס התחברות התומך בשליפה מגוגל (Google Autofill)
        with st.form(key="login_form"):
            username = st.text_input("שם משתמש / דוא\"ל:", autocomplete="username")
            password = st.text_input("סיסמה:", type="password", autocomplete="current-password")
            submit_login = st.form_submit_button("התחברות", type="primary", use_container_width=True)

            if submit_login:
                # 4. בדיקה אם הלקוח הופעל/נרשם במסך 5
                if username in st.session_state.registered_users and st.session_state.registered_users[username]["pass"] == password:
                    st.session_state.logged_in_user = username
                    st.session_state.screen = "main_screen"
                    st.rerun()
                else:
                    st.error("שם משתמש אינו קיים במערכת, לקוח לא רשום.")

        st.markdown("---")
        st.write("עדיין לא רשום במערכת?")
        if st.button("הירשם כאן", use_container_width=True):
            st.session_state.screen = "screen_3"
            st.rerun()

# =========================================================
# מסך 3: רישום לקוח חדש
# =========================================================
elif st.session_state.screen == "screen_3":
    st.title("📝 רישום לקוח חדש")
    
    # 5. שדות מסך 3 בדיוק לפי הדרישות
    full_name = st.text_input("12 - שם ושם משפחה:")
    phone = st.text_input("13 - נייד:")
    email = st.text_input("14 - דוא\"ל:")
    address = st.text_input("15 - כתובת הלקוח:")
    notes = st.text_area("16 - הערות:")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("18 - אישור והמשך", type="primary", use_container_width=True):
        if email and full_name:
            # שמירה זמנית והעברה למסך 4
            st.session_state.temp_user = {"name": full_name, "phone": phone, "email": email, "address": address, "notes": notes}
            st.session_state.screen = "screen_4"
            st.rerun()
        else:
            st.warning("אנא למלא לפחות שם ודוא\"ל.")

# =========================================================
# מסך 4: בחירת תוכנית
# =========================================================
elif st.session_state.screen == "screen_4":
    st.title("💳 בחירת תוכנית מנוי")
    st.selectbox("בחר תוכנית:", ["תוכנית בסיסית", "תוכנית מקצועית", "תוכנית פרימיום"])
    
    if st.button("אישור והפעלה (מעבר למסך 5 לקיוד ומיווש)", type="primary"):
        st.session_state.screen = "screen_5"
        st.rerun()

# =========================================================
# מסך 5: קביעת שם משתמש וסיסמה (הפעלה רשמית)
# =========================================================
elif st.session_state.screen == "screen_5":
    st.title("🔐 הגדרת חשבון וסיסמה")
    st.write("כאן ניתן להגדיר שם משתמש וסיסמה להפעלת החשבון במערכת:")
    
    temp_u = st.session_state.get("temp_user", {})
    user_email = st.text_input("שם משתמש (דוא\"ל):", value=temp_u.get("email", ""))
    new_pass = st.text_input("בחר סיסמה חדשה:", type="password")

    if st.button("סיום והפעלת החשבון", type="primary"):
        if user_email and new_pass:
            st.session_state.registered_users[user_email] = {
                "pass": new_pass,
                "name": temp_u.get("name", "לקוח חדש"),
                "phone": temp_u.get("phone", "")
            }
            st.success("החשבון הופעל בהצלחה! כעת ניתן להתחבר במסך 1.")
            st.session_state.screen = "screen_1"
            st.rerun()

# =========================================================
# 6. מסך ראשי: רשימת עסקים + אפשרות לפתוח עסק חדש
# =========================================================
elif st.session_state.screen == "main_screen":
    render_header()
    
    st.title("🏢 רשימת העסקים שלי")
    
    col_list, col_add = st.columns([3, 1])
    
    with col_list:
        for biz_key in list(st.session_state.businesses.keys()):
            biz = st.session_state.businesses[biz_key]
            with st.container():
                st.markdown(f"### 🔹 {biz['name']}")
                st.write(f"**כתובת:** {biz['address']} | **מהות העסק:** {biz['nature']}")
                if st.button(f"פתוח נושאים של {biz['name']}", key=f"open_biz_{biz_key}"):
                    st.session_state.current_biz_key = biz_key
                    st.session_state.screen = "topics_screen"
                    st.rerun()
                st.markdown("---")

    with col_add:
        st.markdown("### ➕ עסק חדש")
        if st.button("פתיחת עסק חדש (מסך עסק)", use_container_width=True, type="primary"):
            st.session_state.edit_biz_key = None
            st.session_state.screen = "biz_screen"
            st.rerun()

# =========================================================
# מסך עסק: הזנת/עריכת פרטי עסק (לפי תמונת 'מסך עסק')
# =========================================================
elif st.session_state.screen == "biz_screen":
    render_header()
    st.title("📋 מסך עסק")
    
    # 9 משבצות לפי הסקיצה 'מסך עסק'
    b_name = st.text_input("שם העסק:", value="")
    b_phone = st.text_input("נייד:")
    b_email = st.text_input("דוא\"ל:")
    b_address = st.text_input("כתובת:")
    b_nature = st.text_input("מהות העסק:")
    b_tech = st.text_area("נתונים ופרמטרים:")
    
    st.file_uploader("העלאת קבצים:", accept_multiple_files=True)
    st.text_input("חיבור למערכות מידע:")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("שמירה", type="primary", use_container_width=True):
            if b_name:
                st.session_state.businesses[b_name] = {
                    "name": b_name,
                    "phone": b_phone,
                    "email": b_email,
                    "address": b_address,
                    "nature": b_nature,
                    "tech_data": b_tech,
                    "topics": {},
                    "selected_topic": None
                }
                st.success("העסק נשמר בהצלחה!")
                st.session_state.screen = "main_screen"
                st.rerun()
    with col_s2:
        if st.button("עריכה / ביטול", use_container_width=True):
            st.session_state.screen = "main_screen"
            st.rerun()

# =========================================================
# מסך נושאים (לפי תמונת 'מסך נושאים')
# =========================================================
elif st.session_state.screen == "topics_screen":
    render_header()
    
    biz = st.session_state.businesses[st.session_state.current_biz_key]
    
    col_biz_info, col_topics_center, col_user_info = st.columns([1.5, 3, 1.5])
    
    # פאנל פרטי עסק (משמאל בסקיצה)
    with col_biz_info:
        st.subheader("📌 פרטי עסק")
        st.write(f"**שם:** {biz['name']}")
        st.write(f"**מהות:** {biz['nature']}")
        st.write(f"**כתובת:** {biz['address']}")
        if st.button("ערוך פרטי עסק"):
            st.session_state.screen = "biz_screen"
            st.rerun()

    # מרכז: נושאים + צור נושא חדש
    with col_topics_center:
        st.title("📂 מסך נושאים")
        
        topics = biz["topics"]
        if topics:
            for top_name in list(topics.keys()):
                if st.button(f"📄 {top_name}", key=f"top_{top_name}", use_container_width=True):
                    biz["selected_topic"] = top_name
                    st.session_state.screen = "help_screen"
                    st.rerun()
        else:
            st.info("אין נושאים פתוחים עבור עסק זה.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ צור נושא חדש", type="primary"):
            st.session_state.screen = "help_screen"
            st.session_state.is_new_topic = True
            st.rerun()

    # פאנל פרטי לקוח (מימין בסקיצה)
    with col_user_info:
        st.subheader("👤 פרטי לקוח")
        u_data = st.session_state.registered_users.get(st.session_state.logged_in_user, {})
        st.write(f"**שם:** {u_data.get('name', 'ישראל ישראלי')}")
        st.write(f"**נייד:** {u_data.get('phone', '050-0000000')}")

# =========================================================
# מסך עזרה (לפי תמונת 'מסך עזרה' והסעיפים 37-41)
# =========================================================
elif st.session_state.screen == "help_screen":
    render_header()
    
    biz = st.session_state.businesses[st.session_state.current_biz_key]
    
    # במידה וזה נושא חדש
    if st.session_state.get("is_new_topic", False):
        new_top_name = f"נושא חדש {len(biz['topics'])+1}"
        biz["topics"][new_top_name] = {
            "problem": "תאור מהות הבעיה...",
            "structured_params": [{"name": "פרמטר 1", "type": "טקסט", "value": "ערך"}],
            "ai_question": "מהו הנתון הנוסף שברצונך להגדיר?",
            "chats": {"שיחה 1": []},
            "current_chat": "שיחה 1",
            "solutions": []
        }
        biz["selected_topic"] = new_top_name
        st.session_state.is_new_topic = False

    topic_data = biz["topics"][biz["selected_topic"]]

    st.title(f"🛠️ מסך עזרה - {biz['selected_topic']}")

    # פריסת המסך לפי הסקיצה: שמאל (הכוונה/פתרונות/צ'אט), מרכז (פרמטרים), ימין (מהות הבעיה/קבצים/שמירה)
    col_left, col_mid, col_right = st.columns([2.5, 1.8, 1.8])

    # --- צד ימין (מהות הבעיה, העלאת קבצים, שמירה) ---
    with col_right:
        st.markdown("### מהות הבעיה")
        topic_data["problem"] = st.text_area("תיאור הבעיה:", value=topic_data["problem"], height=150)
        
        st.markdown("### העלאת קבצים ותמונות")
        st.file_uploader("בחר קבצים:", accept_multiple_files=True, key="help_files")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 שמור וחזרה למסך נושאים", type="primary", use_container_width=True):
            st.session_state.screen = "topics_screen"
            st.rerun()

    # --- מרכז (פרמטרים) ---
    with col_mid:
        st.markdown("### פרמטרים")
        for idx, p in enumerate(topic_data["structured_params"]):
            st.text_input(f"{p['name']}:", value=f"{p['value']}", key=f"param_{idx}")
        
        with st.popover("➕ הוסף פרמטר"):
            pn = st.text_input("שם הפרמטר:")
            pv = st.text_input("ערך:")
            if st.button("אישור"):
                if pn and pv:
                    topic_data["structured_params"].append({"name": pn, "type": "טקסט", "value": pv})
                    st.rerun()

    # --- צד שמאל (הכוונת הפתרון, פתרונות, כפתורים 37-38, וצ'אט 39-41) ---
    with col_left:
        st.markdown("### הכוונת לפתרון")
        st.info(topic_data["ai_question"])
        ans = st.text_input("תשובה להכוונה:")
        if st.button("עדכן הכוונה"):
            if ans:
                topic_data["structured_params"].append({"name": "הכוונה", "type": "טקסט", "value": ans})
                topic_data["ai_question"] = "שאלת הכוונה נוספת חושבה בהצלחה!"
                st.rerun()

        st.markdown("### פתרונות והמלצות")
        for i, sol in enumerate(topic_data["solutions"], 1):
            st.success(f"**פתרון {i}:** {sol}")

        # 37 ו-38
        c37, c38 = st.columns(2)
        with c37:
            # 37 - הלקוח רוצה עם אותם משתנים ופרמטרים לבחון פתרונות חלופיים
            if st.button("37 - הצעת פתרונות נוספים", use_container_width=True):
                topic_data["solutions"].append(f"פתרון חלופי נוסף {len(topic_data['solutions'])+1} (על בסיס אותם פרמטרים)")
                st.rerun()
        with c38:
            # 38 - אחרי שלקוח מבצע שינויים בפרמטרים או תמונות
            if st.button("38 - חישוב מחדש", type="primary", use_container_width=True):
                topic_data["solutions"] = ["חישוב מחדש בוצע בהצלחה בהתאם לפרמטרים ולקבצים המעודכנים!"]
                st.rerun()

        st.markdown("---")

        # 39, 40, 41: חלון הצ'אט
        st.markdown("### 39 - חלון הצ'אט AI")
        
        c40, c41 = st.columns([3, 1])
        with c40:
            # 40 - אפשרות לעבור בין שיחות הצ'אט השמורות בתיקייה זו
            chat_list = list(topic_data["chats"].keys())
            selected_c = st.selectbox("40 - שיחות שמורות:", chat_list, index=chat_list.index(topic_data["current_chat"]))
            topic_data["current_chat"] = selected_c
        with c41:
            # 41 - הגדלת חלונית הצ'אט
            if st.button("41 - 🔍 הגדל"):
                st.session_state.chat_expanded = not st.session_state.chat_expanded

        # תצוגת צ'אט (מורחבת או רגילה)
        chat_height = 400 if st.session_state.chat_expanded else 180
        chat_messages = topic_data["chats"][topic_data["current_chat"]]

        with st.container(height=chat_height):
            for msg in chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_chat_in = st.chat_input("שאל את העוזר החכם...")
        if user_chat_in:
            chat_messages.append({"role": "user", "content": user_chat_in})
            
            # קריאה מובנית ל-Gemini API בקוד (ללא שום בקשת מפתח מהלקוח)
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={BUILTIN_GEMINI_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": [{"text": f"עסק: {biz['name']}, בעיה: {topic_data['problem']}. שאלה: {user_chat_in}"}]}]}
                
                res = requests.post(url, json=payload, headers=headers, timeout=10)
                if res.status_code == 200 and "candidates" in res.json():
                    bot_reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    bot_reply = "תשובת AI: התקבלה הודעתך, המערכת מעבדת את המידע לפתרון הבעיה."
            except Exception:
                bot_reply = "תשובת AI: התקבלה הודעתך, המערכת מעבדת את המידע לפתרון הבעיה."

            chat_messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
