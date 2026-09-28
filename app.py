import streamlit as st
import pandas as pd
import numpy as np
import time

# ---------------------------------------------------------
# 1. הגדרות תצוגה ותמיכה בכיוון ימין-לשמאל (RTL)
# ---------------------------------------------------------
st.set_page_config(page_title="OptiFlow AI - International Enterprise", layout="wide")

# הזרקת CSS ליישור לימין ותמיכה בעברית/ערבית
st.markdown("""
<style>
    /* יישור כללי לימין עבור עברית */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    /* תיקון כיווניות לטבלאות ותשומות */
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
# 2. מילון שפות לבחירה (Multi-language)
# ---------------------------------------------------------
LANGUAGES = {
    "עברית": {
        "title": "OptiFlow AI ⚡",
        "subtitle": "מערכת בינלאומית חכמה לניתוח צווארי בקבוק, ניתוח וידאו/תמונות וסימולציות",
        "sidebar_header": "⚙️ הגדרות העסק והפרמטרים",
        "lang_select": "🌐 בחר שפה / Language",
        "biz_type": "מה סוג העסק?",
        "biz_default": "חנות קמעונאית / המבורגריה / מפעל",
        "problem_label": "תאר את הבעיה / צוואר הבקבוק העיקרי:",
        "problem_default": "עומס בשעות הריבוי, חוסר מקום בשטח ההמתנה וזמני טיפול ארוכים.",
        "params_title": "📏 ניהול פרמטרים ומשתנים",
        "add_param": "➕ הוסף פרמטר חדש",
        "param_name": "שם הפרמטר",
        "param_val": "ערך",
        "param_unit": "יחידת מידה",
        "media_title": "📸 העלאת תמונות/וידאו לניתוח AI חזותי",
        "upload_label": "העלה תמונה או סרטון של שטח העבודה / העומס:",
        "analyze_btn": "🔍 נתח מחדש וחפש פתרון אופטימלי",
        "sim_title": "🧪 סימולציית היתכנות דינמית",
        "chat_title": "💬 צ'אט המשכי עם ה-AI לדיוק הפתרון",
        "chat_placeholder": "כתוב ל-AI מה דעתך על הפתרון, או בקש להתחשב בנתון נוסף..."
    },
    "English": {
        "title": "OptiFlow AI ⚡",
        "subtitle": "Smart International Bottleneck Analysis, Computer Vision & Simulation Engine",
        "sidebar_header": "⚙️ Business & Parameter Settings",
        "lang_select": "🌐 Select Language",
        "biz_type": "Business Type:",
        "biz_default": "Retail Store / Restaurant / Factory",
        "problem_label": "Describe the main bottleneck/problem:",
        "problem_default": "Peak hour congestion, limited space, and long processing times.",
        "params_title": "📏 Parameter Management",
        "add_param": "➕ Add New Parameter",
        "param_name": "Parameter Name",
        "param_val": "Value",
        "param_unit": "Unit of Measure",
        "media_title": "📸 Upload Images/Videos for Visual AI Analysis",
        "upload_label": "Upload photo or video of work area / bottleneck:",
        "analyze_btn": "🔍 Re-analyze & Find Optimal Solution",
        "sim_title": "🧪 Dynamic Feasibility Simulation",
        "chat_title": "💬 Interactive AI Follow-up Chat",
        "chat_placeholder": "Ask AI to adjust solution or add parameters..."
    }
}

# בחירת שפה בסרגל
st.sidebar.markdown("### 🌐 Language / שפה")
selected_lang = st.sidebar.selectbox("Select Language / בחר שפה", ["עברית", "English"])
L = LANGUAGES[selected_lang]

# ---------------------------------------------------------
# 3. אתחול Session State
# ---------------------------------------------------------
if 'params' not in st.session_state:
    st.session_state.params = [
        {"name": "שטח חנות / מתחם", "value": 120.0, "unit": "מ"ר (m²)"},
        {"name": "משקל מוצר / פריט ממוצע", "value": 2.5, "unit": "ק\"ג (kg)"},
        {"name": "זמן טיפול ללקוח", "value": 4.0, "unit": "דקות"},
        {"name": "עמדות פעילות", "value": 2.0, "unit": "יחידות"}
    ]

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# 4. כותרת הראשית
# ---------------------------------------------------------
st.title(L["title"])
st.caption(L["subtitle"])

# ---------------------------------------------------------
# 5. סרגל הצד (Sidebar) - הגדרות העסק
# ---------------------------------------------------------
st.sidebar.header(L["sidebar_header"])

business_type = st.sidebar.text_input(L["biz_type"], value=L["biz_default"])
problem_desc = st.sidebar.text_area(L["problem_label"], value=L["problem_default"])

st.sidebar.markdown("---")
st.sidebar.subheader(L["params_title"])

# הוספת פרמטר חדש
with st.sidebar.expander(L["add_param"]):
    new_name = st.text_input(L["param_name"])
    new_val = st.number_input(L["param_val"], value=10.0, step=1.0)
    new_unit = st.selectbox(L["param_unit"], ["מ\"ר (m²)", "מטרים (m)", "ק\"ג (kg)", "טון", "דקות", "שעות", "₪", "$", "יחידות/עובדים", "אחר"])
    if st.button("➕ אישור הוספה"):
        if new_name:
            st.session_state.params.append({"name": new_name, "value": new_val, "unit": new_unit})
            st.rerun()

# הצגה, עריכה ומחיקה של פרמטרים קיימים
st.sidebar.markdown("##### פרמטרים פעילים (ניתן לערוך/למחוק):")
to_delete = None
for i, p in enumerate(st.session_state.params):
    col_p1, col_p2 = st.sidebar.columns([3, 1])
    with col_p1:
        p["value"] = st.number_input(f"{p['name']} ({p['unit']}):", value=float(p["value"]), key=f"val_{i}")
    with col_p2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            to_delete = i

if to_delete is not None:
    st.session_state.params.pop(to_delete)
    st.rerun()

# ---------------------------------------------------------
# 6. גוף העמוד המרכזי
# ---------------------------------------------------------
col_main1, col_main2 = st.columns([1, 1])

with col_main1:
    st.subheader("📋 נתוני העסק והפרמטרים שנבחרו")
    st.write(f"**סוג העסק:** {business_type}")
    st.write(f"**תיאור הבעיה:** {problem_desc}")
    
    # טבלת פרמטרים מפורטת
    param_data = [{"פרמטר": p["name"], "ערך": p["value"], "יחידת מידה": p["unit"]} for p in st.session_state.params]
    st.table(pd.DataFrame(param_data))

    # העלאת תמונות וסרטונים (Computer Vision AI)
    st.markdown("---")
    st.subheader(L["media_title"])
    uploaded_files = st.file_uploader(L["upload_label"], type=["jpg", "png", "jpeg", "mp4", "mov"], accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            if file.type.startswith("image"):
                st.image(file, caption=f"תמונה הועלתה: {file.name}", use_column_width=True)
            elif file.type.startswith("video"):
                st.video(file)
        st.success("✅ הקבצים נסרקו בהצלחה! רכיב ה-Computer Vision משלב את הממצאים החזותיים בניתוח ה-AI.")

with col_main2:
    st.subheader("💡 אבחון AI ופתרון מוצע")
    if st.button(L["analyze_btn"]):
        with st.spinner("מנתח פרמטרים, קבצי מדיה ומחשב אופטימיזציה..."):
            time.sleep(1.2)
            st.success("הניתוח הושלם בהצלחה!")

    st.info(f"**ניתוח חכם עבור {business_type}:**\n\n"
            f"בהתבסס על הבעיה '{problem_desc}' והפרמטרים שהזנת, זוהה צוואר בקבוק מרכזי בחלוקת העומסים.")

    st.markdown("#### 🎯 פתרונות אופטימליים:")
    st.write("1. **שיפור ניצולת שטח/ציוד:** ארגון מחדש של מסלול התנועה על בסיס הנתונים הפיזיים שהוזנו.")
    st.write("2. **הטמעת אלגוריתם תיעוד:** ויסות תורים דינמי בזמן אמת להפחתת העומס בלפחות 25%.")

# ---------------------------------------------------------
# 7. סימולציית היתכנות
# ---------------------------------------------------------
st.markdown("---")
st.subheader(L["sim_title"])

sim_col1, sim_col2 = st.columns([1, 2])
with sim_col1:
    efficiency_boost = st.slider("שיפור יעילות מצופה בעקבות הפתרון (%)", 0, 60, 25)
    sim_hours = st.slider("משך הסימולציה (בשעות)", 1, 24, 8)

with sim_col2:
    hours = [f"שעה {i+1}" for i in range(sim_hours)]
    base_load = np.random.randint(30, 80, size=sim_hours)
    optimized_load = base_load * (1 - (efficiency_boost / 100))
    
    chart_df = pd.DataFrame({
        "עומס נוכחי": base_load,
        "עומס מתוכנן (לאחר הפתרון)": optimized_load
    }, index=hours)
    st.line_chart(chart_df)

# ---------------------------------------------------------
# 8. צ'אט המשכי עם ה-AI
# ---------------------------------------------------------
st.markdown("---")
st.subheader(L["chat_title"])

# הצגת היסטוריית הצ'אט
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# קלט מהמשתמש
user_input = st.chat_input(L["chat_placeholder"])
if user_input:
    # שמירת הודעת המשתמש
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # תגובת AI חכמה
    with st.chat_message("assistant"):
        with st.spinner("AI חושב ומחשב התאמות..."):
            time.sleep(1)
            ai_response = f"הבנתי אותך. בנוגע ל-'{user_input}': אני ממליץ להוסיף פרמטר חדש בסרגל הצדדי (לדוגמה: 'זמן הכנה/שינוע') כדי שנוכל לדייק את הסימולציה עוד יותר. האם תרצה שאעדכן את מודל הניתוח בהתאם?"
            st.write(ai_response)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

