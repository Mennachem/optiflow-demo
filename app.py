import streamlit as st
import pandas as pd
import numpy as np
import time

# הגדרת תצוגת העמוד
st.set_page_config(page_title="OptiFlow AI - פתרון בעיות עסקיות", layout="wide")

st.title("OptiFlow AI ⚡")
st.caption("מערכת חכמה לניתוח צווארי בקבוק, סימולציה ואופטימיזציה מותאמת אישית לכל עסק")

# סרגל צד - הגדרת העסק והבעיה
st.sidebar.header("🎯 הגדרת העסק והבעיה")

business_type = st.sidebar.text_input("מה סוג העסק?", value="מסעדת מהיר-לכת (פילוט)")
problem_description = st.sidebar.text_area("תאר את הבעיה / צוואר הבקבוק העיקרי:", 
                                          value="תורים ארוכים בקופה בשעות העומס ועיכוב ביציאת המנות.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 משתנים ופרמטרים של העסק")

# ניהול פרמטרים דינמיים
if 'params' not in st.session_state:
    st.session_state.params = [
        {"name": "זמן טיפול ממוצע ללקוח (דקות)", "value": 4.0},
        {"name": "מספר עמדות / עובדים פעילים", "value": 2.0},
        {"name": "קצב הגעת לקוחות בשעה", "value": 35.0}
    ]

# הוספת פרמטר חדש
with st.sidebar.expander("➕ הוסף פרמטר חדש"):
    new_param_name = st.text_input("שם הפרמטר (למשל: שטח המתן במטרים)")
    new_param_val = st.number_input("ערך", value=1.0, step=0.5)
    if st.button("הוסף משתנה"):
        if new_param_name:
            st.session_state.params.append({"name": new_param_name, "value": new_param_val})
            st.rerun()

# הצגת ועריכת הפרמטרים הקיימים
updated_params = {}
for i, param in enumerate(st.session_state.params):
    updated_params[param["name"]] = st.sidebar.number_input(
        f"{param['name']}:", 
        value=float(param["value"]), 
        key=f"p_{i}"
    )

# תוכן מרכזי
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 נתוני הקלט של העסק")
    st.write(f"**סוג העסק:** {business_type}")
    st.write(f"**תיאור הבעיה:** {problem_description}")
    
    st.markdown("##### פרמטרים שנבדקים:")
    df_params = pd.DataFrame(list(updated_params.items()), columns=["פרמטר", "ערך"])
    st.table(df_params)

with col2:
    st.subheader("💡 ניתוח AI והמלצות לפתרון")
    if st.button("🔍 נתח מחדש וחפש פתרון אופטימלי"):
        with st.spinner("מנתח את הנתונים ומחשב מסלולי שיפור..."):
            time.sleep(1)
            st.success("הניתוח הושלם בהצלחה!")
            
    st.info(f"**אבחון עבור {business_type}:**\n"
            f"על פי הבעיה שהוגדרה ('{problem_description}'), מפתח העומס הנוכחי מושפע מהיחס בין קצב ההגעה לקיבולת הטיפול.")
    
    st.markdown("#### 🎯 פתרונות מומלצים:")
    st.write("1. **אופטימיזציה מבנית:** הסטת קבלת ההזמנות לעמדה דיגיטלית/שירות עצמי.")
    st.write("2. **וויסות עומסים:** הגדרת מסלול מהיר ללקוחות עם הזמנות קטנות.")

st.markdown("---")

# חלק הסימולציה
st.subheader("🧪 סימולציה להרצת הפתרון ויזואלית")
st.caption("כאן תוכל לבחון את היתכנות הפתרון ולראות כיצד שינוי הנתונים משפיע על התוצאה בפועל.")

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    st.markdown("##### הגדרות תרחיש סימולציה")
    efficiency_boost = st.slider("שיפור יעילות מצופה בעקבות הפתרון (%)", 0, 50, 20)
    sim_hours = st.slider("משך הניטור בסימולציה (שעות)", 1, 12, 8)

with sim_col2:
    # יצירת נתוני סימולציה לפי הנתונים שהלקוח הכניס
    hours = [f"שעה {i+1}" for i in range(sim_hours)]
    base_load = np.random.randint(20, 50, size=sim_hours) + updated_params.get("קצב הגעת לקוחות בשעה", 30)
    optimized_load = base_load * (1 - (efficiency_boost / 100))
    
    chart_data = pd.DataFrame({
        "עומס נוכחי (ללא פתרון)": base_load,
        "עומס חיזוי (לאחר פתרון ה-AI)": optimized_load
    }, index=hours)
    
    st.line_chart(chart_data)

st.success("✅ תוכל להוסיף ולשנות פרמטרים בסרגל הצדדי בכל עת – הסימולציה והתוצאות יתעדכנו מול עיניך!")

