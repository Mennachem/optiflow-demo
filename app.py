import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד ועיצוב סרגל כלים מקצועי (Navbar)
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמה חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# עיצוב Custom CSS לסרגל כלים מקצועי ונקי (כמו בדוגמאות)
st.markdown("""
<style>
    /* עיצוב סרגל עליון שטוח ומודרני */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #ffffff;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 20px;
        direction: rtl;
    }
    .stButton>button {
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    /* ביטול מסגרות גסות בסרגל העליון */
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
</style>
""", unsafe_allow_html=True)

# שליפת מפתח API
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ---------------------------------------------------------
# 2. אתחול Session State ומסד נתונים פנימי
# ---------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "screen_1"

if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = GEMINI_API_KEY

if "businesses" not in st.session_state:
    st.session_state.businesses = {
        "חד וחלק": {
            "nature": "חיתוך פלסטיק בלייזר",
            "address": "אזור תעשייה",
            "tech_data": "מכונת חיתוך לייזר CO2 100W",
            "folders": {
                "תיקייה ראשית": {
                    "problem": "סדקים בשולי הפלסטיק בעת חיתוך בלייזר עוצמתי.",
                    "structured_params": [
                        {"name": "סוג חומר", "type": "טקסט", "value": "פלסטיק אקרילי"},
                        {"name": "מהירות חיתוך", "type": "מספר", "value": 150, "unit": "mm/s"},
                        {"name": "עוצמת לייזר", "type": "מספר", "value": 80, "unit": "W"}
                    ],
                    "ai_question": "מהו עובי החומר (ב-מ\"מ) שבו מתרחשים הסדקים?",
                    "chats": {"שיחה ראשית": []},
                    "current_chat": "שיחה ראשית",
                    "solutions": []
                }
            },
            "current_folder": "תיקייה ראשית"
        }
    }

if "current_business" not in st.session_state:
    st.session_state.current_business = "חד וחלק"

def get_biz():
    return st.session_state.businesses[st.session_state.current_business]

def get_folder():
    biz = get_biz()
    return biz["folders"][biz["current_folder"]]

# ---------------------------------------------------------
# 3. סרגל כלים מקצועי ונקי (כמו בדוגמאות 1 ו-2)
# ---------------------------------------------------------
def render_toolbar():
    tb_logo, tb_biz, tb_nav1, tb_nav2, tb_nav3, tb_nav4 = st.columns([2, 2.5, 1.5, 1.5, 1.5, 1.5])
    
    with tb_logo:
        st.markdown("<h3 style='margin:0; color:#1f2937; text-align:right;'>🚀 OptiFlow</h3>", unsafe_allow_html=True)

    with tb_biz:
        biz_list = list(st.session_state.businesses.keys())
        selected_b = st.selectbox("עסק פעיל", biz_list, index=biz_list.index(st.session_state.current_business), label_visibility="collapsed")
        if selected_b != st.session_state.current_business:
            st.session_state.current_business = selected_b
            st.rerun()

    with tb_nav1:
        if st.button("🏠 מסך ראשי", use_container_width=True):
            st.session_state.screen = "main_screen"
            st.rerun()

    with tb_nav2:
        if st.button("👤 פרטי עסק", use_container_width=True):
            st.session_state.screen = "profile_screen"
            st.rerun()

    with tb_nav3:
        with st.popover("⚙️ הגדרות & API"):
            st.write("**מפתח Gemini API:**")
            key_in = st.text_input("הכנס מפתח API:", value=st.session_state.api_key_input, type="password")
            if key_in != st.session_state.api_key_input:
                st.session_state.api_key_input = key_in
                st.success("מפתח ה-API עודכן!")

    with tb_nav4:
        with st.popover("📞 צור קשר"):
            st.write("**תמיכה טכנית**")
            st.write("מייל: support@optiflow.ai")

    st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# =========================================================
# מסך 1: התחברות (כולל תמיכה ב-Autofill / Google Passwords)
# =========================================================
if st.session_state.screen == "screen_1":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🚀 OptiFlow AI")
        st.subheader("התחברות למערכת")

        # שימוש ב-st.form מאפשר לדפדפן/גוגל לזהות ולשמור שם משתמש וסיסמה
        with st.form(key="login_form"):
            username = st.text_input("שם משתמש:", autocomplete="username")
            password = st.text_input("סיסמה:", type="password", autocomplete="current-password")
            submit_login = st.form_submit_button("התחברות", type="primary", use_container_width=True)

            if submit_login:
                if username and password:
                    st.session_state.screen = "main_screen"
                    st.rerun()
                else:
                    st.error("אנא הכנס שם משתמש וסיסמה.")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("שכחתי פרטים", use_container_width=True):
                st.session_state.screen = "screen_2"
                st.rerun()
        with col_btn2:
            if st.button("לקוח חדש? הירשם כאן", use_container_width=True):
                st.session_state.screen = "screen_3"
                st.rerun()

# =========================================================
# מסך ראשי: פאנל עבודה דינמי
# =========================================================
elif st.session_state.screen == "main_screen":
    render_toolbar()

    biz = get_biz()
    folder = get_folder()

    row1_left, row1_mid, row1_right = st.columns([2, 1.8, 1.8])

    # --- צד שמאל: פתרונות והמלצות דינמיות ---
    with row1_left:
        st.subheader("💡 פתרונות והמלצות")
        
        if folder["solutions"]:
            for i, sol in enumerate(folder["solutions"], 1):
                st.success(f"**פתרון {i}:** {sol}")
        else:
            st.info("לחץ על 'חישוב מחדש' או 'הצעת פתרונות נוספים' לקבלת המלצות.")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("הצעת פתרונות נוספים", use_container_width=True):
                # הפקת פתרון דינמי לפי הפרמטרים
                params_summary = ", ".join([f"{p['name']}: {p['value']}" for p in folder['structured_params']])
                new_sol = f"אופטימיזציה מותאמת לפרמטרים ({params_summary}): התאמת פולס הלייזר וקירור אוויר מוגבר."
                folder["solutions"].append(new_sol)
                st.rerun()

        with btn_c2:
            if st.button("חישוב מחדש", type="primary", use_container_width=True):
                folder["solutions"] = [
                    f"כיול מחדש לפי הפרמטר העדכני: {folder['structured_params'][-1]['name'] if folder['structured_params'] else 'כללי'}",
                    "בדיקת עדשות ומערכת הקרנת הלייזר"
                ]
                st.toast("החישוב בוצע מחדש בהצלחה!")
                st.rerun()

    # --- מרכז: מנוע הכוונה AI שיוצר פרמטרים ומחשב שאלות חדשות ---
    with row1_mid:
        st.subheader("🤖 AI מנוע הכוונה")
        st.write("**שאלת הכוונה לדיוק הנתונים:**")
        
        st.info(folder["ai_question"])
        
        param_name = st.text_input("שם הפרמטר שיוגדר:", value="מאפיין מופק")
        param_value = st.text_input("תשובתך / ערך הפרמטר:")

        if st.button("עדכן נתוני הכוונה", use_container_width=True, type="primary"):
            if param_value:
                # 1. הוספת הפרמטר לרשימת הפרמטרים המובנית
                folder["structured_params"].append({
                    "name": param_name if param_name else "הכוונה",
                    "type": "טקסט",
                    "value": param_value
                })
                
                # 2. חישוב שאלת הכוונה חדשה שנוצרת בהתאם
                folder["ai_question"] = f"בהתחשב בכך ש-{param_name} הוא '{param_value}', מהי טמפרטורת העבודה או לחץ האוויר במכונה?"
                st.success("הפרמטר נוצר בהצלחה ושאלת הכוונה חדשה חושבה!")
                st.rerun()

    # --- צד ימין: הוספה וניהול פרמטרים מובנים (טקסט / מספר / משתנה) ---
    with row1_right:
        folder_list = list(biz["folders"].keys())
        selected_f = st.selectbox("בחירת תיקייה:", folder_list, index=folder_list.index(biz["current_folder"]))
        if selected_f != biz["current_folder"]:
            biz["current_folder"] = selected_f
            st.rerun()

        folder["problem"] = st.text_area("מהות הבעיה:", value=folder["problem"], height=70)

        st.write("**פרמטרים ונתונים מובנים:**")
        
        # תצוגת הפרמטרים הקיימים
        for idx, p in enumerate(folder["structured_params"]):
            c_p1, c_p2 = st.columns([3, 1])
            with c_p1:
                unit_str = f" {p.get('unit', '')}" if p.get('unit') else ""
                st.text_input(f"{p['name']} ({p['type']}):", value=f"{p['value']}{unit_str}", key=f"p_{idx}")
            with c_p2:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"del_{idx}"):
                    folder["structured_params"].pop(idx)
                    st.rerun()

        # פופאובר להוספת פרמטר חדש (מספר / טקסט / משתנה)
        with st.popover("➕ הוסף פרמטר חדש"):
            p_type = st.selectbox("סוג הפרמטר:", ["טקסט", "מספר", "משתנה"])
            p_n = st.text_input("שם הפרמטר:")
            p_v = st.text_input("ערך הפרמטר:")
            p_u = st.text_input("יחידת מידה (אופציונלי):") if p_type == "מספר" else ""
            
            if st.button("אישור הוספה"):
                if p_n and p_v:
                    folder["structured_params"].append({"name": p_n, "type": p_type, "value": p_v, "unit": p_u})
                    st.rerun()

        st.file_uploader("העלאת תמונות וקבצים:", accept_multiple_files=True)

    st.markdown("---")

    # --- חלק תחתון: צ'אט מחובר יציב ל-API ---
    c_chat, c_info = st.columns([3, 1])
    with c_chat:
        st.subheader("💬 חלון צ'אט AI")
        
        chat_list = list(folder["chats"].keys())
        selected_chat = st.selectbox("שיחות שמורות:", chat_list, index=chat_list.index(folder["current_chat"]), label_visibility="collapsed")
        if selected_chat != folder["current_chat"]:
            folder["current_chat"] = selected_chat
            st.rerun()

        current_messages = folder["chats"][folder["current_chat"]]
        for msg in current_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("שאל את העוזר החכם בנוגע לבעיה...")
        if user_input:
            current_messages.append({"role": "user", "content": user_input})
            st.chat_message("user").markdown(user_input)

            api_key = st.session_state.api_key_input
            if not api_key:
                st.error("לא הוגדר מפתח Gemini API. אנא הכנס מפתח בלשונית 'הגדרות & API' בסרגל העליון.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("מעבד תשובה..."):
                        try:
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                            headers = {"Content-Type": "application/json"}
                            
                            p_summary = ", ".join([f"{p['name']}: {p['value']}" for p in folder['structured_params']])
                            prompt_context = f"עסק: {st.session_state.current_business}, תחום: {biz['nature']}. בעיה: {folder['problem']}. פרמטרים: {p_summary}. ענה בקצרה ומקצועיות: {user_input}"
                            
                            payload = {"contents": [{"parts": [{"text": prompt_context}]}]}

                            res = requests.post(url, json=payload, headers=headers)
                            res_json = res.json()

                            if res.status_code == 200 and "candidates" in res_json:
                                reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                st.markdown(reply)
                                current_messages.append({"role": "assistant", "content": reply})
                            else:
                                err_msg = res_json.get("error", {}).get("message", "שגיאה בחיבור ל-API")
                                st.error(f"שגיאת API: {err_msg}")
                        except Exception as e:
                            st.error(f"שגיאה בהתקשרות: {e}")

# =========================================================
# מסכים משלימים (שחזור / הרשמה / פרופיל)
# =========================================================
elif st.session_state.screen == "screen_2":
    st.title("🔑 שחזור סיסמה")
    if st.button("חזרה להתחברות"):
        st.session_state.screen = "screen_1"
        st.rerun()

elif st.session_state.screen == "screen_3":
    st.title("📝 הרשמה")
    if st.button("חזרה להתחברות"):
        st.session_state.screen = "screen_1"
        st.rerun()

elif st.session_state.screen == "profile_screen":
    render_toolbar()
    st.title("👤 פרטי הלקוח והעסק")
    biz = get_biz()
    biz["nature"] = st.text_input("מהות העסק:", value=biz["nature"])
    if st.button("שמור וחזור"):
        st.session_state.screen = "main_screen"
        st.rerun()
