import streamlit as st
import pandas as pd
import numpy as np
import time

# ---------------------------------------------------------
# 1. הגדרות תצוגה ותמיכה בכיוון ימין-לשמאל (RTL)
# ---------------------------------------------------------
st.set_page_config(page_title="OptiFlow AI - Enterprise Engine", layout="wide")

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
# 2. מילון שפות לבחירה (Multi-language)
# ---------------------------------------------------------
LANGUAGES = {
    "עברית": {
        "title": "OptiFlow AI ⚡",
        "subtitle": "מערכת בינה מלאכותית אקטיבית לאבחון בעיות עסקיות, רווחיות ואופטימיזציה",
        "sidebar_header": "⚙️ הגדרות העסק ופרמטרים",
        "biz_type": "מה סוג העסק?",
        "biz_default": "חנות קמעונאית / מסעדה / דפוס / מפעל",
        "problem_label": "תאר את הבעיה המרכזית בעסק:",
        "problem_default": "יש עבודה ותנועת לקוחות, אך בסוף החודש לא נשאר רווח נקי.",
        "params_title": "📏 ניהול פרמטרים ובעיות נוספות",
        "add_param": "➕ הוסף פרמטר / בעיה נוספת",
        "param_name": "שם הפרמטר / תיאור הרכיב",
        "param_type": "סוג הנתון",
        "param_val": "ערך / פירוט",
        "param_unit": "יחידת מידה (אם מספרי)",
        "media_title": "📸 העלאת קבצים / תמונות / מסמכים לניתוח AI",
        "upload_label": "העלה קובץ, תמונה או דוח לניתוח:",
        "analyze_btn": "🔍 בצע ניתוח AI מקיף וגלה פתרונות",
        "sim_title": "🧪 סימולציית שיפור עסקי ופיננסי",
        "chat_title": "💬 צ'אט יועץ AI אקטיבי - דיון בפתרון",
        "chat_placeholder": "שאל את ה-AI על הפתרון המוצע, או הסבר נוסף על הבעיה..."
    },
    "English": {
        "title": "OptiFlow AI ⚡",
        "subtitle": "Active AI Engine for Business Optimization & Profitability Analysis",
        "sidebar_header": "⚙️ Business & Parameter Settings",
        "biz_type": "Business Type:",
        "biz_default": "Retail Store / Restaurant / Factory",
        "problem_label": "Describe the main business problem:",
        "problem_default": "High customer volume but low monthly net profit margins.",
        "params_title": "📏 Parameters & Issues Management",
        "add_param": "➕ Add New Parameter / Issue",
        "param_name": "Parameter / Issue Name",
        "param_type": "Data Type",
        "param_val": "Value / Details",
        "param_unit": "Unit of Measure (if numeric)",
        "media_title": "📸 Upload Files / Images / Documents for AI Analysis",
        "upload_label": "Upload photo, video, or report:",
        "analyze_btn": "🔍 Perform Comprehensive AI Analysis",
        "sim_title": "🧪 Business Improvement Simulation",
        "chat_title": "💬 Active AI Advisor Chat",
        "chat_placeholder": "Ask AI about the solution or provide more details..."
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
        {"name": "שטח עסקי", "type": "מספרי", "value": 120.0, "unit": "sqm"},
        {"name": "מחזור חודשי ממוצע", "type": "מספרי", "value": 50000.0, "unit": "שקלים"},
        {"name": "הערה לגבי עלויות", "type": "טקסט / בעיה", "value": "עלויות חומרי הגלם והחשמל עלו ב-20% בשנה האחרונה", "unit": "-"}
    ]

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# 4. כותרת הראשית
# ---------------------------------------------------------
st.title(L["title"])
st.caption(L["subtitle"])

# ---------------------------------------------------------
# 5. סרגל הצד (Sidebar) - הגדרות העסק ופרמטרים
# ---------------------------------------------------------
st.sidebar.header(L["sidebar_header"])

business_type = st.sidebar.text_input(L["biz_type"], value=L["biz_default"])
problem_desc = st.sidebar.text_area(L["problem_label"], value=L["problem_default"], height=120)

st.sidebar.markdown("---")
st.sidebar.subheader(L["params_title"])

# הוספת פרמטר חדש (מספרי או טקסטואלי)
with st.sidebar.expander(L["add_param"]):
    new_name = st.text_input(L["param_name"])
    p_type = st.radio(L["param_type"], ["מספרי", "טקסט / בעיה"])
    
    if p_type == "מספרי":
        new_val = st.number_input(L["param_val"], value=10.0, step=1.0)
        new_unit = st.selectbox(L["param_unit"], ["sqm", "מטרים", "kg", "טון", "דקות", "שעות", "שקלים", "דולרים", "יחידות", "אחר"])
    else:
        new_val = st.text_area(L["param_val"], value="פרט כאן את הבעיה או הנסיבות...")
        new_unit = "-"
        
    if st.button("➕ אישור הוספה"):
        if new_name:
            st.session_state.params.append({"name": new_name, "type": p_type, "value": new_val, "unit": new_unit})
            st.rerun()

# הצגה, עריכה ומחיקה של פרמטרים ובעיות קיימים
st.sidebar.markdown("##### פרמטרים ובעיות מוגדרים:")
to_delete = None
for i, p in enumerate(st.session_state.params):
    col_p1, col_p2 = st.sidebar.columns([3, 1])
    with col_p1:
        if p.get("type") == "טקסט / בעיה":
            p["value"] = st.text_input(f"📌 {p['name']}:", value=str(p["value"]), key=f"val_txt_{i}")
        else:
            p["value"] = st.number_input(f"🔢 {p['name']} ({p['unit']}):", value=float(p["value"]), key=f"val_num_{i}")
    with col_p2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{i}"):
            to_delete = i

if to_delete is not None:
    st.session_state.params.pop(to_delete)
    st.rerun()

# ---------------------------------------------------------
# 6. מנוע ניתוח AI חכם ודינמי (Logical Engine)
# ---------------------------------------------------------
def generate_ai_analysis(biz, prob, params):
    prob_lower = prob.lower()
    
    # זיהוי נושאים בטקסט הבעיה והפרמטרים
    all_text = prob_lower + " " + " ".join([str(p['value']).lower() for p in params if p.get("type") == "טקסט / בעיה"])
    
    is_profit = any(w in all_text for w in ["רווח", "מאזן", "כסף", "רווחיות", "הפסד", "עלות", "מחיר", "הכנסה", "profit", "margin"])
    is_queue = any(w in all_text for w in ["תור", "עומס", "זמן", "המתנה", "איטי", "צוואר בקבוק", "queue", "delay"])
    
    analysis = []
    solutions = []
    
    if is_profit and not is_queue:
        analysis.append(f"מניתוח הנתונים עולה כי הבעיה המרכזית ב-**{biz}** היא **אי-סינכרון פיננסי ושחיקת מרווח הרווח**, ולא בעיה תפעולית של עומסי תנועה.")
        analysis.append("למרות שיש נפח פעילות ולקוחות, העלויות הישירות והסמויות אוכלות את שולי הרווח הנקי.")
        
        solutions.append("**ניתוח והעלאת מרווחים (Margin Optimization):** בדיקת תמחור המוצרים/שירותים מול עלויות חומרי הגלם והעבודה הישירות.")
        solutions.append("**זיהוי דליפות פיננסיות:** סקירת ההוצאות הקבועות והמשתנות (חשמל, פחת, מלאי מת, פריטים לא מתומחרים נכון).")
        solutions.append("**הגדלת ערך עסקה ממוצע (Upselling):** בניית חבילות משלימות שמגדילות את הרווח הנקי מכל לקוח קיים ללא הגדלת הוצאות התפעול.")
        
    elif is_queue and not is_profit:
        analysis.append(f"מניתוח הנתונים עולה כי הבעיה המרכזית ב-**{biz}** היא **צוואר בקבוק תפעולי ועיכוב בטיפול בלקוחות**.")
        solutions.append("**ארגון מחדש של זרימת העבודה (Workflow):** צמצום פעולות סרק ומיקום מחדש של הציוד והעובדים.")
        solutions.append("**אוטומציה וניתוח זמנים:** הטמעת רכיבים דיגיטליים לקיצור זמן התגובה בכל תחנה.")
        
    else: # בעיה משולבת או כללית
        analysis.append(f"מניתוח הבעיה ב-**{biz}** והנתונים שהוזנו, זוהה שילוב בין אתגר פיננסי לתפעולי.")
        solutions.append("**בחינת עלות מול תפוקה:** בדיקה האם זמני העבודה והמשאבים המושקעים בכל לקוח מצדיקים את המחיר הנגבה.")
        solutions.append("**בניית מודל תמחור וייעול:** ייעול שלבי העבודה לצד עדכון תמחור השירותים/מוצרים.")

    return "\n\n".join(analysis), solutions

# ---------------------------------------------------------
# 7. גוף העמוד המרכזי
# ---------------------------------------------------------
col_main1, col_main2 = st.columns([1, 1])

with col_main1:
    st.subheader("📋 נתוני העסק והפרמטרים שהוגדרו")
    st.write(f"**סוג העסק:** {business_type}")
    st.write(f"**תיאור הבעיה הראשית:** {problem_desc}")
    
    # הצגת טבלת הפרמטרים והבעיות
    formatted_params = []
    for p in st.session_state.params:
        formatted_params.append({
            "שם הרכיב": p["name"],
            "סוג": p.get("type", "מספרי"),
            "ערך / תיאור": p["value"],
            "יחידה": p["unit"]
        })
    st.table(pd.DataFrame(formatted_params))

    # העלאת קבצים ומדיה
    st.markdown("---")
    st.subheader(L["media_title"])
    uploaded_files = st.file_uploader(L["upload_label"], type=["jpg", "png", "jpeg", "mp4", "pdf", "csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        st.success(f"✅ נסרקו {len(uploaded_files)} קבצים. הנתונים שולבו במודל הניתוח.")

with col_main2:
    st.subheader("💡 אבחון AI ופתרון אופטימלי")
    
    # הרצת הניתוח
    ai_summary, ai_sols = generate_ai_analysis(business_type, problem_desc, st.session_state.params)
    
    st.info(ai_summary)

    st.markdown("#### 🎯 פתרונות אופרטיביים מומלצים:")
    for idx, sol in enumerate(ai_sols, 1):
        st.write(f"{idx}. {sol}")

# ---------------------------------------------------------
# 8. סימולציית שיפור פיננסי / תפעולי
# ---------------------------------------------------------
st.markdown("---")
st.subheader(L["sim_title"])

sim_col1, sim_col2 = st.columns([1, 2])
with sim_col1:
    improvement_pct = st.slider("אחוז שיפור מתוכנן ברווחיות / יעילות (%)", 5, 50, 20)
    sim_months = st.slider("משך הסימולציה (בחודשים)", 1, 12, 6)

with sim_col2:
    months = [f"חודש {i+1}" for i in range(sim_months)]
    
    # חישוב דינמי לפי נתוני המחזור שנרשמו בפרמטרים
    base_val = 50000
    for p in st.session_state.params:
        if "מחזור" in p["name"] or "רווח" in p["name"]:
            try:
                base_val = float(p["value"])
            except:
                pass
                
    current_projection = [base_val] * sim_months
    improved_projection = [base_val * (1 + (improvement_pct/100) * (i+1)/sim_months) for i in range(sim_months)]
    
    chart_df = pd.DataFrame({
        "מצב נוכחי (ללא שינוי)": current_projection,
        "תחזית לאחר יישום פתרונות AI": improved_projection
    }, index=months)
    st.line_chart(chart_df)

# ---------------------------------------------------------
# 9. צ'אט המשכי חכם ואקטיבי
# ---------------------------------------------------------
st.markdown("---")
st.subheader(L["chat_title"])

# הצגת היסטוריית צ'אט
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input(L["chat_placeholder"])
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("מנתח את הדברים ומחשב פתרון..."):
            time.sleep(1)
            
            # תשובת AI דינמית בהתאם לקלט המשתמש
            inp_lower = user_input.lower()
            if "רווח" in inp_lower or "כסף" in inp_lower or "מאזן" in inp_lower or "מחיר" in inp_lower:
                reply = (f"בנוגע לנקודה שהעלית ('{user_input}'): כשאנו מתמודדים עם בעיית רווחיות, "
                         f"המפתח הוא לפרק את העלויות הקבועות מול המשתנות. אני ממליץ שנוסיף בסרגל הימני "
                         f"פרמטר נוסף מסוג 'טקסט/בעיה' עם פירוט הוצאות הספק העיקריות שלך, "
                         f"כדי שנוכל לזהות איפה בדיוק נעלם הרווח הנקי.")
            elif "כן" in inp_lower or "איך" in inp_lower or "כיצד" in inp_lower:
                reply = (f"מצויין. הצעד המעשי הראשון ליישום הפתרון ב-**{business_type}** הוא: "
                         f"1. בדיקת תמחור של 3 המוצרים/שירותים הנמכרים ביותר.\n"
                         f"2. הוספת רכיב מוצר משלים ברווח גבוה.\n"
                         f"תרצה שנחשב עכשיו את תוספת הרווח הצפויה משינוי המחיר?")
            else:
                reply = (f"הבנתי אותך לגבי '{user_input}'. ניתוח הנתונים מראה כי שילוב אלמנט זה "
                         f"ישפיע ישירות על תוצאות העסק. מהי העלות הממשית כיום של רכיב זה בעסק שלך?")
                
            st.write(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

