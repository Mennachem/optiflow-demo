import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. הגדרות תצורת עמוד
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמה חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ---------------------------------------------------------
# 2. אתחול Session State ומסד נתונים פנימי לפי עסקים ותיקיות
# ---------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "screen_1"

if "show_password" not in st.session_state:
    st.session_state.show_password = False

# מאגר הנתונים המופרד לכל עסק
if "businesses" not in st.session_state:
    st.session_state.businesses = {
        "חד וחלק": {
            "nature": "חיתוך פלסטיק בלייזר",
            "address": "אזור תעשייה",
            "tech_data": "מכונת חיתוך לייזר CO2 100W, תוכנת AutoCAD",
            "folders": {
                "תיקייה ראשית": {
                    "problem": "סדקים בשולי הפלסטיק בעת חיתוך בלייזר עוצמתי.",
                    "params": "מהירות: 150mm/s, עוצמה: 80W",
                    "chats": {
                        "שיחה ראשית": []
                    },
                    "current_chat": "שיחה ראשית",
                    "solutions": []
                }
            },
            "current_folder": "תיקייה ראשית"
        }
    }

if "current_business" not in st.session_state:
    st.session_state.current_business = "חד וחלק"

# הגדרות תצוגה
if "theme_color" not in st.session_state:
    st.session_state.theme_color = "כחול"
if "font_family" not in st.session_state:
    st.session_state.font_family = "Rubik"
if "language" not in st.session_state:
    st.session_state.language = "עברית"

# ---------------------------------------------------------
# פונקציות עזר לשליפת/עדכון הנתונים של העסק הנוכחי
# ---------------------------------------------------------
def get_biz():
    return st.session_state.businesses[st.session_state.current_business]

def get_folder():
    biz = get_biz()
    return biz["folders"][biz["current_folder"]]

# ---------------------------------------------------------
# סרגל כלים עליון
# ---------------------------------------------------------
def render_toolbar():
    st.markdown("---")
    tb_logo, tb_biz, tb_s1, tb_s2, tb_s3, tb_s4 = st.columns([1.5, 2.5, 1.5, 1.5, 1.5, 1.5])
    
    with tb_logo:
        if st.button("🚀 OptiFlow", key="tb_logo_btn", use_container_width=True):
            st.session_state.screen = "main_screen"
            st.rerun()

    with tb_biz:
        biz_list = list(st.session_state.businesses.keys())
        selected_b = st.selectbox("עסק פעיל:", biz_list, index=biz_list.index(st.session_state.current_business), label_visibility="collapsed")
        if selected_b != st.session_state.current_business:
            st.session_state.current_business = selected_b
            st.rerun()

    with tb_s1:
        with st.popover("⚙️ הגדרות"):
            st.session_state.language = st.selectbox("שפה:", ["עברית", "English", "العربية"])
            st.session_state.font_family = st.selectbox("גופן:", ["Rubik", "Segoe UI", "Arial"])
            st.session_state.theme_color = st.selectbox("צבע נושא:", ["כחול", "כהה", "ירוק"])

    with tb_s2:
        if st.button("👤 פרטי עסק", use_container_width=True):
            st.session_state.screen = "profile_screen"
            st.rerun()

    with tb_s3:
        if st.button("➕ עסק נוסף", use_container_width=True):
            st.session_state.screen = "screen_3"
            st.rerun()

    with tb_s4:
        with st.popover("📞 צור קשר"):
            st.write("**תמיכה טכנית ושירות לקוחות**")
            st.write("מייל: support@optiflow.ai")
            st.write("טלפון: 077-0000000")

    st.markdown("---")

# =========================================================
# מסך 1: התחברות
# =========================================================
if st.session_state.screen == "screen_1":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🚀 OptiFlow AI")
        st.subheader("התחברות למערכת")

        username = st.text_input("שם משתמש:")

        col_pass, col_eye = st.columns([5, 1])
        with col_pass:
            pwd_type = "text" if st.session_state.show_password else "password"
            password = st.text_input("סיסמה:", type=pwd_type)
        with col_eye:
            st.write("")
            st.write("")
            if st.button("👁️️", help="הצג/הסתר סיסמה"):
                st.session_state.show_password = not st.session_state.show_password
                st.rerun()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("התחברות", type="primary", use_container_width=True):
                if username and password:
                    st.session_state.screen = "main_screen"
                    st.rerun()
                else:
                    st.error("אנא הכנס שם משתמש וסיסמה תקינים.")

        with col_btn2:
            if st.button("שכחתי פרטים", use_container_width=True):
                st.session_state.screen = "screen_2"
                st.rerun()

        st.markdown("---")
        if st.button("לקוח חדש? הירשם כאן", use_container_width=True):
            st.session_state.screen = "screen_3"
            st.rerun()

# =========================================================
# מסך 2: שחזור סיסמה
# =========================================================
elif st.session_state.screen == "screen_2":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🔑 שחזור סיסמה")
        
        email = st.text_input("דוא''ל:")
        mobile = st.text_input("נייד:")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("שליחת קוד במייל", use_container_width=True):
                st.info(f"קוד אימות נשלח לכתובת {email}")

        with col_s2:
            with st.popover("שליחת סיסמה בנייד"):
                st.write("בחר אמצעי לקבלת הקוד:")
                if st.button("📱 SMS"):
                    st.success("קוד נשלח ב-SMS")
                if st.button("💬 WhatsApp"):
                    st.success("קוד נשלח ב-WhatsApp")
                if st.button("📞 שיחה טלפונית"):
                    st.success("שיחה קולית בדרך אליך")

        st.markdown("---")
        auth_code = st.text_input("הכנס קוד אימות שקיבלת:")
        if st.button("אמת קוד והמשך", type="primary", use_container_width=True):
            if len(auth_code) >= 2:
                st.session_state.screen = "screen_5"
                st.rerun()
            else:
                st.error("סיסמה שגויה. נסה שנית.")

# =========================================================
# מסך 3: הרשמת לקוח חדש / הוספת עסק
# =========================================================
elif st.session_state.screen == "screen_3":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("📝 הרשמה והוספת עסק")
        
        c1, c2 = st.columns(2)
        with c1:
            full_name = st.text_input("שם ושם משפחה:")
            mobile = st.text_input("נייד:")
            email = st.text_input("דוא''ל:")
        with c2:
            biz_name = st.text_input("שם העסק:")
            biz_nature = st.text_input("מהות העסק:")
            biz_address = st.text_input("כתובת העסק:")

        if st.button("אישור והמשך לבחירת תוכנית ➔", type="primary", use_container_width=True):
            if biz_name:
                # יצירת העסק במערכת הנתונים המבודדת
                st.session_state.businesses[biz_name] = {
                    "nature": biz_nature,
                    "address": biz_address,
                    "tech_data": "",
                    "folders": {
                        "תיקייה ראשית": {
                            "problem": "",
                            "params": "",
                            "chats": {"שיחה ראשית": []},
                            "current_chat": "שיחה ראשית",
                            "solutions": []
                        }
                    },
                    "current_folder": "תיקייה ראשית"
                }
                st.session_state.current_business = biz_name
                st.session_state.screen = "screen_4"
                st.rerun()
            else:
                st.error("אנא הכנס שם עסק.")

# =========================================================
# מסך 4: בחירת תוכנית
# =========================================================
elif st.session_state.screen == "screen_4":
    st.title("💳 בחירת תוכנית שירות")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.subheader("תוכנית חודשית")
        st.write("₪199 / חודש")
        if st.button("בחר חודשי מעבר לסליקה", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

    with p2:
        st.subheader("תוכנית שנתית")
        st.write("₪1,990 / שנה")
        if st.button("בחר שנתי מעבר לסליקה", type="primary", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

    with p3:
        st.subheader("תוכנית פרימיום")
        st.write("₪3,490 / שנה")
        if st.button("בחר פרימיום מעבר לסליקה", use_container_width=True):
            st.session_state.screen = "screen_5"
            st.rerun()

# =========================================================
# מסך 5: סיסמה חדשה
# =========================================================
elif st.session_state.screen == "screen_5":
    col_a, col_center, col_b = st.columns([1, 2, 1])
    with col_center:
        st.title("🔐 הגדרת פרטי התחברות חדשים")
        
        new_user = st.text_input("שם משתמש חדש:")

        c_pass, c_eye = st.columns([5, 1])
        with c_pass:
            p_type = "text" if st.session_state.show_password else "password"
            new_pass = st.text_input("סיסמה חדשה:", type=p_type)
        with c_eye:
            st.write("")
            st.write("")
            if st.button("👁️", key="eye_5"):
                st.session_state.show_password = not st.session_state.show_password
                st.rerun()

        confirm_pass = st.text_input("אימות סיסמה חדשה:", type="password")

        if st.button("אישור והמשך להתחברות", type="primary", use_container_width=True):
            if new_pass and new_pass == confirm_pass:
                st.success("הפרטים עודכנו בהצלחה!")
                st.session_state.screen = "screen_1"
                st.rerun()
            else:
                st.error("הסיסמאות אינן תואמות.")

# =========================================================
# מסך ראשי: פעיל ומחובר למסד נתונים דינמי
# =========================================================
elif st.session_state.screen == "main_screen":
    render_toolbar()

    biz = get_biz()
    folder = get_folder()

    row1_left, row1_mid, row1_right = st.columns([2, 1.5, 1.5])

    # --- צד שמאל: פתרונות והמלצות ---
    with row1_left:
        st.subheader("💡 פתרונות והמלצות")
        
        if folder["solutions"]:
            for i, sol in enumerate(folder["solutions"], 1):
                st.success(f"**פתרון {i}:** {sol}")
        else:
            st.info("לחץ על 'חישוב מחדש' או 'הצעת פתרונות נוספים' לקבלת המלצות ה-AI.")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("הצעת פתרונות נוספים", use_container_width=True):
                new_sol = f"אופטימיזציית פרמטרים חלופית עבור {biz['nature']}: הורדת עוצמה ל-70W והגברת תדר."
                folder["solutions"].append(new_sol)
                st.rerun()

        with btn_c2:
            if st.button("חישוב מחדש", type="primary", use_container_width=True):
                folder["solutions"] = [
                    f"כיול מחדש לפי הנתונים: {folder['params']}",
                    "בדיקת עדשות ומערכת הקרנת הלייזר"
                ]
                st.toast("החישוב בוצע מחדש בהצלחה!")
                st.rerun()

    # --- מרכז: מנוע הכוונה AI ---
    with row1_mid:
        st.subheader("🤖 מנוע הכוונה AI")
        st.write("שאלת הכוונה לדיוק הנתונים:")
        ai_question = st.text_area("הכוונת המערכת:", value=f"איזה סוג חומר מדויק משמש ב-{biz['nature']}?", height=100)
        ai_answer = st.text_input("תשובתך להכוונה:")
        if st.button("עדכן נתוני הכוונה", use_container_width=True):
            if ai_answer:
                folder["params"] += f" | הכוונה: {ai_answer}"
                st.success("הנתונים עודכנו בהצלחה!")
                st.rerun()

    # --- צד ימין: ניהול התיקייה והזנת נתונים ---
    with row1_right:
        # ניהול תיקיות בעסק
        folder_list = list(biz["folders"].keys())
        selected_f = st.selectbox("בחירת תיקייה:", folder_list, index=folder_list.index(biz["current_folder"]))
        if selected_f != biz["current_folder"]:
            biz["current_folder"] = selected_f
            st.rerun()

        # כפתור ליצירת תיקייה חדשה
        with st.popover("➕ פתח תיקייה חדשה"):
            new_f_name = st.text_input("שם התיקייה החדשה:")
            if st.button("צור תיקייה"):
                if new_f_name and new_f_name not in biz["folders"]:
                    biz["folders"][new_f_name] = {
                        "problem": "",
                        "params": "",
                        "chats": {"שיחה ראשית": []},
                        "current_chat": "שיחה ראשית",
                        "solutions": []
                    }
                    biz["current_folder"] = new_f_name
                    st.rerun()

        # תיאור בעיה ופרמטרים - נשמרים ישירות בתיקייה הספציפית
        new_prob = st.text_area("מהות הבעיה:", value=folder["problem"], height=80)
        if new_prob != folder["problem"]:
            folder["problem"] = new_prob

        new_param = st.text_input("פרמטרים ונתונים:", value=folder["params"])
        if new_param != folder["params"]:
            folder["params"] = new_param

        st.file_uploader("העלאת תמונות וקבצים:", accept_multiple_files=True)

    st.markdown("---")

    # --- חלק תחתון: צ'אט מופרד ומתוקן ---
    c_chat, c_info = st.columns([3, 1])
    with c_chat:
        st.subheader("💬 חלון צ'אט AI")
        
        col_ch1, col_ch2 = st.columns([3, 1])
        with col_ch1:
            chat_list = list(folder["chats"].keys())
            selected_chat = st.selectbox("שיחות שמורות בתיקייה זו:", chat_list, index=chat_list.index(folder["current_chat"]), label_visibility="collapsed")
            if selected_chat != folder["current_chat"]:
                folder["current_chat"] = selected_chat
                st.rerun()

        with col_ch2:
            with st.popover("➕ שיחה חדשה"):
                new_chat_name = st.text_input("שם השיחה:")
                if st.button("צור שיחה"):
                    if new_chat_name and new_chat_name not in folder["chats"]:
                        folder["chats"][new_chat_name] = []
                        folder["current_chat"] = new_chat_name
                        st.rerun()

        # הצגת הודעות השיחה הנוכחית בלבד
        current_messages = folder["chats"][folder["current_chat"]]
        for msg in current_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # קלט צ'אט ופנייה יציבה ל-Gemini API
        user_input = st.chat_input("שאל את העוזר החכם בנוגע לבעיה...")
        if user_input:
            # הוספת הודעת משתמש
            current_messages.append({"role": "user", "content": user_input})
            st.chat_message("user").markdown(user_input)

            if not GEMINI_API_KEY:
                st.error("אנא הכנס מפתח Gemini API בהגדרות המערכת.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("חורז פתרון..."):
                        try:
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                            headers = {"Content-Type": "application/json"}
                            
                            prompt_context = f"אתה יועץ מומחה עבור עסק בשם '{st.session_state.current_business}' העוסק ב'{biz['nature']}'. הבעיה שפורטה: {folder['problem']}. פרמטרים: {folder['params']}. ענה בקצרה ובמקצועיות ללקוח: {user_input}"
                            
                            payload = {
                                "contents": [{"parts": [{"text": prompt_context}]}]
                            }

                            res = requests.post(url, json=payload, headers=headers)
                            res_json = res.json()

                            if res.status_code == 200 and "candidates" in res_json:
                                reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                st.markdown(reply)
                                current_messages.append({"role": "assistant", "content": reply})
                            else:
                                err_msg = res_json.get("error", {}).get("message", "שגיאה בתקשורת מול ה-API")
                                st.error(f"שגיאה: {err_msg}")
                        except Exception as e:
                            st.error(f"אירעה שגיאה בחיבור: {e}")

# =========================================================
# מסך פרטי הלקוח והעסק
# =========================================================
elif st.session_state.screen == "profile_screen":
    render_toolbar()
    st.title("👤 פרטי הלקוח והעסק")

    biz = get_biz()

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.session_state.current_business = st.text_input("שם העסק:", value=st.session_state.current_business)
        biz["nature"] = st.text_input("מהות העסק:", value=biz["nature"])
        biz["address"] = st.text_input("כתובת העסק:", value=biz["address"])

    with col_p2:
        biz["tech_data"] = st.text_area("נתונים טכניים ומכשור:", value=biz["tech_data"])
        st.checkbox("סנכרון אוטומטי של הפרטים מול מנוע ה-AI", value=True)

    if st.button("💾 שמור נתונים וחזור למסך ראשי", type="primary"):
        st.success("הנתונים עודכנו בהצלחה!")
        st.session_state.screen = "main_screen"
        st.rerun()
