import streamlit as st

# 1. הגדרת תצורת עמוד ראשונית
st.set_page_config(
    page_title="OptiFlow AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. טיפול בטוח ביבוא ספריית Google GenAI
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# 3. אתחול מנגנון ניהול מצב (Session State)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "theme" not in st.session_state:
    st.session_state.theme = "כחול קלאסי (Classic Blue)"
if "font_family" not in st.session_state:
    st.session_state.font_family = "Heebo"
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "language" not in st.session_state:
    st.session_state.language = "עברית"

# 4. הגדרת פלטות צבעים ועיצוב דינמי
COLOR_PALETTES = {
    "כחול קלאסי (Classic Blue)": {
        "header_bg": "#003366",
        "header_text": "#ffffff",
        "card_header": "#004080",
        "accent": "#008040",
    },
    "כהה (Dark Mode)": {
        "header_bg": "#1e1e1e",
        "header_text": "#00e5ff",
        "card_header": "#2d2d2d",
        "accent": "#00b0ff",
    },
    "בהיר מודרני (Light Modern)": {
        "header_bg": "#2c3e50",
        "header_text": "#ecf0f1",
        "card_header": "#34495e",
        "accent": "#27ae60",
    }
}

current_colors = COLOR_PALETTES.get(st.session_state.theme, COLOR_PALETTES["כחול קלאסי (Classic Blue)"])

# 5. הזרקת עיצוב CSS מותאם אישית (RTL, גופנים, כרטיסיות וסרגל עליון)
custom_css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700&family=Rubik:wght@300;400;700&family=Assistant:wght@300;400;700&display=swap');

    html, body, [class*="css"] {{
        direction: rtl;
        text-align: right;
        font-family: '{st.session_state.font_family}', sans-serif !important;
        font-size: {st.session_state.font_size}px;
    }}

    /* סרגל עליון כהה ומכובד */
    .top-header {{
        background-color: {current_colors['header_bg']};
        color: {current_colors['header_text']};
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid {current_colors['accent']};
        margin-bottom: 25px;
        border-radius: 4px;
    }}
    .top-header .logo-area {{
        font-size: 1.4em;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .top-header .user-area {{
        font-size: 0.9em;
    }}

    /* עיצוב כרטיסיות המידע */
    .info-card {{
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        overflow: hidden;
    }}
    .info-card-header {{
        background-color: {current_colors['card_header']};
        color: #ffffff;
        padding: 10px 16px;
        font-weight: bold;
        font-size: 1.1em;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .info-card-body {{
        padding: 16px;
        color: #333333;
    }}

    /* כפתורי פעולה בולטים */
    .stButton > button {{
        background-color: {current_colors['accent']} !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 8px 20px !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# מסך 1: התחברות למערכת (מוצג בלבד אם לא מחובר)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
            <div style="background-color: {current_colors['header_bg']}; padding: 15px; border-radius: 8px 8px 0 0; color: white; text-align: center;">
                <h2>🚀 כניסה למערכת OptiFlow AI</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("שם משתמש")
            password = st.text_input("סיסמה", type="password")
            submit = st.form_submit_button("התחבר למערכת", use_container_width=True)
            
            if submit:
                if username and password:  # כאן ניתן לשלב אימות מול מסד נתונים
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("נא להזין שם משתמש וסיסמה תקינים.")
    st.stop()


# ==========================================
# מסך 2: המערכת הראשית (לאחר התחברות מוצלחת)
# ==========================================

# 1. סרגל כלים עליון מעוצב (RTL: לוגו מימין, משתמש וביצועים משמאל)
st.markdown(f"""
    <div class="top-header">
        <div class="logo-area">
            🚀 OptiFlow AI | מנהל מערכת
        </div>
        <div class="user-area">
            שלום, <b>{st.session_state.username}</b> | 
            <span style="color: #a0a0a0;">שפה: {st.session_state.language}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# הודעת שגיאה/אזהרה שקופה במידה וספריית GenAI אינה מותקנת בסביבה
if not GENAI_AVAILABLE:
    st.warning("⚠️ ספריית `google-genai` אינה מותקנת בסביבת העבודה. נא לוודא הוספת `google-genai` לקובץ `requirements.txt`.")

# 2. ניווט בלשוניות (Tabs) בצורה מסודרת
tab_home, tab_settings, tab_contact = st.tabs(["🏠 מסך ראשי", "⚙️ הגדרות מערכת", "📞 צור קשר"])

# --- לשונית 1: מסך ראשי ---
with tab_home:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
            <div class="info-card">
                <div class="info-card-header">👤 פרטים אישיים</div>
                <div class="info-card-body">
                    <p><b>שם משתמש:</b> """ + st.session_state.username + """</p>
                    <p><b>סטטוס חשבון:</b> פעיל (מורשה מערכת)</p>
                    <p><b>תאריך חיבור:</b> מחובר כעת</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
            <div class="info-card">
                <div class="info-card-header">📊 פרטי זכאות ותפעול</div>
                <div class="info-card-body">
                    <p><b>סוג מנוי:</b> OptiFlow Enterprise AI</p>
                    <p><b>מכסת ניתוחים:</b> ללא הגבלה</p>
                    <p><b>סטטוס שרתים:</b> תקין לקבלה ולעיבוד</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="info-card">
            <div class="info-card-header">📝 טופס עדכון נתונים</div>
            <div class="info-card-body">
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("דואר אלקטרוני", value="user@example.com")
    with c2:
        st.text_input("מספר טלפון נייד", value="050-0000000")
        
    if st.button("עדכן נתונים"):
        st.success("הנתונים עודכנו בהצלחה במערכת!")
        
    st.markdown("</div></div>", unsafe_allow_html=True)


# --- לשונית 2: הגדרות מערכת (כולל התאמה מורחבת) ---
with tab_settings:
    st.subheader("⚙️ הגדרות תצוגה וממשק")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        new_lang = st.selectbox(
            "שפת ממשק:",
            ["עברית", "English", "العربية"],
            index=["עברית", "English", "العربية"].index(st.session_state.language)
        )
        
        new_theme = st.selectbox(
            "ערכת נושא (צבעים):",
            list(COLOR_PALETTES.keys()),
            index=list(COLOR_PALETTES.keys()).index(st.session_state.theme)
        )

    with col_s2:
        new_font = st.selectbox(
            "סגנון גופן (Font Family):",
            ["Heebo", "Rubik", "Assistant"],
            index=["Heebo", "Rubik", "Assistant"].index(st.session_state.font_family)
        )
        
        new_size = st.slider(
            "גודל גופן (בפיקסלים):",
            min_value=12,
            max_value=22,
            value=st.session_state.font_size
        )
        
    st.markdown("---")
    
    if st.button("שמור הגדרות"):
        st.session_state.language = new_lang
        st.session_state.theme = new_theme
        st.session_state.font_family = new_font
        st.session_state.font_size = new_size
        st.success("ההגדרות שנבחרו נשמרו בהצלחה!")
        st.rerun()


# --- לשונית 3: צור קשר ---
with tab_contact:
    st.subheader("📞 יצירת קשר ותמיכה טכנית")
    st.write("לכל שאלה, בעיה טכנית או בקשה לפיתוח מותאם אישית, ניתן לפנות אלינו באמצעות הטופס:")
    
    st.text_input("נושא הפנייה")
    st.text_area("תוכן ההודעה")
    if st.button("שלח פנייה"):
        st.info("פנייתך התקבלה ותענה בהקדם.")

# 3. אפשרות התנתקות בתחתית
st.markdown("---")
if st.button("🚪 התנתק מהמערכת"):
    st.session_state.authenticated = False
    st.rerun()
