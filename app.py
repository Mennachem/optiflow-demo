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

# מאגר תיקים נפרד לכל משתמש
if 'users_data' not in st.session_state:
    st.session_state.users_data = {
        "מנדי": {
            "תיק 1 - חיתוך פלסטיק": {
                "biz_type": "חיתוך פלסטיק בלייזר",
                "problem": "עיקר העסק בנוי על שלטים לילדות. יש הרבה מתחרים ואני צריך לחדש דברים ייחודיים.",
                "params": [
                    {"name": "כמות חנויות שעובדות איתי", "type": "מספרי", "value": 60.0, "unit": "חנויות"},
                    {"name": "כמות הזמנות ממוצע ליום", "type": "מספרי", "value": 8.0, "unit": "הזמנות"},
                    {"name": "עלות שלטים", "type": "טקסט / בעיה", "value": "בין 150 ל 300", "unit": "שקלים"}
                ],
                "chats": {
                    "שיחה ראשונית": [
                        {"role": "assistant", "content": "שלום מנדי! ניתחתי את הנתונים של עסק חיתוך הפלסטיק. איך אוכל לסייע בפיתוח המוצרים הייחודיים?"}
                    ]
                },
                "active_chat": "שיחה ראשונית"
            }
        }
    }

# ---------------------------------------------------------
# 3. מסך התחברות עם טופס מובנה (פתרון לזיכרון סיסמאות)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔒 התחברות למערכת OptiFlow AI</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    
    with col_b:
        # שימוש ב-st.form מאפשר לדפדפן להשלים שם משתמש וסיסמה יחד
        with st.form(key="login_form"):
            username = st.text_input("שם משתמש / אימייל:", key="login_username")
            password = st.text_input("סיסמה:", type="password", key="login_password")
            submit_button = st.form_submit_button(label="🔑 התחבר לאזור האישי")
            
            if submit_button:
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    
                    # פתיחת תיק ריק ראשוני למשתמש חדש אם הוא לא קיים במערכת
                    if username not in st.session_state.users_data:
                        st.session_state.users_data[username] = {
                            "תיק חדש 1": {
                                "biz_type": "",
                                "problem": "",
                                "params": [],
                                "chats": {
                                    "שיחה חדשה": [{"role": "assistant", "content": f"שלום {username}! זהו התיק החדש שלך. אנא הזן את סוג העסק והבעיה בסרגל הצד כדי שנוכל להתחיל."}]
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
# 4. עיצוב ושפה
# ---------------------------------------------------------
user_id = st.session_state.current_user
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
# 5. סרגל צד (Sidebar) - אזור אישי של המשתמש בלבד
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
                "chats": {"שיחה חדשה": [{"role": "assistant", "content": "שלום! במה אוכל לעזור בתיק זה?"}]},
                "active_chat": "שיחה חדשה"
            }
            st.session_state.active_workspace = new_ws_title
            st.rerun()

cur_ws = user_workspaces[st.session_state.active_workspace]

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ פרמטרים ונתונים לתיק")

cur_ws["biz_type"] = st.sidebar.text_input("סוג העסק:", value=cur_ws["biz_type"])
cur_ws["problem"] = st.sidebar.text_area("תיאור הבעיה / האתגר:", value=cur_ws["problem"], height=80)

# עריכת הפרמטרים
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
# 6. מנוע המלצות דינמי לפי סוג העסק (סעיף 3)
# ---------------------------------------------------------
def get_dynamic_recommendations(biz_type):
    biz_type_lower = biz_type.lower()
    if "חיתוך" in biz_type_lower or "פלסטיק" in biz_type_lower or "ייצור" in biz_type_lower or "בלייזר" in biz_type_lower:
        return [
            {"name": "סוג מכונת הלייזר / עוצמה (Watt)", "type": "טקסט / בעיה", "val": "100W CO2", "unit": "-"},
            {"name": "זמן חיתוך ממוצע למוצר", "type": "מספרי", "val": 12.0, "unit": "דקות"},
            {"name": "עלות חומר גלם למטר", "type": "מספרי", "val": 45.0, "unit": 'ש"ח'},
            {"name": "שיעור פחת / שאריות חומר", "type": "מספרי", "val": 15.0, "unit": "%"}
        ]
    elif "אוכל" in biz_type_lower or "מסעדה" in biz_type_lower or "קפה" in biz_type_lower:
        return [
            {"name": "עלות מנה ממוצעת (Food Cost)", "type": "מספרי", "val": 25.0, "unit": 'ש"ח'},
            {"name": "תפוסת שולחנות בשעות שיא", "type": "מספרי", "val": 85.0, "unit": "%"},
            {"name": "זמן הכנת מנה ממוצע", "type": "מספרי", "val": 10.0, "unit": "דקות"}
        ]
    else:
        return [
            {"name": "עלות ייצור למוצר", "type": "מספרי", "val": 50.0, "unit": 'ש"ח'},
            {"name": "זמן עבודה מושקע במוצר", "type": "מספרי", "val": 2.0, "unit": "שעות"},
            {"name": "מחיר מכירה מומלץ", "type": "מספרי", "val": 150.0, "unit": 'ש"ח'}
        ]

# ---------------------------------------------------------
# 7. הגוף המרכזי
# ---------------------------------------------------------
st.title(f"📂 {st.session_state.active_workspace}")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 נתוני התיק")
    st.write(f"**סוג העסק:** {cur_ws['biz_type'] if cur_ws['biz_type'] else 'לא הוגדר'}")
    st.write(f"**תיאור הבעיה:** {cur_ws['problem'] if cur_ws['problem'] else 'לא הוגדרה'}")
    
    if cur_ws["params"]:
        df_p = pd.DataFrame([{"פרמטר": p["name"], "ערך": p["value"], "יחידה": p["unit"]} for p in cur_ws["params"]])
        st.table(df_p)

    # פרמטרים מומלצים דינמיים לפי סוג העסק
    st.markdown("---")
    st.subheader("💡 פרמטרים מומלצים להוספה (משתנה לפי סוג העסק):")
    
    rec_list = get_dynamic_recommendations(cur_ws["biz_type"])
    existing_param_names = [p["name"] for p in cur_ws["params"]]
    
    for rec in rec_list:
        if rec["name"] not in existing_param_names:
            c_r1, c_r2 = st.columns([3, 1])
            c_r1.write(f"• **{rec['name']}**")
            if c_r2.button("➕ הוסף לתיק", key=f"add_rec_{rec['name']}"):
                cur_ws["params"].append({
                    "name": rec["name"],
                    "type": rec["type"],
                    "value": rec["val"],
                    "unit": rec["unit"]
                })
                st.rerun()

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
    st.subheader("🎯 ניתוח AI ופתרונות")
    if st.button("🔄 לחץ לחישוב מחדש של הפתרונות", type="primary"):
        with st.spinner("מחשב ומנתח נתונים..."):
            time.sleep(0.5)
            st.success("הפתרונות עודכנו!")

    st.info("💡 **פתרון מומלץ 1:** מעבר לשלטי פרימיום תלת-ממדיים בשילוב עץ ואקריליק. מאפשר להעלות מחיר מ-150 ש\"ח ל-350 ש\"ח.")
    st.info("💡 **פתרון מומלץ 2:** ערכות DIY להרכבה עצמית לילדים - מכירת חלקי פלסטיק חתוכים עם צבעים לחנויות יצירה.")

# ---------------------------------------------------------
# 8. צ'אט חכם, אינטראקטיבי ומסונכרן (סעיף 4)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💬 צ'אט יועץ AI מסונכרן")

chats = cur_ws["chats"]
active_c_name = cur_ws.get("active_chat", list(chats.keys())[0])

col_c1, col_c2 = st.columns([3, 1])
with col_c1:
    selected_c = st.selectbox("שיחה פעילה:", list(chats.keys()), index=list(chats.keys()).index(active_c_name) if active_c_name in chats else 0)
    if selected_c != active_c_name:
        cur_ws["active_chat"] = selected_c
        st.rerun()

with col_c2:
    if st.button("➕ שיחה חדשה"):
        new_c_title = f"שיחה ({time.strftime('%H:%M')})"
        chats[new_c_title] = [{"role": "assistant", "content": "פתחתי שיחה חדשה. במה נתמקד?"}]
        cur_ws["active_chat"] = new_c_title
        st.rerun()

current_chat_history = chats[cur_ws["active_chat"]]

# הצגת כל הודעות הצ'אט
for idx, msg in enumerate(current_chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        # אם יש תמונה שה-AI החליט להציג
        if "image" in msg:
            st.image(msg["image"], caption="הדמיה ויזואלית לפתרון")
            
        # אם ה-AI הציע להוסיף פרמטר בלחיצת כפתור
        if "suggested_param" in msg:
            sp = msg["suggested_param"]
            if st.button(f"➕ לחץ כאן להוספת הפרמטר '{sp['name']}' לתיק", key=f"chat_add_p_{idx}"):
                cur_ws["params"].append(sp)
                st.success(f"הפרמטר '{sp['name']}' הנוסף בהצלחה לרשימת המשתנים!")
                st.rerun()

chat_input = st.chat_input("שאל את ה-AI, בקש תמונה או התייעץ...")

if chat_input:
    current_chat_history.append({"role": "user", "content": chat_input})
    
    # ניתוח בקשת המשתמש
    user_txt = chat_input.lower()
    
    new_reply = {}
    new_reply["role"] = "assistant"
    
    if "תמונה" in user_txt or "שרטוט" in user_txt or "איך זה נראה" in user_txt or "סקיצה" in user_txt:
        new_reply["content"] = "הנה הדמיה ויזואלית המדגימה את השלט התלת-ממדי המשולב עץ ואקריליק:"
        # תמונת הדגמה של לייזר/עץ
        new_reply["image"] = "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600"
        
    elif "מכונה" in user_txt or "ציוד" in user_txt or "לייזר" in user_txt:
        new_reply["content"] = "כדי לתת חישוב מדויק של קצב הייצור, אני ממליץ להוסיף את הפרמטר 'הספק מכונת הלייזר (Watt)' לנתוני התיק."
        new_reply["suggested_param"] = {"name": "הספק מכונת הלייזר (Watt)", "type": "מספרי", "value": 100.0, "unit": "Watt"}
        
    elif "עלות" in user_txt or "מחיר" in user_txt or "חומר" in user_txt:
        new_reply["content"] = "כדי לבדוק את כדאיות הפתרון, כדאי שנגדיר את הפרמטר 'עלות חומר גלם ללוח'."
        new_reply["suggested_param"] = {"name": "עלות חומר גלם ללוח", "type": "מספרי", "value": 120.0, "unit": 'ש"ח'}
        
    else:
        new_reply["content"] = f"ניתחתי את בקשתך בנושא '{chat_input}'. בהתחשב בנתוני התיק כעת, נוכל לבחון התרחבות למכירת מוצרים מותאמים אישית לאירועים. תרצה שנבדוק פרמטרים של תמחור סיטונאי?"

    current_chat_history.append(new_reply)
    st.rerun()

