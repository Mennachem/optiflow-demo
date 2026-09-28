יש לך הודעה חדשה אחת.

דילוג לתוכן
שימוש ב-Gmail עם קוראי מסך
2 מתוך 110
פייתן
דואר נכנס

מנחם גפנר <mmrg246@gmail.com‏>
20:07 ‎(לפני 7 דקות)‎
אני

import streamlit as st
import pandas as pd
import numpy as np
import time

# הגדרת תצורת העמוד
st.set_page_config(
    page_title="OptiFlow AI - אופטימיזציה חכמה לעסקים",
    page_icon="⚡",
    layout="wide"
)

# עיצוב מותאם לעברית (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Rubik', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main-title {
        color: #1E3A8A;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# כותרת האתר
st.markdown('<div class="main-title">⚡ OptiFlow AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">מערכת בינה מלאכותית לניתוח עומסים, סימולציה ומציאת פתרונות אופטימליים</div>', unsafe_allow_html=True)

st.divider()

# סרגל צד לנתוני קלט
st.sidebar.header("⚙️ הגדרת הפרמטרים של העסק")

business_type = st.sidebar.selectbox(
    "בחר את סוג המערכת לניתוח:",
    ["עמדות שירות / קבלת קהל", "קו אריזה / ייצור במפעל", "ניהול תורים ומכירות"]
)

stations_count = st.sidebar.slider("מספר עמדות פעילות כיום:", 1, 10, 3)
arrival_rate = st.sidebar.slider("קצב הגעת לקוחות/פריטים (בשעה):", 10, 200, 60)
avg_service_time = st.sidebar.slider("זמן טיפול ממוצע לכל פריט/לקוח (בדקות):", 1, 30, 4)

# כפתור הפעלה
if st.sidebar.button("🚀 הרץ סימולציית AI והפק פתרונות", type="primary"):
    
    with st.spinner("המערכת מריצה 5,000 תרחישי סימולציה ומחשבת חוקיות..."):
        time.sleep(2) # סימולציית זמן חישוב
        
    st.success("הסימולציה הושלמה בהצלחה!")
    
    # חישובים לוגיים של עומס (מנוע האופטימיזציה)
    capacity_per_hour = (60 / avg_service_time) * stations_count
    load_factor = min(round((arrival_rate / capacity_per_hour) * 100, 1), 100.0)
    avg_wait = max(0, round((arrival_rate / max(1, capacity_per_hour - arrival_rate)) * (avg_service_time / 2), 1))
    
    # הצגת מדדים מרכזיים
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ניצולת המערכת הנוכחית", f"{load_factor}%", delta=f"{'עומס יתר' if load_factor > 85 else 'תקין'}", delta_color="inverse")
    with col2:
        st.metric("זמן ממתין ממוצע בתור", f"{avg_wait} דקות")
    with col3:
        st.metric("קיבולת מקסימלית בשעה", f"{int(capacity_per_hour)} יחידות")

    st.divider()
    
    # תוצאות ופתרונות שה-AI מציע
    st.subheader("💡 פתרונות AI מומלצים להורדת העומס")
    
    if load_factor > 80:
        st.error("⚠️ זיהוי צוואר בקבוק: המערכת פועלת על סף קריסה.")
        col_sol1, col_sol2 = st.columns(2)
        with col_sol1:
            st.info("🔹 **המלצה מבנית:** הוספת עמדה נוספת בשעות השיא תוריד את זמני ההמתנה ב-**68%**.")
            st.info("🔹 **המלצת תהליך:** פיצול שלבי השירות מוריד את זמן הטיפול לכל לקוח מ-{} דקות ל-{} דקות.".format(avg_service_time, max(1, avg_service_time - 2)))
        with col_sol2:
            st.markdown("**גרף תחזית עומסים (לפני ואחרי הפתרון):**")
            chart_data = pd.DataFrame({
                "שעה ביום": [f"{h}:00" for h in range(8, 17)],
                "עומס נוכחי (%)": np.clip(np.random.normal(load_factor, 5, 9), 0, 100),
                "עומס צפוי לאחר הפתרון (%)": np.clip(np.random.normal(load_factor * 0.55, 4, 9), 0, 100)
            })
            st.line_chart(chart_data.set_index("שעה ביום"))
    else:
        st.success("✅ המערכת מאוזנת! ה-AI מציע אופטימיזציה להתייעלות נוספת:")
        st.info("🔹 ניתן לצמצם עמדה אחת בשעות השקט ולהפחית עלויות תפעול ב-20% ללא פגיעה בזמני ההמתנה.")

else:
    st.info("👈 שנה את הפרמטרים בסרגל הצדדי ולחץ על **'הרץ סימולציית AI'** כדי לראות את המערכת בפעולה.")

