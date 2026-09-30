import streamlit as st
import requests
import json
import os

# ---------------------------------------------------------
# 1. תצורת עמוד ועיצוב CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="OptiFlow AI - פלטפורמה חכמה",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* עיצוב סרגל עליון נקי */
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
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. אתחול Session State
# ---------------------------------------------------------
if "screen" not in st.session_state:
    st.session_state.screen = "main_screen"

# שליפת מפתח API מ-Secrets או משתני סביבה
default_api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = default_api_key

# הגדרות אתר כלליות
if "site_settings" not in st.session_state:
    st.session_state.site_settings = {
        "site_name": "OptiFlow AI",
        "language": "עברית",
        "theme": "בהיר",
        "notifications": True,
        "default_model": "gemini-1.5-flash"
    }

# בנק שאלות הכוונה מתמשך למנוע ההכוונה
GUIDANCE_QUESTIONS_POOL = [
    "מהו עובי החומר (ב-מ\"מ) שבו מתרחשת הבעיה?",
    "מהי טמפרטורת הסביבה או טמפרטורת העבודה של המכונה?",
    "מהי תדירות הטיפולים/התחזוקה השוטפת שמבוצעת במערכת?",
    "מהו לחץ האוויר/הגז (ב-Bar) המוזרק בזמן העבודה?",
    "האם הבעיה מופיעה באופן רציף או רק בתחילת העבודה?",
    "מהו הדגם והמספר הסידורי של עדשת/ראש העבודה?"
]

if "guidance_idx" not in st.session_state:
    st.session_state.guidance_idx = 0

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
                    "ai_question": GUIDANCE_QUESTIONS_POOL[0],
                    "chats": {"שיחה ראשית": []},
                    "current_chat": "שיחה ראשית",
                    "solutions": [
                        "כיול מחדש לפי הנתונים: פלסטיק אקרילי",
                        "בדיקת עדשות ומערכת הקרנת הלייזר"
                    ]
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
# 3. סרגל כלים עליון עם תפריט הגדרות אתר מורחב
# ---------------------------------------------------------
def render_toolbar():
    tb_logo, tb_biz, tb_nav1, tb_nav2, tb_nav3, tb_nav4 = st.columns([2, 2.5, 1.5, 1.5, 1.5, 1.5])
    
    with tb_logo:
        st.markdown(f"<h3 style='margin:0; color:#1f2937; text-align:right;'>🚀 {st.session_state.site_settings['site_name']}</h3>", unsafe_allow_html=True)

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

    # --- הגדרות האתר מורחבות ---
    with tb_nav3:
        with st.popover("⚙️ הגדרות האתר"):
            st.markdown("### ⚙️ הגדרות האתר והמערכת")
            
            st.session_state.site_settings["site_name"] = st.text_input(
                "שם המערכת / האתר:", 
                value=st.session_state.site_settings["site_name"]
            )
            
            st.session_state.site_settings["language"] = st.selectbox(
                "שפת ממשק:", 
                ["עברית", "English", "العربية"], 
                index=0
            )
            
            st.session_state.site_settings["default_model"] = st.selectbox(
                "מודל AI ברירת מחדל:", 
                ["gemini-1.5-flash", "gemini-1.5-pro"]
            )
            
            st.session_state.site_settings["notifications"] = st.checkbox(
                "התראות מערכת פעילות", 
                value=st.session_state.site_settings["notifications"]
            )
            
            st.markdown("---")
            st.markdown("**מפתח חיבור Gemini API:**")
            key_in = st.text_input(
                "הכנס API Key:", 
                value=st.session_state.api_key_input, 
                type="password",
                help="הכנס מפתח תקין מ-Google AI Studio"
            )
            if key_in != st.session_state.api_key_input:
                st.session_state.api_key_input = key_in.strip()
                st.success("מפתח ה-API עודכן בהצלחה!")

    with tb_nav4:
        with st.popover("📞 צור קשר"):
            st.write("**תמיכה טכנית**")
            st.write("מייל: support@optiflow.ai")

    st.markdown("<hr style='margin-top:5px; margin-bottom:20px;'>", unsafe_allow_html=True)

# =========================================================
# מסך ראשי
# =========================================================
if st.session_state.screen == "main_screen":
    render_toolbar()

    biz = get_biz()
    folder = get_folder()

    row1_left, row1_mid, row1_right = st.columns([2, 1.8, 1.8])

    # --- 1. פתרונות והמלצות (דינמי ללא חזרתיות) ---
    with row1_left:
        st.subheader("💡 פתרונות והמלצות")
        
        if folder["solutions"]:
            for i, sol in enumerate(folder["solutions"], 1):
                st.success(f"**פתרון {i}:** {sol}")
        else:
            st.info("אין פתרונות מוצגים. לחץ על 'הצעת פתרונות נוספים'.")

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("הצעת פתרונות נוספים", use_container_width=True):
                # הפקת פתרונות חדשים מגוונים לפי מספר הפעמים
                num_existing = len(folder["solutions"])
                new_solutions_pool = [
                    f"הפחתת עוצמת הלייזר ב-15% והגברת מהירות ההזנה לסירוגין.",
                    f"שימוש בגז עזר (חמצן/חנקן) בלחץ מבוקר למניעת התחממות יתר.",
                    f"בדיקה והחלפה של עדשת הריכוז בראש החיתוך.",
                    f"הוספת פעימות קירור קצרות (Pulse Mode) בזמן החיתוך.",
                    f"שינוי זווית הקרן והתאמת המרחק הבוקאלי מהחומר."
                ]
                
                # בחירת פתרון שלא הופיע עדיין
                next_sol = new_solutions_pool[num_existing % len(new_solutions_pool)]
                folder["solutions"].append(next_sol)
                st.rerun()

        with btn_c2:
            if st.button("חישוב מחדש", type="primary", use_container_width=True):
                params_summary = ", ".join([f"{p['name']}: {p['value']}" for p in folder['structured_params']])
                folder["solutions"] = [
                    f"כיול מודל עבודה מחדש לפי הפרמטרים: {params_summary}",
                    "אופטימיזציה כוללת של פרמטרי הלייזר והקירור"
                ]
                st.toast("החישוב בוצע מחדש!")
                st.rerun()

    # --- 2. מנוע הכוונה AI (מחשב שאלה חדשה אחרי כל עדכון) ---
    with row1_mid:
        st.subheader("🤖 AI מנוע הכוונה")
        st.write("**שאלת הכוונה לדיוק הנתונים:**")
        
        st.info(folder["ai_question"])
        
        param_name_input = st.text_input("שם הפרמטר שיוגדר:", value="נתון הכוונה")
        param_val_input = st.text_input("תשובתך להכוונה:")

        if st.button("עדכן נתוני הכוונה", use_container_width=True, type="primary"):
            if param_val_input:
                # א. שמירת הנתון כפרמטר חדש במערכת
                folder["structured_params"].append({
                    "name": param_name_input if param_name_input else "הכוונה",
                    "type": "טקסט",
                    "value": param_val_input
                })
                
                # ב. קידום תור השאלות וחישוב שאלת הכוונה הבאה
                st.session_state.guidance_idx = (st.session_state.guidance_idx + 1) % len(GUIDANCE_QUESTIONS_POOL)
                folder["ai_question"] = GUIDANCE_QUESTIONS_POOL[st.session_state.guidance_idx]
                
                st.success("הנתון עודכן! חושבה שאלת הכוונה חדשה.")
                st.rerun()
            else:
                st.warning("אנא הכנס תשובה לפני העדכון.")

    # --- 3. ניהול פרמטרים מובנים ---
    with row1_right:
        folder_list = list(biz["folders"].keys())
        selected_f = st.selectbox("בחירת תיקייה:", folder_list, index=folder_list.index(biz["current_folder"]))
        if selected_f != biz["current_folder"]:
            biz["current_folder"] = selected_f
            st.rerun()

        folder["problem"] = st.text_area("מהות הבעיה:", value=folder["problem"], height=70)

        st.write("**פרמטרים ונתונים מובנים:**")
        
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

        with st.popover("➕ הוסף פרמטר חדש"):
            p_type = st.selectbox("סוג הפרמטר:", ["טקסט", "מספר", "משתנה"])
            p_n = st.text_input("שם הפרמטר:")
            p_v = st.text_input("ערך הפרמטר:")
            p_u = st.text_input("יחידת מידה (אופציונלי):") if p_type == "מספר" else ""
            
            if st.button("אישור הוספה"):
                if p_n and p_v:
                    folder["structured_params"].append({"name": p_n, "type": p_type, "value": p_v, "unit": p_u})
                    st.rerun()

    st.markdown("---")

    # --- 4. צ'אט AI מתוקן ויציב ---
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

            api_key = st.session_state.api_key_input.strip()
            
            if not api_key:
                err_msg = "⚠️️ לא הוגדר מפתח API תקין. אנא היכנס ל-'⚙️ הגדרות האתר' בסרגל העליון והכנס מפתח Gemini API."
                st.chat_message("assistant").error(err_msg)
                current_messages.append({"role": "assistant", "content": err_msg})
            else:
                with st.chat_message("assistant"):
                    with st.spinner("מעבד תשובה..."):
                        try:
                            model_name = st.session_state.site_settings.get("default_model", "gemini-1.5-flash")
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                            headers = {"Content-Type": "application/json"}
                            
                            p_summary = ", ".join([f"{p['name']}: {p['value']}" for p in folder['structured_params']])
                            prompt_context = f"עסק: {st.session_state.current_business}, תחום: {biz['nature']}. בעיה: {folder['problem']}. פרמטרים: {p_summary}. ענה בקצרה: {user_input}"
                            
                            payload = {"contents": [{"parts": [{"text": prompt_context}]}]}

                            res = requests.post(url, json=payload, headers=headers, timeout=15)
                            res_json = res.json()

                            if res.status_code == 200 and "candidates" in res_json:
                                reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
                                st.markdown(reply)
                                current_messages.append({"role": "assistant", "content": reply})
                            else:
                                api_err = res_json.get("error", {}).get("message", "מפתח API לא תקין או שגיאת תקשורת.")
                                err_text = f"שגיאת API: {api_err}. אנא בדוק את המפתח ב-'⚙️ הגדרות האתר'."
                                st.error(err_text)
                                current_messages.append({"role": "assistant", "content": err_text})
                        except Exception as e:
                            err_text = f"שגיאה בהתקשרות: {e}"
                            st.error(err_text)
                            current_messages.append({"role": "assistant", "content": err_text})

elif st.session_state.screen == "profile_screen":
    render_toolbar()
    st.title("👤 פרטי הלקוח והעסק")
    biz = get_biz()
    biz["nature"] = st.text_input("מהות העסק:", value=biz["nature"])
    biz["address"] = st.text_input("כתובת העסק:", value=biz["address"])
    biz["tech_data"] = st.text_area("מידע טכני/ציוד:", value=biz["tech_data"])
    
    if st.button("שמור וחזור למסך ראשי", type="primary"):
        st.session_state.screen = "main_screen"
        st.rerun()
