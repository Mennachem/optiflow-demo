import streamlit as st
import pandas as pd
import numpy as np
import time
import zipfile
import io

# ---------------------------------------------------------
# 1. הגדרות תצוגה
# ---------------------------------------------------------
st.set_page_config(page_title="OptiFlow AI - Enterprise SaaS", layout="wide")

# ---------------------------------------------------------
# 2. אתחול Session State
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'lang' not in st.session_state:
    st.session_state.lang = "עברית"

if 'users_data' not in st.session_state:
    st.session_state.users_data = {}

# ---------------------------------------------------------
# פונקציית עזר להבטחת המבנה התקין של תיק (מניעת KeyError)
# ---------------------------------------------------------
def ensure_workspace_structure(ws):
    if "biz_type" not in ws: ws["biz_type"] = ""
    if "problem" not in ws: ws["problem"] = ""
    if "params" not in ws: ws["params"] = []
    if "solutions" not in ws: ws["solutions"] = []
    if "chats" not in ws or not isinstance(ws["chats"], dict):
        ws["chats"] = {"שיחה חדשה": [{"role": "assistant", "content": "שלום! זהו תיק חדש. הזן נתונים בסרגל הצד כדי להתחיל."}]}
    if "active_chat" not in ws or ws["active_chat"] not in ws["chats"]:
        ws["active_chat"] = list(ws["chats"].keys())[0]
    return ws

# ---------------------------------------------------------
# 3. מסך התחברות
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
                                "chats": {
                                    "שיחה חדשה": [{"role": "assistant", "content": f"שלום {username}! זהו תיק חדש וריק. אנא הזן סוג עסק ופרמטרים בסרגל הצד כדי להתחיל."}]
                                },
                                "active_chat": "שיחה חדשה"
                            }
                        }
                    st.success("התחברת בהצלחה!")
                    st.rerun()
                else:
                    st.error("אנא הזן שם משתמש וסיסמה.")
    st.stop()

# ---------------------------------------------------------
# 4. עיצוב והגנת הנתונים למשתמש מחובר
# ---------------------------------------------------------
user_id = st.session_state.current_user

if user_id not in st.session_state.users_data:
    st.session_state.users_data[user_id] = {
        "תיק חדש 1": {
            "biz_type": "",
            "problem": "",
            "params": [],
            "solutions": [],
            "chats": {
                "שיחה חדשה": [{"role": "assistant", "content": f"שלום {user_id}! זהו תיק חדש."}]
            },
            "active_chat": "שיחה חדשה"
        }
    }

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
# 5. סרגל צד (Sidebar)
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
                "chats": {"שיחה חדשה": [{"role": "assistant", "content": "שלום! התיק חדש וריק. הזן נתונים כדי להתחיל."}]},
                "active_chat": "שיחה חדשה"
            }
            st.session_state.active_workspace = new_ws_title
            st.rerun()

# וידוא מבנה תקין לתיק הנוכחי
cur_ws = ensure_workspace_structure(user_workspaces[st.session_state.active_workspace])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ פרמטרים ונתונים לתיק")

cur_ws["biz_type"] = st.sidebar.text_input("סוג העסק:", value=cur_ws.get("biz_type", ""))
cur_ws["problem"] = st.sidebar.text_area("תיאור הבעיה / האתגר:", value=cur_ws.get("problem", ""), height=80)

st.sidebar.markdown("**רשימת המשתנים בתיק:**")
to_del = None
for i, p in enumerate(cur_ws["params"]):
    c1, c2 = st.sidebar.columns([3, 1])
    with c1:
        if p.get("type") == "טקסט / בעיה":
            p["value"] = st.text_input(f"{p['name']}:", value=str(p["value"]), key=f"p_t_{i}")
        else:
            p["value"] = st.number_input(f"{p['name']} ({p['unit']}):", value=float(p["value"]), key=f"p_n_{i}")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            to_del = i

if to_del is not None:
    cur_ws["params"].pop(to_del)
    st.rerun()

with st.sidebar.expander("➕ הוסף משתנה חדש ידנית"):
    p_name = st.text_input("שם הפרמטר:")
    p_type = st.radio("סוג:", ["מספרי", "טקסט / בעיה"])
    if p_type == "מספרי":
        p_val = st.number_input("ערך:", value=1.0)
        p_unit = st.text_input('יחידת מידה:', value='ש"ח')
    else:
        p_val = st.text_input("ערך טקסטואלי:")
        p_unit = "-"
        
    if st.button("אישור הוספה"):
        if p_name:
            cur_ws["params"].append({"name": p_name, "type": p_type, "value": p_val, "unit": p_unit})
            st.rerun()

# ---------------------------------------------------------
# 6. מנוע פתרונות
# ---------------------------------------------------------
def get_dynamic_recommendations(biz_type):
    if not biz_type:
        return []
    biz = biz_type.lower()
    if "חיתוך" in biz or "פלסטיק" in biz or "לייזר" in biz or "ייצור" in biz:
        return [
            {"name": "הספק מכונת הלייזר (Watt)", "type": "מספרי", "val": 100.0, "unit": "W"},
            {"name": "זמן חיתוך ממוצע למוצר", "type": "מספרי", "val": 10.0, "unit": "דקות"},
            {"name": "עלות חומר גלם למטר", "type": "מספרי", "val": 45.0, "unit": 'ש"ח'},
            {"name": "שיעור פחת חומר", "type": "מספרי", "val": 12.0, "unit": "%"}
        ]
    else:
        return [
            {"name": "עלות ייצור יחידה", "type": "מספרי", "val": 50.0, "unit": 'ש"ח'},
            {"name": "מחיר מכירה ממוצע", "type": "מספרי", "val": 150.0, "unit": 'ש"ח'}
        ]

def generate_creative_solutions(biz_type, problem, params):
    if not biz_type and not problem:
        return ["⚠️ אנא הזן את סוג העסק ותיאור הבעיה בסרגל הצד כדי שה-AI יוכל לחשב פתרונות."]
    
    solutions = [
        f"💡 **מודל פרימיום ודיפרנציאציה (ROI גבוה):** מעבר לייצור סדרות יוקרתיות בעיצוב אישי עבור עסק מסוג '{biz_type}'. "
        f"במקום להתחרות על מחיר נמוך בשוק רווי, שילוב טכנולוגיות מתקדמות יאפשר להעלות את שולי הרווח ב-150%-200%.",
        f"💡 **פתרון B2B וערוצי הפצה חדשים:** יצירת ערכות מוכנות / מוצרי מדף עבור חנויות וסיטונאים. "
        f"פתרון זה משפר את יציבות תזרימי המזומנים ומפחית את התלות בלקוחות קצה בודדים."
    ]
    if params:
        param_summary = ", ".join([f"{p['name']}: {p['value']}" for p in params])
        solutions.append(f"📈 **אופטימיזציה תהליכית:** ניתוח המשתנים שהזנת ({param_summary}) מראה שניתן לחסוך כ-18% מבעלויות התפעול.")
    return solutions

# ---------------------------------------------------------
# 7. מרכז המסך
# ---------------------------------------------------------
st.title(f"📂 {st.session_state.active_workspace}")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 נתוני התיק")
    st.write(f"**סוג העסק:** {cur_ws.get('biz_type') or 'לא הוגדר'}")
    st.write(f"**תיאור הבעיה:** {cur_ws.get('problem') or 'לא הוגדרה'}")
    
    if cur_ws.get("params"):
        df_p = pd.DataFrame([{"פרמטר": p["name"], "ערך": p["value"], "יחידה": p["unit"]} for p in cur_ws["params"]])
        st.table(df_p)
    else:
        st.info("💡 אין עדיין פרמטרים מוגדרים בתיק זה.")

    st.markdown("---")
    st.subheader("💡 פרמטרים מומלצים להוספה:")
    
    rec_list = get_dynamic_recommendations(cur_ws.get("biz_type"))
    existing_param_names = [p["name"] for p in cur_ws.get("params", [])]
    
    if rec_list:
        for rec in rec_list:
            if rec["name"] not in existing_param_names:
                c_r1, c_r2 = st.columns([3, 1])
                c_r1.write(f"• **{rec['name']}**")
                if c_r2.button("➕ הוסף לתיק", key=f"add_rec_{rec['name']}"):
                    cur_ws["params"].append({
                        "name": rec["name"], "type": rec["type"], "value": rec["val"], "unit": rec["unit"]
                    })
                    st.rerun()
    else:
        st.caption("הזן סוג עסק בסרגל הצד לקבלת המלצות מותאמות.")

    st.markdown("---")
    st.subheader("📁 העלאת קבצים ותיקיות ZIP")
    uploaded_files = st.file_uploader("העלה תמונות או קובצי ZIP:", accept_multiple_files=True)
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
    st.subheader("🎯 ניתוח AI ופתרונות יצירתיים")
    if st.button("🔄 חישוב / עדכון פתרונות מחדש", type="primary"):
        with st.spinner("מנתח נתונים ומייצר פתרונות אסטרטגיים..."):
            time.sleep(0.3)
            cur_ws["solutions"] = generate_creative_solutions(cur_ws.get("biz_type"), cur_ws.get("problem"), cur_ws.get("params"))
            st.success("הפתרונות חושבו ועודכנו!")

    # גישה בטוחה למפתח solutions ללא KeyError
    solutions_list = cur_ws.get("solutions", [])
    if solutions_list:
        for sol in solutions_list:
            st.info(sol)
    else:
        st.warning("⚠️ בתיק זה עדיין לא חושבו פתרונות. הזן נתונים ולחץ על 'חישוב / עדכון פתרונות מחדש'.")

# ---------------------------------------------------------
# 8. צ'אט
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💬 צ'אט יועץ AI מסונכרן")

chats = cur_ws.get("chats", {})
active_c_name = cur_ws.get("active_chat", list(chats.keys())[0] if chats else "שיחה חדשה")

col_c1, col_c2 = st.columns([3, 1])
with col_c1:
    selected_c = st.selectbox("שיחה פעילה:", list(chats.keys()), index=list(chats.keys()).index(active_c_name) if active_c_name in chats else 0)
    if selected_c != active_c_name:
        cur_ws["active_chat"] = selected_c
        st.rerun()

with col_c2:
    if st.button("➕ שיחה חדשה"):
        new_c_title = f"שיחה ({time.strftime('%H:%M')})"
        chats[new_c_title] = [{"role": "assistant", "content": "פתחתי שיחה חדשה. במה אוכל לסייע בתיק זה?"}]
        cur_ws["active_chat"] = new_c_title
        st.rerun()

current_chat_history = chats[cur_ws["active_chat"]]

for idx, msg in enumerate(current_chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image" in msg:
            st.image(msg["image"], caption="הדמיה ויזואלית")
        if "suggested_param" in msg:
            sp = msg["suggested_param"]
            if st.button(f"➕ הוסף פרמטר '{sp['name']}' לתיק", key=f"chat_add_p_{idx}"):
                cur_ws["params"].append(sp)
                st.success(f"הפרמטר נוסף!")
                st.rerun()

chat_input = st.chat_input("שאל את ה-AI...")

if chat_input:
    current_chat_history.append({"role": "user", "content": chat_input})
    q = chat_input.lower()
    
    reply = {"role": "assistant"}
    if "תמונה" in q or "הדמיה" in q or "שרטוט" in q:
        reply["content"] = f"הנה הדמיה ויזואלית מוצעת עבור העסק '{cur_ws.get('biz_type') or 'שלך'}':"
        reply["image"] = "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600"
    elif "מחיר" in q or "עלות" in q or "רווח" in q:
        reply["content"] = "בתמחור מוצרים מסוג זה, מומלץ לחשב את עלות חומר הגלם הישיר."
        reply["suggested_param"] = {"name": "עלות חומר גלם ללוח", "type": "מספרי", "value": 120.0, "unit": 'ש"ח'}
    else:
        reply["content"] = f"לגבי שאלתך בנושא '{chat_input}': בהתחשב בסוג העסק ({cur_ws.get('biz_type') or 'שטרם הוגדר'}), מומלץ לבחון ערוצי מכירה נוספים ואופטימיזציית תהליכים."

    current_chat_history.append(reply)
    st.rerun()

