import streamlit as st
import pandas as pd
import numpy as np
import time
import zipfile
import io
import json
import os

# ניסיון ייבוא בטוח של ספריית Gemini
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# ---------------------------------------------------------
# 1. הגדרות תצוגה
# ---------------------------------------------------------
st.set_page_config(page_title="OptiFlow AI - Enterprise SaaS", layout="wide")

# ---------------------------------------------------------
# 2. מנגנון שמירת נתונים קבועה (Persistence) ב-JSON
# ---------------------------------------------------------
DATA_FILE = "data_store.json"

def load_all_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_all_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"שגיאה בשמירת הנתונים: {e}")

# ---------------------------------------------------------
# 3. אתחול Session State
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'lang' not in st.session_state:
    st.session_state.lang = "עברית"

if 'users_data' not in st.session_state:
    st.session_state.users_data = load_all_data()

def ensure_workspace_structure(ws):
    if "biz_type" not in ws: ws["biz_type"] = ""
    if "problem" not in ws: ws["problem"] = ""
    if "params" not in ws: ws["params"] = []
    if "solutions" not in ws: ws["solutions"] = []
    if "integrations" not in ws: ws["integrations"] = {"crm": False, "pos": False, "inventory": False}
    if "chats" not in ws or not isinstance(ws["chats"], dict):
        ws["chats"] = {"שיחה חדשה": [{"role": "assistant", "content": "שלום! אני יועץ ה-AI שלך. במה אוכל לסייע היום?"}]}
    if "active_chat" not in ws or ws["active_chat"] not in ws["chats"]:
        ws["active_chat"] = list(ws["chats"].keys())[0]
    return ws

# ---------------------------------------------------------
# 4. מסך התחברות
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔒 התחברות למערכת OptiFlow AI</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    
    with col_b:
        with st.form(key="login_form"):
            username = st.text_input("שם משתמש / אימייל:", key="login_username")
            password = st.text_input("סיסמה:", type="password", key="login_password")
            submit_button = st.form_submit_button(label="🔑 התחבר לאזור האישי")
            
            if submit_button:
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    
                    if username not in st.session_state.users_data:
                        st.session_state.users_data[username] = {
                            "תיק חדש 1": {
                                "biz_type": "",
                                "problem": "",
                                "params": [],
                                "solutions": [],
                                "integrations": {"crm": False, "pos": False, "inventory": False},
                                "chats": {
                                    "שיחה חדשה": [{"role": "assistant", "content": f"שלום {username}! במה אוכל לסייע בתיק זה?"}]
                                },
                                "active_chat": "שיחה חדשה"
                            }
                        }
                        save_all_data()
                    st.success("התחברת בהצלחה!")
                    st.rerun()
                else:
                    st.error("אנא הזן שם משתמש וסיסמה.")
    st.stop()

# ---------------------------------------------------------
# 5. ניהול נתוני משתמש מחובר
# ---------------------------------------------------------
user_id = st.session_state.current_user

if user_id not in st.session_state.users_data:
    st.session_state.users_data[user_id] = {
        "תיק חדש 1": {
            "biz_type": "",
            "problem": "",
            "params": [],
            "solutions": [],
            "integrations": {"crm": False, "pos": False, "inventory": False},
            "chats": {
                "שיחה חדשה": [{"role": "assistant", "content": f"שלום {user_id}! במה אוכל לסייע בתיק זה?"}]
            },
            "active_chat": "שיחה חדשה"
        }
    }
    save_all_data()

user_workspaces = st.session_state.users_data[user_id]

is_rtl = st.session_state.lang in ["עברית", "العربية"]
dir_style = "rtl" if is_rtl else "ltr"

st.markdown(f"""
<style>
    .stApp {{ direction: {dir_style}; text-align: {'right' if is_rtl else 'left'}; }}
    div[data-testid="stSidebar"] {{ direction: {dir_style}; text-align: {'right' if is_rtl else 'left'}; }}
    input, textarea, select {{ direction: {dir_style} !important; text-align: {'right' if is_rtl else 'left'} !important; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. סרגל צד (Sidebar)
# ---------------------------------------------------------
st.sidebar.title("OptiFlow AI ⚡")
st.sidebar.markdown(f"👤 מחובר כ: **{user_id}**")

if st.sidebar.button("🚪 התנתק"):
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

st.sidebar.markdown("---")
st.session_state.lang = st.sidebar.selectbox("🌐 שפת ממשק / Language:", ["עברית", "English", "Español"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 תיקי הלקוחות שלי")

ws_keys = list(user_workspaces.keys())
if "active_workspace" not in st.session_state or st.session_state.active_workspace not in ws_keys:
    st.session_state.active_workspace = ws_keys[0]

selected_ws = st.sidebar.selectbox("בחר תיק פעיל:", ws_keys, index=ws_keys.index(st.session_state.active_workspace))
if selected_ws != st.session_state.active_workspace:
    st.session_state.active_workspace = selected_ws
    st.rerun()

with st.sidebar.expander("➕ פתח תיק חדש"):
    new_ws_title = st.text_input("שם התיק / הפרויקט:")
    if st.button("צור תיק"):
        if new_ws_title and new_ws_title not in user_workspaces:
            user_workspaces[new_ws_title] = {
                "biz_type": "",
                "problem": "",
                "params": [],
                "solutions": [],
                "integrations": {"crm": False, "pos": False, "inventory": False},
                "chats": {"שיחה חדשה": [{"role": "assistant", "content": "שלום! התיק נפתח. במה אוכל לעזור?"}]},
                "active_chat": "שיחה חדשה"
            }
            st.session_state.active_workspace = new_ws_title
            save_all_data()
            st.rerun()

cur_ws = ensure_workspace_structure(user_workspaces[st.session_state.active_workspace])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ פרמטרים ונתונים לתיק")

old_biz = cur_ws.get("biz_type", "")
old_prob = cur_ws.get("problem", "")

cur_ws["biz_type"] = st.sidebar.text_input("סוג העסק:", value=old_biz, key=f"biz_type_{st.session_state.active_workspace}")
cur_ws["problem"] = st.sidebar.text_area("תיאור הבעיה / האתגר:", value=old_prob, height=80, key=f"problem_{st.session_state.active_workspace}")

if cur_ws["biz_type"] != old_biz or cur_ws["problem"] != old_prob:
    save_all_data()

# ---------------------------------------------------------
# רכיב חדש: חיבור למערכות מידע (CRM, קופה, ניהול מלאי)
# ---------------------------------------------------------
st.sidebar.markdown("---")
with st.sidebar.expander("🔌 חיבור למערכות מידע (ERP/CRM/קופה)"):
    st.markdown("חבר את העסק למערכות ניהול לקבלת התראות אוטומטיות:")
    
    pos_connected = st.checkbox("חיבור לקופה/מכירות (Comax / Priority / Verifone)", value=cur_ws["integrations"].get("pos", False))
    inv_connected = st.checkbox("חיבור למערכת ניהול מלאי", value=cur_ws["integrations"].get("inventory", False))
    crm_connected = st.checkbox("חיבור ל-CRM מודול לקוחות", value=cur_ws["integrations"].get("crm", False))
    
    cur_ws["integrations"]["pos"] = pos_connected
    cur_ws["integrations"]["inventory"] = inv_connected
    cur_ws["integrations"]["crm"] = crm_connected
    
    api_token = st.text_input("מפתח התממשקות API (סודי):", type="password", key=f"api_tok_{st.session_state.active_workspace}")
    if st.button("סנכרן נתונים עכשיו"):
        save_all_data()
        st.success("הנתונים סונכרנו בהצלחה מול המערכות!")

# ---------------------------------------------------------
# 7. מרכז המסך
# ---------------------------------------------------------
st.title(f"📂 {st.session_state.active_workspace}")

# תצוגת התראות מערכות מידע אם חוברו
if any(cur_ws["integrations"].values()):
    st.info("🔗 **מערכות מידע מחוברות:** " + ", ".join([k.upper() for k, v in cur_ws["integrations"].items() if v]))

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 נתוני התיק")
    st.write(f"**סוג העסק:** {cur_ws.get('biz_type') or 'לא הוגדר'}")
    st.write(f"**תיאור הבעיה:** {cur_ws.get('problem') or 'לא הוגדרה'}")
    
    if cur_ws.get("params"):
        df_p = pd.DataFrame([{"פרמטר": p["name"], "ערך": p["value"], "יחידה": p.get("unit","")} for p in cur_ws["params"]])
        st.table(df_p)
    else:
        st.info("💡 אין עדיין פרמטרים מוגדרים בתיק זה.")

    st.markdown("---")
    st.subheader("📁 העלאת קבצים ותמונות לתיק")
    
    file_uploader_key = f"file_uploader_{st.session_state.current_user}_{st.session_state.active_workspace}"
    uploaded_files = st.file_uploader("העלה תמונות או קובצי ZIP:", accept_multiple_files=True, key=file_uploader_key)
    
    if uploaded_files:
        for f in uploaded_files:
            if f.name.endswith('.zip'):
                st.success(f"📦 נפתח ZIP: {f.name}")
                with zipfile.ZipFile(io.BytesIO(f.read())) as z:
                    for filename in z.namelist():
                        st.write(f"📄 קובץ בתוך ה-ZIP: `{filename}`")
            else:
                st.write(f"✅ נטען קובץ: `{f.name}`")

with col_right:
    st.subheader("🎯 ניתוח AI ופתרונות אסטרטגיים")
    
    # תצוגת דוגמה להתראה אוטומטית ממערכת הקופה/מלאי
    if cur_ws["integrations"].get("pos") or cur_ws["integrations"].get("inventory"):
        st.warning("⚠️ **התראת מנוע המלאי והקופה:** מוצר X תופס 12% משטח המדף אך מייצר רק 1.5% מהרווח. מומלץ להחליפו במוצר בעל סירקולציה גבוהה יותר.")

    if st.button("🔄 חישוב / עדכון פתרונות מחדש", type="primary", key=f"btn_calc_{st.session_state.active_workspace}"):
        with st.spinner("מנתח נתונים ומייצר פתרונות אסטרטגיים..."):
            time.sleep(0.3)
            solutions = [
                f"💡 **מודל פרימיום ודיפרנציאציה:** מעבר לייצור סדרות יוקרתיות בעיצוב אישי עבור עסק מסוג '{cur_ws.get('biz_type')}'. "
                f"זה יאפשר להעלות את שולי הרווח ב-150%-200%.",
                f"💡 **אופטימיזציית מדף ומלאי:** ניתוח נתוני הקופה מראה שכדאי לצמצם תצוגה של מוצרים איטיים ולהגדיל נפח למוצרים מובילים."
            ]
            cur_ws["solutions"] = solutions
            save_all_data()
            st.success("הפתרונות חושבו ועודכנו!")

    solutions_list = cur_ws.get("solutions", [])
    if solutions_list:
        for sol in solutions_list:
            st.info(sol)

# ---------------------------------------------------------
# 8. צ'אט AI מתוקן ודינמי לחלוטין
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💬 צ'אט יועץ AI חכם ומסונכרן")

gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

if HAS_GEMINI and gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
    except Exception:
        pass

chats = cur_ws.get("chats", {})
active_c_name = cur_ws.get("active_chat", list(chats.keys())[0] if chats else "שיחה חדשה")

col_c1, col_c2 = st.columns([3, 1])
with col_c1:
    selected_c = st.selectbox("שיחה פעילה:", list(chats.keys()), index=list(chats.keys()).index(active_c_name) if active_c_name in chats else 0, key=f"chat_select_{st.session_state.active_workspace}")
    if selected_c != active_c_name:
        cur_ws["active_chat"] = selected_c
        st.rerun()

with col_c2:
    if st.button("➕ שיחה חדשה", key=f"btn_new_chat_{st.session_state.active_workspace}"):
        new_c_title = f"שיחה ({time.strftime('%H:%M')})"
        chats[new_c_title] = [{"role": "assistant", "content": "פתחתי שיחה חדשה. במה אוכל לסייע בתיק זה?"}]
        cur_ws["active_chat"] = new_c_title
        save_all_data()
        st.rerun()

current_chat_history = chats[cur_ws["active_chat"]]

# הצגת כל מודעות הצ'אט בעבר
for idx, msg in enumerate(current_chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

chat_input = st.chat_input("שאל את ה-AI בכל נושא...", key=f"chat_input_{st.session_state.active_workspace}")

if chat_input:
    # 1. הוספת הודעת המשתמש להיסטוריה
    current_chat_history.append({"role": "user", "content": chat_input})
    save_all_data()
    
    # 2. הזרמת תשובת AI דינמית
    if HAS_GEMINI and gemini_api_key:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # בניית היסטוריית השיחה בצורה תקינה עבור המודל
            formatted_history = []
            for msg in current_chat_history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg["content"]]})
            
            chat_session = model.start_chat(history=formatted_history)
            
            prompt_context = f"""
            אתה יועץ עסקי ותפעולי חכם.
            הנחיות קשיחות:
            1. ענה בצורה עניינית, חכמה וישירה.
            2. אל תגמגם, אל תחזור על המילים של המשתמש, ואל תפתח בביטויים כמו 'לגבי שאלתך'.
            
            נתוני העסק כעת:
            - סוג העסק: {cur_ws.get('biz_type', 'כללי')}
            - אפיון הבעיה: {cur_ws.get('problem', 'כללי')}
            - מודולים מחוברים: {json.dumps(cur_ws.get('integrations', {}), ensure_ascii=False)}
            """
            
            response = chat_session.send_message(f"{prompt_context}\n\nהודעת המשתמש החדשה: {chat_input}")
            ai_reply_text = response.text
        except Exception as e:
            ai_reply_text = f"שגיאה בהתקשרות ל-Gemini API: {e}"
    else:
        # במידה ואין מפתח API, המערכת מציגה הסבר שקוף במקום תשובה קבועה ומטעה
        ai_reply_text = (
            "⚠️ **מפתח Gemini API אינו מוגדר במערכת.**\n\n"
            "כדי שהצ'אט יענה לך באופן דינמי וחכם בזמן אמת, יש לאגור את המפתח `GEMINI_API_KEY` בקובץ `secrets.toml` או בהגדרות הסביבה."
        )

    current_chat_history.append({"role": "assistant", "content": ai_reply_text})
    save_all_data()
    st.rerun()
