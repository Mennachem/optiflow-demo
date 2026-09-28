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
# 2. אתחול Session State (התחברות, שפה, תיקים וצ'אט)
# ---------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'lang' not in st.session_state:
    st.session_state.lang = "עברית"

if 'workspaces' not in st.session_state:
    st.session_state.workspaces = {
        "לקוח - מנדי (חיתוך פלסטיק)": {
            "biz_type": "חיתוך פלסטיק בלייזר",
            "problem": "עיקר העסק בנוי על שלטים לילדות. בהתחלה זה היה רווחי מאוד, היום יש הרבה מתחרים ואני צריך לחדש דברים יחודיים שרק אני עושה.",
            "params": [
                {"name": "כמות חנויות שעובדות איתי", "type": "מספרי", "value": 60.0, "unit": "חנויות"},
                {"name": "כמות הזמנות ממוצע ליום", "type": "מספרי", "value": 8.0, "unit": "הזמנות"},
                {"name": "עלות שלטים", "type": "טקסט / בעיה", "value": "בין 150 ל 300", "unit": "שקלים"}
            ],
            "chats": {
                "שיחה ראשונית": [
                    {"role": "assistant", "content": "שלום! ניתחתי את הנתונים של עסק חיתוך הפלסטיק. איך אוכל לסייע בפיתוח המוצרים היחודיים?"}
                ]
            },
            "active_chat": "שיחה ראשונית",
            "files": []
        }
    }

if 'active_workspace' not in st.session_state:
    st.session_state.active_workspace = "לקוח - מנדי (חיתוך פלסטיק)"

# ---------------------------------------------------------
# 3. מסך התחברות (מערכת משתמשים וסיסמאות)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔒 התחברות למערכת OptiFlow AI</h2>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        username = st.text_input("שם משתמש / אימייל:")
        password = st.text_input("סיסמה:", type="password")
        if st.button("🔑 התחבר לאזור האישי"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.user_name = username
                st.success("התחברת בהצלחה!")
                st.rerun()
            else:
                st.error("אנא הזן שם משתמש וסיסמה.")
    st.stop()

# ---------------------------------------------------------
# 4. עיצוב ושפה לפי בחירה
# ---------------------------------------------------------
is_rtl = st.session_state.lang in ["עברית", "العربية"]
dir_style = "rtl" if is_rtl else "ltr"

st.markdown(f"""
<style>
    .stApp {{
        direction: {dir_style};
        text-align: {'right' if is_rtl else 'left'};
    }}
    div[data-testid="stSidebar"] {{
        direction: {dir_style};
        text-align: {'right' if is_rtl else 'left'};
    }}
    input, textarea, select {{
        direction: {dir_style} !important;
        text-align: {'right' if is_rtl else 'left'} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. סרגל צד (Sidebar) - אזור אישי, הגדרות ושפה
# ---------------------------------------------------------
st.sidebar.title("OptiFlow AI ⚡")
st.sidebar.markdown(f"👤 מחובר כ: **{st.session_state.get('user_name', 'משתמש')}**")

if st.sidebar.button("🚪 התנתק"):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
st.session_state.lang = st.sidebar.selectbox("🌐 שפת ממשק / Language:", ["עברית", "English", "Español"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 ניהול תיקי לקוחות (אזור אישי)")

ws_keys = list(st.session_state.workspaces.keys())
selected_ws = st.sidebar.selectbox("בחר תיק פעיל:", ws_keys, index=ws_keys.index(st.session_state.active_workspace))

if selected_ws != st.session_state.active_workspace:
    st.session_state.active_workspace = selected_ws
    st.rerun()

with st.sidebar.expander("➕ פתח תיק לקוח חדש"):
    new_ws_title = st.text_input("שם הלקוח / הפרויקט:")
    if st.button("צור תיק"):
        if new_ws_title and new_ws_title not in st.session_state.workspaces:
            st.session_state.workspaces[new_ws_title] = {
                "biz_type": "עסק חדש",
                "problem": "",
                "params": [],
                "chats": {"שיחה חדשה": [{"role": "assistant", "content": "שלום! במה אוכל לעזור בתיק זה?"}]},
                "active_chat": "שיחה חדשה",
                "files": []
            }
            st.session_state.active_workspace = new_ws_title
            st.rerun()

# הפניה לתיק הנוכחי
cur_ws = st.session_state.workspaces[st.session_state.active_workspace]

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ פרמטרים ונתונים לתיק")

cur_ws["biz_type"] = st.sidebar.text_input("סוג העסק:", value=cur_ws["biz_type"])
cur_ws["problem"] = st.sidebar.text_area("תיאור הבעיה / האתגר:", value=cur_ws["problem"], height=100)

with st.sidebar.expander("➕ הוסף פרמטר / נתון למדד"):
    p_name = st.text_input("שם הפרמטר (כגון: סוג מכונה, עלות יצור):")
    p_type = st.radio("סוג הנתון:", ["מספרי", "טקסט / בעיה"])
    
    if p_type == "מספרי":
        p_val = st.number_input("ערך:", value=1.0)
        p_unit = st.text_input('יחידת מידה חופשית (כגון: ש"ח, יחידות, %, שעות, יחידה לשעה):', value='ש"ח')
    else:
        p_val = st.text_input("תיאור / ערך טקסטואלי:")
        p_unit = "-"
        
    if st.button("אישור הוספה"):
        if p_name:
            cur_ws["params"].append({"name": p_name, "type": p_type, "value": p_val, "unit": p_unit})
            st.rerun()

# עריכה/מחיקה של פרמטרים קיימים
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

# ---------------------------------------------------------
# 6. מנוע בינה מלאכותית יצירתי + הצעת פרמטרים חסרים
# ---------------------------------------------------------
def generate_ai_solutions(biz, prob, params):
    param_str = ", ".join([f"{p['name']}: {p['value']} {p['unit']}" for p in params])
    
    recommended_params = []
    if "חיתוך" in biz or "פלסטיק" in biz or "ייצור" in biz:
        recommended_params = ["סוג מכונת הלייזר / עוצמה (Watt)", "זמן חיתוך ממוצע למוצר", "עלות חומר גלם למטר", "שיעור פחת / שאריות חומר"]
    elif "מסעדה" in biz or "אוכל" in biz:
        recommended_params = ["עלות מנה ממוצעת (Food Cost)", "תפוסת שולחנות בשעות שיא", "אחוז נטישת משלוחים"]
    else:
        recommended_params = ["עלות רכישת לקוח (CAC)", "ערך חיי לקוח (LTV)", "זמן עבודה מושקע במוצר", "שיעור המרה בחנות/אתר"]

    solutions = []
    if "שלטים" in prob or "חיתוך" in biz:
        solutions.append({
            "title": "🎨 מעבר לשלט תלת-ממדי משולב חומרים (Wood & Acrylic Hybrid)",
            "desc": "שילוב עץ טבעי עם אקריליק שקוף ומואר. מתחרים המשתמשים בלייזר פשוט אינם יכולים להעתיק זאת בקלות. מעלה את נתפס השוק של השלט מ-150 ש\"ח ל-350 ש\"ח.",
            "sim": "סכמת ייצור: חיתוך אקריליק 3 מ\"מ ➔ הדבקה על בסיס עץ אורן אורגני ➔ שילוב תאורת LED נסתרת."
        })
        solutions.append({
            "title": "📦 מודל ערכות DIY להרכבה עצמית לילדות (DIY Name Kit)",
            "desc": "מכירת שלט בחלקים יחד עם צבעים מיוחדים ומכחול. הילדה וההורים מכינים את השלט בעצמם. זה מייצר חוויה משפחתית ופותח ערוץ מכירה חדש לחנויות יצירה וצעצועים.",
            "sim": "אריזה: קופסת מיתוג שטוחה ➔ חלקי פלסטיק חתוכים בלייזר ➔ דף הוראות וברקוד לסרטון הדרכה."
        })
        solutions.append({
            "title": "🔄 תוכנית מנוי עונתית לחנויות (Seasonal Refresh Club)",
            "desc": "אספקת תצוגות מתחלפות לחנויות לפי חגים ועונות (חזרה לבית הספר, ימי הולדת). החנות מקבלת מרווח גבוה יותר והעסק מקבל הכנסה חודשית קבועה.",
            "sim": "מודל עבודה: אספקה בתחילת חודש ➔ איסוף עודפים בסוף חודש ➔ חיוב ריטיינר קבוע."
        })
    else:
        solutions.append({
            "title": "🚀 תמחור פרימיום מבוסס ערך (Value-Based Pricing)",
            "desc": "אריזת השירות/המוצר מחדש והעלאת מחיר תוך מתן אחריות מורחבת וערך ייחודי.",
            "sim": "מבנה מודל: חבילת בסיס ➔ חבילת פרימיום ➔ VIP"
        })

    return recommended_params, solutions

# ---------------------------------------------------------
# 7. הגוף המרכזי של האפליקציה
# ---------------------------------------------------------
st.title(f"📂 {st.session_state.active_workspace}")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 נתוני העסק והפרמטרים שנרשמו")
    st.write(f"**תחום / סוג עסק:** {cur_ws['biz_type']}")
    st.write(f"**תיאור הבעיה:** {cur_ws['problem']}")
    
    if cur_ws["params"]:
        df_p = pd.DataFrame([{"פרמטר": p["name"], "ערך": p["value"], "יחידה": p["unit"]} for p in cur_ws["params"]])
        st.table(df_p)

    rec_params, ai_sols = generate_ai_solutions(cur_ws["biz_type"], cur_ws["problem"], cur_ws["params"])
    
    st.markdown("---")
    st.subheader("💡 פרמטרים מומלצים להוספה (לדיוק הניתוח):")
    st.info("הזנת הנתונים הבאים תאפשר למערכת לספק חישובים ופתרונות מדויקים עוד יותר:")
    for rp in rec_params:
        col_rp1, col_rp2 = st.columns([3, 1])
        col_rp1.write(f"• **{rp}**")
        if col_rp2.button("➕ הוסף", key=f"add_rec_{rp}"):
            cur_ws["params"].append({"name": rp, "type": "מספרי", "value": 0.0, "unit": "יחידות"})
            st.rerun()

    st.markdown("---")
    st.subheader("📁 העלאת קבצים, תמונות ותיקיות ZIP")
    uploaded_files = st.file_uploader("העלה תמונות, מסמכים או קובצי ZIP דחוסים:", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "zip", "csv", "xlsx"])
    
    if uploaded_files:
        for f in uploaded_files:
            if f.name.endswith('.zip'):
                st.success(f"📦 נפתח קובץ דחוס: {f.name}")
                with zipfile.ZipFile(io.BytesIO(f.read())) as z:
                    for filename in z.namelist():
                        st.write(f"📄 מוצא בקובץ: `{filename}`")
            else:
                st.write(f"✅ נטען קובץ: `{f.name}`")

with col_right:
    st.subheader("🎯 ניתוח AI, סימולציה ופתרונות יצירתיים")
    if st.button("🔄 לחץ לחישוב מחדש של הפתרונות", type="primary"):
        with st.spinner("מחשב ומנתח נתונים מחדש..."):
            time.sleep(0.7)
            st.success("החישוב עודכן בהצלחה!")

    for idx, sol in enumerate(ai_sols, 1):
        with st.expander(f"פתרון {idx}: {sol['title']}", expanded=True):
            st.write(f"**תיאור מפורט:** {sol['desc']}")
            st.markdown(f"**🎬 סימולציה / סכמת הדגמה:**")
            st.info(sol['sim'])

# ---------------------------------------------------------
# 8. צ'אט חכם מסונכרן
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💬 צ'אט יועץ AI מסונכרן")

chats = cur_ws["chats"]
active_c_name = cur_ws.get("active_chat", list(chats.keys())[0])

col_c1, col_c2, col_c3 = st.columns([2, 1, 1])

with col_c1:
    selected_c = st.selectbox("שיחה פעילה:", list(chats.keys()), index=list(chats.keys()).index(active_c_name) if active_c_name in chats else 0)
    if selected_c != active_c_name:
        cur_ws["active_chat"] = selected_c
        st.rerun()

with col_c2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 סגור נושא ופתח שיחה חדשה"):
        new_c_title = f"שיחה בנושא חדש ({time.strftime('%H:%M')})"
        chats[new_c_title] = [{"role": "assistant", "content": "הנושא הקודם נסגר ונשמר. פתחנו שיחה חדשה, במה נוכל להתמקד כעת?"}]
        cur_ws["active_chat"] = new_c_title
        st.rerun()

with col_c3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ מחק שיחה זו"):
        if len(chats) > 1:
            chats.pop(active_c_name)
            cur_ws["active_chat"] = list(chats.keys())[0]
            st.rerun()
        else:
            st.warning("חייבת להישאר לפחות שיחה אחת.")

current_chat_history = chats[cur_ws["active_chat"]]

for msg in current_chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

chat_input = st.chat_input("שאל את ה-AI שאלה, בקש פתרון חלופי או התייעץ...")
if chat_input:
    current_chat_history.append({"role": "user", "content": chat_input})
    with st.chat_message("user"):
        st.write(chat_input)
        
    with st.chat_message("assistant"):
        with st.spinner("AI מנתח את התיק והפתרונות..."):
            time.sleep(0.8)
            
            reply = ""
            if "פתרון" in chat_input or "רעיון" in chat_input or "עוד" in chat_input:
                reply = f"בהתבסס על הבעיה בתיק ({cur_ws['problem']}), הנה פתרון חלופי נוסף: יצירת סדרת שלטי תאורה קטנים לשולחנות עבודה/חדרי שינה. זה חוסך בחומר גלם ומעלה את הרווחיות."
            elif "לא מרוצה" in chat_input or "לא מתאים" in chat_input:
                reply = "מבין אותך לחלוטין. בוא נשנה גישה: במקום למכור לפרטיים או חנויות, נוכל לפנות ישירות לערייות, מתנ\"סים ומארגני אירועים להזמנות מוסדיות גדולות. האם תרצה שנגדיר פרמטרים לעלויות סיטונאיות?"
            else:
                reply = f"קיבלתי את דבריך לגבי '{chat_input}'. העברתי זאת לניתוח התיק. האם תרצה שנוסיף פרמטר חדש בסרגל הצד כדי לעדכן את חישוב הרווחיות?"
            
            st.write(reply)
            current_chat_history.append({"role": "assistant", "content": reply})

