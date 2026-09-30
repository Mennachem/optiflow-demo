import streamlit as st

# הגדרת תצורת העמוד
st.set_page_config(
    page_title="OptiFlow AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# הגדרת מצב הניווט (Session State)
if "page" not in st.mutable_state if hasattr(st, 'mutable_state') else st.session_state:
    st.session_state["page"] = "screen_1"

def set_page(page_name):
    st.session_state["page"] = page_name

# עיצוב CSS מותאם אישית לתמיכה ב-RTL ובמראה הנקי
st.markdown("""
<style>
    /* כיוון טקסט RTL */
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* הסתרת סרגל צד דיפולטיבי במידת הצורך */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* כותרת עליונה */
    .app-header {
        background-color: #003366;
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    /* עיצוב כרטיסים */
    .custom-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    .card-title {
        background-color: #003366;
        color: white;
        padding: 10px 15px;
        border-radius: 6px 6px 0 0;
        margin: -20px -20px 15px -20px;
        font-weight: bold;
        font-size: 1.1rem;
    }

    /* כפתור עסק חדש בצד שמאל למטה */
    .create-btn-container {
        display: flex;
        justify-content: flex-start;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# מסך 1: התחברות
# ==========================================
if st.session_state["page"] == "screen_1":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2 style="margin:0;">OptiFlow AI 🚀 (1)</h2>
                <p style="margin:5px 0 0 0; font-size:0.9rem;">כניסה למערכת</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.text_input("שם משתמש (2)", key="login_user")
            st.text_input("סיסמה (3)", type="password", key="login_pass", help="לחץ על האייקון בצד שמאל לצפייה בסיסמה")
            
            # כפתור שכחתי שם משתמש / סיסמה
            if st.button("שכחתי שם משתמש או סיסמה (4)", type="secondary"):
                set_page("screen_2")
                st.rerun()
            
            st.write("")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("התחברות (5)", type="primary", use_container_width=True):
                    set_page("screen_main")
                    st.rerun()
            with col_b2:
                if st.button("הירשם (6)", use_container_width=True):
                    set_page("screen_3")
                    st.rerun()


# ==========================================
# מסך 2: שכחתי שם משתמש / סיסמה
# ==========================================
elif st.session_state["page"] == "screen_2":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2 style="margin:0;">OptiFlow AI 🚀</h2>
                <p style="margin:5px 0 0 0;">שחזור פרטי גישה למערכת</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.text_input("דואר אלקטרוני לשחזור (7)")
        st.text_input("מספר טלפון (8)")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.button("שלח קוד (9)", type="primary", use_container_width=True)
        with col_b:
            if st.button("ביטול (10)", use_container_width=True):
                set_page("screen_1")
                st.rerun()
                
        if st.button("אישור ושחזור (11)", use_container_width=True):
            st.success("הוראות שחזור נשלחו בהצלחה!")


# ==========================================
# מסך 3: הרשמה למערכת
# ==========================================
elif st.session_state["page"] == "screen_3":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2 style="margin:0;">OptiFlow AI 🚀</h2>
                <p style="margin:5px 0 0 0;">הרשמה למערכת</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_name1, col_name2 = st.columns(2)
        with col_name1:
            st.text_input("שם פרטי (12)")
        with col_name2:
            st.text_input("שם משפחה (13)")
            
        st.text_input('דוא"ל (15)')
        st.text_input("טלפון (16)")
        st.text_input("סיסמה (17)", type="password")
        
        if st.button("סיום הרשמה (18)", type="primary", use_container_width=True):
            set_page("screen_main")
            st.rerun()
            
        if st.button("חזרה להתחברות", use_container_width=True):
            set_page("screen_1")
            st.rerun()


# ==========================================
# המסך הראשי (לקוח)
# ==========================================
elif st.session_state["page"] == "screen_main":
    # כותרת עליונה + לוגו מימין שניתן ללחוץ עליו לחזרה
    st.markdown("""
        <div class="app-header">
            <div><strong>OptiFlow AI | מנהל מערכת 🚀</strong></div>
            <div>שלום, רובי | שפה: עברית</div>
        </div>
    """, unsafe_allow_html=True)

    # סרגל כלים עליון
    c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
    with c1:
        st.button("🏠 מסך ראשי")
    with c2:
        st.button("⚙️ הגדרות")
    with c3:
        st.button("📞 צור קשר")

    st.markdown("<hr style='margin: 10px 0 20px 0;'>", unsafe_allow_html=True)

    # חלוקת המסך לפי הסקיצה:
    # בצד ימין (col_right): משבצת אחת מאוחדת של פרטי לקוח
    # בצד שמאל (col_left): נושאים ועסקים בלחיצה
    col_left, col_right = st.columns([2, 1])

    with col_right:
        st.markdown("""
            <div class="custom-card">
                <div class="card-title">👤 פרטי לקוח</div>
                <p><strong>שם משתמש:</strong> רובי</p>
                <p><strong>סטטוס חשבון:</strong> פעיל (מורשה מערכת)</p>
                <p><strong>תאריך חיבור:</strong> מחובר כעת</p>
                <hr>
                <p><strong>סוג מנוי:</strong> OptiFlow Enterprise AI</p>
                <p><strong>מכסת ניתוחים:</strong> ללא הגבלה</p>
                <p><strong>סטטוס שרתים:</strong> תקין לקבלה ולעיבוד</p>
                <hr>
                <p><strong>דואר אלקטרוני:</strong> user@example.com</p>
                <p><strong>מספר טלפון:</strong> 050-0000000</p>
            </div>
        """, unsafe_allow_html=True)

    with col_left:
        st.markdown("""
            <div class="custom-card">
                <div class="card-title">📂 נושאים ועסקים</div>
            </div>
        """, unsafe_allow_html=True)
        
        # רשימת העסקים / הנושאים
        with st.expander("🏢 עסק / נושא 1", expanded=True):
            st.write("פירוט הנושא, נתונים מדדי ביצוע ודוחות פעילים עבור עסק 1.")
            st.button("פתיחת לוח בקרה עסק 1", key="b1")
            
        with st.expander("🏢 עסק / נושא 2"):
            st.write("פירוט הנושא, נתונים מדדי ביצוע ודוחות פעילים עבור עסק 2.")
            st.button("פתיחת לוח בקרה עסק 2", key="b2")

        with st.expander("🏢 עסק / נושא 3"):
            st.write("פירוט הנושא, נתונים מדדי ביצוע ודוחות פעילים עבור עסק 3.")
            st.button("פתיחת לוח בקרה עסק 3", key="b3")

        # כפתור ליצירת עסק חדש בתחתית צד שמאל
        st.markdown('<div class="create-btn-container">', unsafe_allow_html=True)
        if st.button("➕ צור עסק חדש", type="primary"):
            st.toast("נפתחה חלונית ליצירת עסק חדש")
        st.markdown('</div>', unsafe_allow_html=True)
