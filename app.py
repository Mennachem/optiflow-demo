import streamlit as st

# ==========================================
# 0. הגדרת API Key מובנה (נסתר מהלקוח)
# ==========================================
BUILTIN_API_KEY = "YOUR_EMBEDDED_GEMINI_API_KEY_HERE"

st.set_page_config(
    page_title="OptiFlow AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# אתחול מצבי ניווט ונתונים ב-Session State
if "page" not in st.session_state:
    st.session_state["page"] = "screen_1"

# מסד נתונים מדומה למשתמשים רשומים
if "registered_users" not in st.session_state:
    st.session_state["registered_users"] = {"רובי": "1234", "admin": "admin"}

if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None

# נתוני עסקים ונושאים דינמיים של הלקוח
if "businesses" not in st.session_state:
    st.session_state["businesses"] = [
        {"id": 1, "name": "עסק 1 - חנות דיגיטלית", "topics": ["תמיכה טכנית", "ניהול מלאי"]},
        {"id": 2, "name": "עסק 2 - ייעוץ עסקי", "topics": ["שיווק ומכירות", "אסטרטגיה"]}
    ]

if "selected_business" not in st.session_state:
    st.session_state["selected_business"] = None

if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = {}

if "chat_fullscreen" not in st.session_state:
    st.session_state["chat_fullscreen"] = False

def navigate_to(page_name):
    st.session_state["page"] = page_name
    st.rerun()

# עיצוב CSS מתקדם למיקומים קבועים ואיכותיים
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }

    /* סרגל עליון קבוע */
    .header-bar {
        background-color: #003366;
        color: white;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 6px;
        margin-bottom: 20px;
    }

    .logo-container {
        cursor: pointer;
        font-size: 1.4rem;
        font-weight: bold;
    }

    .card-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .card-header-title {
        background-color: #003366;
        color: white;
        padding: 10px 15px;
        border-radius: 6px 6px 0 0;
        margin: -20px -20px 15px -20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# סרגל עליון מובנה קבוע (לוגו מימין, סרגל משמאל)
# ==========================================
def render_header():
    col_logo, col_space, col_menu = st.columns([2, 4, 3])
    
    with col_logo:
        # לחיצה על הלוגו מחזירה למסך ראשי אם מחובר, או למסך 1
        if st.button("🚀 OptiFlow AI", key="header_logo_btn", type="tertiary"):
            if st.session_state["logged_in_user"]:
                navigate_to("screen_main")
            else:
                navigate_to("screen_1")
                
    with col_menu:
        if st.session_state["logged_in_user"]:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                if st.button("🏠 ראשי", key="nav_home"): navigate_to("screen_main")
            with m2:
                if st.button("⚙️ הגדרות", key="nav_settings"): navigate_to("screen_settings")
            with m3:
                if st.button("📞 צור קשר", key="nav_contact"): navigate_to("screen_contact")
            with m4:
                if st.button("🚪 יציאה", key="nav_logout"):
                    st.session_state["logged_in_user"] = None
                    navigate_to("screen_1")


# ==========================================
# מסך 1: התחברות ובדיקת משתמש קיים
# ==========================================
if st.session_state["page"] == "screen_1":
    render_header()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
            <div style="background-color: #003366; color: white; padding: 18px; text-align: center; border-radius: 8px 8px 0 0;">
                <h3 style="margin:0;">כניסה למערכת</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("שם משתמש")
            password = st.text_input("סיסמה", type="password")
            
            submit_login = st.form_submit_button("התחברות", use_container_width=True)
            
            if submit_login:
                if username in st.session_state["registered_users"]:
                    if st.session_state["registered_users"][username] == password:
                        st.session_state["logged_in_user"] = username
                        navigate_to("screen_main")
                    else:
                        st.error("סיסמה שגויה. נסה שוב.")
                else:
                    st.error("שם משתמש אינו קיים במערכת, לקוח לא רשום.")
                    if st.form_submit_button("לחץ כאן להרשמה (הירשם כאן)"):
                        navigate_to("screen_3")

        st.write("---")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("שכחתי שם משתמש או סיסמה", use_container_width=True):
                navigate_to("screen_2")
        with col_f2:
            if st.button("הרשמה למשתמש חדש", use_container_width=True):
                navigate_to("screen_3")


# ==========================================
# מסך 2: שחזור פרטים
# ==========================================
elif st.session_state["page"] == "screen_2":
    render_header()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.subheader("שחזור שם משתמש / סיסמה")
        st.text_input("דואר אלקטרוני לשחזור")
        st.text_input("מספר טלפון נייד")
        if st.button("שלח קוד אימות", type="primary", use_container_width=True):
            st.success("קוד אימות נשלח לטלפון שלך.")
        if st.button("חזרה למסך התחברות", use_container_width=True):
            navigate_to("screen_1")


# ==========================================
# מסך 3: הרשמת לקוח חדש
# ==========================================
elif st.session_state["page"] == "screen_3":
    render_header()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
            <div style="background-color: #003366; color: white; padding: 15px; text-align: center; border-radius: 8px 8px 0 0;">
                <h3 style="margin:0;">הרשמת לקוח חדש (מסך 3)</h3>
            </div>
        """, unsafe_allow_html=True)
        
        new_name = st.text_input("שם ושם משפחה (12)")
        new_phone = st.text_input("נייד (13)")
        new_email = st.text_input("דוא\"ל (14)")
        new_address = st.text_input("כתובת הלקוח (15)")
        new_notes = st.text_area("הערות (16)")
        new_pass = st.text_input("בחר סיסמה", type="password")

        if st.button("אישור והמשך לבחירת תוכנית (18)", type="primary", use_container_width=True):
            if new_name and new_pass:
                st.session_state["registered_users"][new_name] = new_pass
                st.session_state["logged_in_user"] = new_name
                navigate_to("screen_4")
            else:
                st.warning("נא למלא שם משתמש וסיסמה.")


# ==========================================
# מסך 4: בחירת תוכנית
# ==========================================
elif st.session_state["page"] == "screen_4":
    render_header()
    st.title("בחירת תוכנית מנוי (מסך 4)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### בסיסי")
        st.write("גישה לניהול עסק יחיד")
        if st.button("בחר בסיסי"): navigate_to("screen_main")
    with col2:
        st.markdown("### מקצועי")
        st.write("גישה לעד 5 עסקים + AI מלא")
        if st.button("בחר מקצועי", type="primary"): navigate_to("screen_main")
    with col3:
        st.markdown("### פרימיום")
        st.write("עסקים ללא הגבלה ותמיכה 24/7")
        if st.button("בחר פרימיום"): navigate_to("screen_main")


# ==========================================
# המסך הראשי של הלקוח: רשימת עסקים + פרטי לקוח
# ==========================================
elif st.session_state["page"] == "screen_main":
    render_header()
    
    col_left, col_right = st.columns([2, 1])

    with col_right:
        st.markdown(f"""
            <div class="card-box">
                <div class="card-header-title">👤 פרטי לקוח</div>
                <p><strong>שם לקוח:</strong> {st.session_state['logged_in_user']}</p>
                <p><strong>סטטוס:</strong> פעיל</p>
                <hr>
                <p><strong>סוג מנוי:</strong> OptiFlow Pro AI</p>
                <p><strong>מכסת ניתוחים:</strong> ללא הגבלה</p>
            </div>
        """, unsafe_allow_html=True)

    with col_left:
        st.subheader("🏢 העסקים שלי")
        
        for bus in st.session_state["businesses"]:
            with st.container():
                st.markdown(f"### {bus['name']}")
                if st.button(f"כנס לעסק: {bus['name']}", key=f"bus_btn_{bus['id']}", type="primary"):
                    st.session_state["selected_business"] = bus
                    navigate_to("screen_topics")
                st.write("---")

        # יצירת עסק חדש
        with st.expander("➕ צור עסק חדש"):
            new_bus_name = st.text_input("שם העסק החדש")
            if st.button("שמור עסק"):
                if new_bus_name:
                    new_id = len(st.session_state["businesses"]) + 1
                    st.session_state["businesses"].append({"id": new_id, "name": new_bus_name, "topics": []})
                    st.success("העסק נשמר בהצלחה!")
                    st.rerun()


# ==========================================
# מסך נושאים (השייכים לעסק שנבחר)
# ==========================================
elif st.session_state["page"] == "screen_topics":
    render_header()
    
    bus = st.session_state["selected_business"]
    st.button("⬅️ חזרה לרשימת העסקים", onclick=lambda: navigate_to("screen_main"))
    
    st.title(f"📂 נושאים עבור: {bus['name']}")
    
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        if not bus["topics"]:
            st.info("אין נושאים פתוחים עבור עסק זה עדיין.")
        else:
            for topic in bus["topics"]:
                if st.button(f"📌 נושא: {topic}", key=f"top_{topic}", use_container_width=True):
                    st.session_state["selected_topic"] = topic
                    navigate_to("screen_help")

    with col_t2:
        st.markdown("### צור נושא חדש")
        new_topic = st.text_input("שם הנושא החדש")
        if st.button("➕ צור נושא ועבור למסך עזרה", type="primary"):
            if new_topic:
                bus["topics"].append(new_topic)
                st.session_state["selected_topic"] = new_topic
                navigate_to("screen_help")


# ==========================================
# מסך עזרה / צ'אט (עם כפתורי 37, 38, 39, 40, 41)
# ==========================================
elif st.session_state["page"] == "screen_help":
    render_header()
    
    topic = st.session_state.get("selected_topic", "כללי")
    st.button("⬅️ חזרה לרשימת הנושאים", onclick=lambda: navigate_to("screen_topics"))
    
    st.title(f"🛠️ מסך עזרה ופתרונות - {topic}")
    
    # בקרות עליונות של הצ'אט והפתרונות
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        if st.button("💡 הצעת פתרונות נוספים (37)", type="primary", use_container_width=True):
            st.info("בוחן פתרונות חלופיים תוך שמירה על אותם משתנים ופרמטרים...")
    with col_b:
        if st.button("🔄 חישוב מחדש (38)", use_container_width=True):
            st.success("מבצע חישוב מחדש לאחר שינוי הפרמטרים/התמונות...")
    with col_c:
        if st.button("🔍 הגדל/מזער חלונית צ'אט (41)", use_container_width=True):
            st.session_state["chat_fullscreen"] = not st.session_state["chat_fullscreen"]
            st.rerun()

    st.write("---")

    col_chat_main, col_chat_history = st.columns([3, 1])

    # 40 - מעבר בין שיחות צ'אט שמורות
    with col_chat_history:
        st.markdown("### 📁 שיחות שמורות (40)")
        st.selectbox("בחר שיחה מהתיקייה:", ["שיחה 1 - ניתוח ראשוני", "שיחה 2 - מעקב פרמטרים"])

    # 39 - חלון הצ'אט
    with col_chat_main:
        st.markdown("### 💬 חלון הצ'אט (39)")
        
        chat_key = f"chat_{topic}"
        if chat_key not in st.session_state["chat_history"]:
            st.session_state["chat_history"][chat_key] = [
                {"role": "assistant", "content": f"שלום! איך אוכל לעזור לך בנושא {topic}?"}
            ]

        # הצגת ההיסטוריה
        for msg in st.session_state["chat_history"][chat_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # קלט משתמש
        user_input = st.chat_input("רשום הודעה או שאלה בנושא...")
        if user_input:
            st.session_state["chat_history"][chat_key].append({"role": "user", "content": user_input})
            # מענה אוטומטי מבוסס מודל
            st.session_state["chat_history"][chat_key].append({
                "role": "assistant", 
                "content": f"קיבלתי את פנייתך לגבי '{user_input}'. המערכת מעבדת את הנתונים ומכינה פתרון מותאם."
            })
            st.rerun()


# ==========================================
# מסכי הגדרות וצור קשר
# ==========================================
elif st.session_state["page"] == "screen_settings":
    render_header()
    st.title("⚙️ הגדרות מערכת")
    st.write("מפתח ה-API מוגדר דינמית במערכת ואינו מופיע כאן לשמירה על אבטחה.")
    st.selectbox("ערכת נושא", ["כחול קלאסי", "כהה", "בהיר"])

elif st.session_state["page"] == "screen_contact":
    render_header()
    st.title("📞 צור קשר")
    st.text_area("תוכן הפנייה")
    if st.button("שלח"): st.success("הפנייה נשלחה!")
