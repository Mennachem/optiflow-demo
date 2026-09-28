import streamlit as st
import pandas as pd
import numpy as np
import time

# ---------------------------------------------------------
# 1. הגדרות תצוגה ותמיכה בכיוון ימין-לשמאל (RTL)
# ---------------------------------------------------------
st.set_page_config(page_title="OptiFlow AI - SaaS Enterprise", layout="wide")

st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. אתחול Session State (אזור אישי, תיקיות וצ'אט)
# ---------------------------------------------------------
if 'workspaces' not in st.session_state:
    st.session_state.workspaces = {
        "תיק ברירת מחדל": {
            "biz_type": "חנות קמעונאית / מסעדה / מפעל",
            "problem": "יש עבודה ותנועת לקוחות, אך בסוף החודש לא נשאר רווח נקי.",
            "params": [
                {"name": "שטח עסקי", "type": "מספרי", "value": 120.0, "unit": "sqm"},
                {"name": "אחוז רווח גולמי", "type": "מספרי", "value": 15.0, "unit": "%"},
                {"name": "הערה לגבי הוצאות", "type": "טקסט / בעיה", "value": "עלויות חומרי הגלם והחשמל עלו ב-20%", "unit": "-"}
            ],
            "chats": {
                "שיחה ראשונית - אבחון": [
                    {"role": "assistant", "content": "שלום! אני כאן כדי לעזור לך לאבחן בעיות ולשפר רווחיות ותפעול. במה נתחיל?"}
                ]
            },
            "active_chat": "שיחה ראשונית - אבחון"
        }
    }

if 'active_workspace' not in st.session_state:
    st.session_state.active_workspace = "תיק ברירת מחדל"

# גישה קלה לתיק הנוכחי
ws_name = st.session_state.active_workspace
current_ws = st.session_state.workspaces[ws_name]

# ---------------------------------------------------------
# 3. סרגל הצד (Sidebar) - אזור אישי ותיקיות לקוח
# ---------------------------------------------------------
st.sidebar.title("OptiFlow AI ⚡")
st.sidebar.markdown("### 👤 אזור אישי & ניהול תיקים")

# מעבר/יצירת תיקיות לקוחות
existing_workspaces = list(st.session_state.workspaces.keys())
selected_ws = st.sidebar.selectbox("📂 בחר תיק לקוח / פרויקט:", existing_workspaces, index=existing_workspaces.index(ws_name))

if selected_ws != ws_name:
    st.session_state.active_workspace = selected_ws
    st.rerun()

with st.sidebar.expander("➕ פתח תיק לקוח / פרויקט חדש"):
    new_ws_name = st.text_input("שם הלקוח / התיק החדש:")
    if st.button("צור תיק חדש"):
        if new_ws_name and new_ws_name not in st.session_state.workspaces:
            st.session_state.workspaces[new_ws_name] = {
                "biz_type": "עסק חדש",
                "problem": "תאר כאן את אתגרי העסק...",
                "params": [],
                "chats": {"שיחה חדשה": [{"role": "assistant", "content": "שלום! פתחת שיחה בתיק חדש. איך אוכל לסייע?"}]},
                "active_chat": "שיחה חדשה"
            }
            st.session_state.active_workspace = new_ws_name
            st.success(f"תיק '{new_ws_name}' נוצר בהצלחה!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ פרטי התיק והפרמטרים")

current_ws["biz_type"] = st.sidebar.text_input("מה סוג העסק?", value=current_ws["biz_type"])
current_ws["problem"] = st.sidebar.text_area("תאר את הבעיה המרכזית:", value=current_ws["problem"], height=100)

st.sidebar.markdown("---")
st.sidebar.subheader("📏 ניהול פרמטרים ובעיות")

# הוספת פרמטר חדש (עם יחידת מידה פתוחה לחלוטין)
with st.sidebar.expander("➕ הוסף פרמטר / בעיה"):
    p_name = st.text_input("שם הפרמטר / הרכיב:")
    p_type = st.radio("סוג הנתון:", ["מספרי", "טקסט / בעיה"])
    
    if p_type == "מספרי":
        p_val = st.number_input("ערך מספרי:", value=10.0, step=1.0)
        unit_type = st.selectbox("בחר יחידת מידה:", ["sqm", "%", "קמ\"ש", "שעות", "דקות", "שקלים", "דולרים", "יחידות", "✍️ יחידה מותאמת אישית (טקסט חופשי)"])
        if unit_type == "✍️ יחידה מותאמת אישית (טקסט חופשי)":
            p_unit = st.text_input("רשום יחידת מידה חופשית (כגון: פניות/יום, % תשואה וכו'):", value="יחידה")
        else:
            p_unit = unit_type
    else:
        p_val = st.text_area("פירוט הבעיה / הנתון:")
        p_unit = "-"

    if st.button("➕ אישור הוספה"):
        if p_name:
            current_ws["params"].append({"name": p_name, "type": p_type, "value": p_val, "unit": p_unit})
            st.rerun()

# עריכה ומחיקת פרמטרים
to_del_p = None
for i, p in enumerate(current_ws["params"]):
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        if p.get("type") == "טקסט / בעיה":
            p["value"] = st.text_input(f"📌 {p['name']}:", value=str(p["value"]), key=f"p_txt_{ws_name}_{i}")
        else:
            p["value"] = st.number_input(f"🔢 {p['name']} ({p['unit']}):", value=float(p["value"]), key=f"p_num_{ws_name}_{i}")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_p_{ws_name}_{i}"):
            to_del_p = i

if to_del_p is not None:
    current_ws["params"].pop(to_del_p)
    st.rerun()

# ---------------------------------------------------------
# 4. מנוע ניתוח AI דינמי
# ---------------------------------------------------------
def run_ai_engine(biz, prob, params):
    all_text = (prob + " " + " ".join([f"{p['name']} {p['value']} {p['unit']}" for p in params])).lower()
    
    is_profit = any(w in all_text for w in ["רווח", "שקלים", "%", "מחיר", "עלות", "הפסד", "תשואה", "margin"])
    is_speed = any(w in all_text for w in ["מהירות", "זמן", "קמ\"ש", "איטי", "שעות", "דקות", "תור", "speed"])
    
    analysis = []
    solutions = []
    
    if is_profit and not is_speed:
        analysis.append(f"מניתוח הפרמטרים בתיק **{ws_name}** ({biz}), זוהה מיקוד בפיננסים ומרווחי רווח.")
        solutions.append("**אופטימיזציית מרווחים:** בחינת תמחור ועלויות שוליות לפי יחידות המידה שהוגדרו.")
        solutions.append("**הפחתת דליפות משאבים:** ניתוח הוצאות תפעוליות והגדלת ערך עסקה ממוצע.")
    elif is_speed:
        analysis.append(f"מניתוח הנתונים בתיק **{ws_name}** זוהו מדדי זמנים/מהירות וצווארי בקבוק תפעוליים.")
        solutions.append("**קיצור זמני תגובה וקצב עבודה:** שיפור תהליכים וקיצור משכי טיפול.")
        solutions.append("**אוטומציה של שלבי עבודה:** צמצום פעולות ידניות שמאיטות את הקצב.")
    else:
        analysis.append(f"מניתוח כולל בתיק **{ws_name}** ({biz}), הוכנה תוכנית אופטימיזציה מותאמת.")
        solutions.append("**ייעול שרשרת הפעילות:** איזון בין משאבים לתפוקה בפועל.")
        solutions.append("**בניית מודל בקרה דינמי:** מעקב רציף אחר השינויים.")

    return "\n\n".join(analysis), solutions

# ---------------------------------------------------------
# 5. הגוף המרכזי של האפליקציה
# ---------------------------------------------------------
st.title(f"OptiFlow AI - {ws_name} 📂")

col_main1, col_main2 = st.columns([1, 1])

with col_main1:
    st.subheader("📋 נתוני התיק והפרמטרים שנרשמו")
    st.write(f"**סוג העסק:** {current_ws['biz_type']}")
    st.write(f"**תיאור הבעיה:** {current_ws['problem']}")
    
    formatted_p = [{"רכיב / פרמטר": p["name"], "סוג": p.get("type","מספרי"), "ערך": p["value"], "יחידת מידה": p["unit"]} for p in current_ws["params"]]
    st.table(pd.DataFrame(formatted_p))

    st.markdown("---")
    st.subheader("📸 העלאת קבצים / מסמכים לתיק זה")
    files = st.file_uploader("העלה קובץ לניתוח:", type=["jpg", "png", "mp4", "pdf", "csv", "xlsx"], key=f"u_{ws_name}")
    if files:
        st.success("✅ הקובץ נשמר בתיק זה ושולב במודל הניתוח.")

with col_main2:
    st.subheader("💡 אבחון AI ופתרונות אופטימליים")
    ai_summary, ai_sols = run_ai_engine(current_ws['biz_type'], current_ws['problem'], current_ws['params'])
    
    st.info(ai_summary)
    st.markdown("#### 🎯 פתרונות מומלצים:")
    for idx, s in enumerate(ai_sols, 1):
        st.write(f"{idx}. {s}")

# ---------------------------------------------------------
# 6. צ'אט מעקב, סגירת נושאים ושמירת שיחות
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💬 צ'אט יועץ AI - ניהול נושאים ושיחות")

# ניהול שיחות בתיק הנוכחי
chats_dict = current_ws["chats"]
active_chat_key = current_ws.get("active_chat", list(chats_dict.keys())[0])

c_col1, c_col2, c_col3 = st.columns([2, 1, 1])

with c_col1:
    selected_chat = st.selectbox("💬 בחר שיחה שמורה בתיק זה:", list(chats_dict.keys()), index=list(chats_dict.keys()).index(active_chat_key) if active_chat_key in chats_dict else 0)
    if selected_chat != active_chat_key:
        current_ws["active_chat"] = selected_chat
        st.rerun()

with c_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 סגור נושא ופתח שיחה חדשה"):
        new_chat_title = f"שיחה נושא - {time.strftime('%H:%M %d/%m')}"
        chats_dict[new_chat_title] = [{"role": "assistant", "content": "שלום! פתחת נושא חדש. במה אוכל לעזור כעת?"}]
        current_ws["active_chat"] = new_chat_title
        st.success("הנושא נסגר והשיחה נשמרה!")
        st.rerun()

with c_col3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ מחק שיחה זו"):
        if len(chats_dict) > 1:
            chats_dict.pop(active_chat_key)
            current_ws["active_chat"] = list(chats_dict.keys())[0]
            st.success("השיחה נמחקה!")
            st.rerun()
        else:
            st.warning("לא ניתן למחוק את השיחה היחידה בתיק.")

# הצגת השיחה הפעילה
st.markdown(f"**מתכתב בתוך:** `{active_chat_key}`")
chat_history = chats_dict[active_chat_key]

for m in chat_history:
    with st.chat_message(m["role"]):
        st.write(m["content"])

user_input = st.chat_input("כתוב ל-AI הודעה לגבי נושא זה...")
if user_input:
    chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("AI חושב..."):
            time.sleep(0.8)
            # מענה AI המביא בחשבון את יחידות המידה החופשיות והתיק
            units_list = [p['unit'] for p in current_ws['params'] if p.get('unit') not in ['-', None]]
            units_str = ", ".join(units_list) if units_list else "הנתונים שהזנת"
            
            ai_reply = (f"הבנתי אותך לגבי '{user_input}'. בהתחשב ביחידות המדויקות שהגדרת ({units_str}), "
                        f"אני מציע שנבדוק את המשמעות התפעולית/פיננסית בתיק **{ws_name}**. "
                        f"תרצה שאעדכן את מודל הניתוח או שנתחיל לחשב תוכנית פעולה?")
            
            st.write(ai_reply)
            chat_history.append({"role": "assistant", "content": ai_reply})

