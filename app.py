<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OptiFlow AI</title>
    <style>
        :root {
            --primary: #003366;
            --primary-hover: #002244;
            --bg-light: #f4f6f9;
            --card-bg: #ffffff;
            --text-dark: #333333;
            --accent-green: #00875a;
            --border-color: #dddddd;
        }

        * {
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-light);
            color: var(--text-dark);
            min-height: 100vh;
        }

        .hidden {
            display: none !important;
        }

        /* --- כפתור/לוגו חזרה לרענון/בית --- */
        .app-logo {
            cursor: pointer;
            font-weight: bold;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* --- סגנונות מסכי התחברות / הרשמה / שחזור (מסכים 1, 2, 3) --- */
        .auth-container {
            max-width: 450px;
            margin: 60px auto;
            background: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .auth-header {
            background-color: var(--primary);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 1.4rem;
            position: relative;
        }

        .auth-body {
            padding: 25px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
            position: relative;
        }

        .form-group label {
            font-size: 0.9rem;
            font-weight: 600;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .form-control {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 1rem;
            background-color: #f9f9f9;
        }

        .toggle-password {
            position: absolute;
            left: 10px;
            cursor: pointer;
            background: none;
            border: none;
            font-size: 1.1rem;
            user-select: none;
        }

        .btn {
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
            text-align: center;
            text-decoration: none;
        }

        .btn-primary {
            background-color: var(--primary);
            color: white;
        }

        .btn-primary:hover {
            background-color: var(--primary-hover);
        }

        .btn-secondary {
            background-color: #e0e0e0;
            color: #333;
        }

        .btn-link {
            background: none;
            color: var(--primary);
            font-size: 0.85rem;
            text-decoration: underline;
            cursor: pointer;
            padding: 0;
            border: none;
            text-align: right;
        }

        .auth-actions {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 5px;
        }

        /* --- סגנונות מסך ראשי לקוח --- */
        .main-header {
            background-color: var(--primary);
            color: white;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .main-nav {
            display: flex;
            gap: 20px;
            align-items: center;
            background-color: #ffffff;
            padding: 8px 16px;
            border-bottom: 1px solid #e0e0e0;
        }

        .main-nav a {
            color: var(--text-dark);
            text-decoration: none;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .main-layout {
            display: grid;
            grid-template-columns: 2fr 1fr; /* שמאל: עסקים/נושאים, ימין: פרטי לקוח */
            gap: 20px;
            padding: 20px;
            max-width: 1300px;
            margin: 0 auto;
            position: relative;
            min-height: calc(100vh - 120px);
        }

        .card {
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow: hidden;
        }

        .card-header {
            background-color: var(--primary);
            color: white;
            padding: 12px 16px;
            font-size: 1.1rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-body {
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
            font-size: 0.95rem;
        }

        .info-label {
            font-weight: bold;
            color: #555;
        }

        .topics-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .topic-item {
            background-color: #f8f9fa;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            cursor: pointer;
            transition: transform 0.1s, box-shadow 0.1s;
        }

        .topic-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            border-color: var(--primary);
        }

        .btn-create-business {
            position: absolute;
            bottom: 20px;
            right: 20px; /* בצד שמאל של המסך (RTL) */
            background-color: var(--accent-green);
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            cursor: pointer;
            border: none;
        }

        .btn-create-business:hover {
            background-color: #006c48;
        }
    </style>
</head>
<body>

    <!-- ==================== מסך 1: התחברות ==================== -->
    <div id="screen-1" class="auth-container">
        <div class="auth-header">
            <div class="app-logo" onclick="goToScreen('screen-1')">
                OptiFlow AI 🚀
            </div>
            <span style="font-size: 0.9rem; font-weight: normal;">כניסה למערכת</span>
        </div>
        <div class="auth-body">
            <div class="form-group">
                <label>שם משתמש (2)</label>
                <input type="text" id="login-username" class="form-control" placeholder="הכנס שם משתמש">
            </div>

            <div class="form-group">
                <label>סיסמה (3)</label>
                <div class="input-wrapper">
                    <input type="password" id="login-password" class="form-control" placeholder="הכנס סיסמה">
                    <button class="toggle-password" onclick="togglePassword('login-password')">👁️</button>
                </div>
            </div>

            <div class="auth-actions">
                <button class="btn-link" onclick="goToScreen('screen-2')">שכחתי שם משתמש או סיסמה (4)</button>
            </div>

            <button class="btn btn-primary" onclick="handleLogin()">התחברות (5)</button>
            <button class="btn btn-secondary" onclick="goToScreen('screen-3')">הירשם (6)</button>
        </div>
    </div>

    <!-- ==================== מסך 2: שכחתי שם משתמש / סיסמה ==================== -->
    <div id="screen-2" class="auth-container hidden">
        <div class="auth-header">
            <div class="app-logo" onclick="goToScreen('screen-1')">OptiFlow AI 🚀</div>
            <span style="font-size: 0.9rem; font-weight: normal;">שחזור פרטי גישה</span>
        </div>
        <div class="auth-body">
            <div class="form-group">
                <label>דואר אלקטרוני לשחזור (7)</label>
                <input type="email" class="form-control" placeholder="user@example.com">
            </div>
            <div class="form-group">
                <label>מספר טלפון (8)</label>
                <input type="tel" class="form-control" placeholder="050-0000000">
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" style="flex: 1;">שלח קוד (9)</button>
                <button class="btn btn-secondary" style="flex: 1;" onclick="goToScreen('screen-1')">ביטול (10)</button>
            </div>
            <button class="btn btn-primary" style="margin-top: 10px;">אישור ושחזור (11)</button>
        </div>
    </div>

    <!-- ==================== מסך 3: הרשמה ==================== -->
    <div id="screen-3" class="auth-container hidden">
        <div class="auth-header">
            <div class="app-logo" onclick="goToScreen('screen-1')">OptiFlow AI 🚀</div>
            <span style="font-size: 0.9rem; font-weight: normal;">הרשמה للمערכת</span>
        </div>
        <div class="auth-body">
            <div class="form-group"><label>שם פרטי (12)</label><input type="text" class="form-control"></div>
            <div class="form-group"><label>שם משפחה (13)</label><input type="text" class="form-control"></div>
            <div class="form-group"><label>דוא"ל (15)</label><input type="email" class="form-control"></div>
            <div class="form-group"><label>טלפון (16)</label><input type="tel" class="form-control"></div>
            <div class="form-group"><label>סיסמה (17)</label><input type="password" class="form-control"></div>
            <button class="btn btn-primary" onclick="goToScreen('screen-main')">סיום הרשמה (18)</button>
            <button class="btn btn-secondary" onclick="goToScreen('screen-1')">חזרה להתחברות</button>
        </div>
    </div>

    <!-- ==================== מסך ראשי לקוח ==================== -->
    <div id="screen-main" class="hidden">
        <!-- Header עליון -->
        <header class="main-header">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span>שלום, רובי | שפה: עברית</span>
            </div>
            <div class="app-logo" onclick="goToScreen('screen-1')">
                OptiFlow AI | מנהל מערכת 🚀 (1)
            </div>
        </header>

        <!-- סרגל כלים -->
        <nav class="main-nav">
            <a href="#">🏠 מסך ראשי</a>
            <a href="#">⚙️ הגדרות מערכת</a>
            <a href="#">📞 צור קשר</a>
        </nav>

        <!-- תוכן מרכזי -->
        <div class="main-layout">

            <!-- צד שמאל: נושאים / עסקים בלחיצה -->
            <div class="card">
                <div class="card-header">
                    📁 נושאים ועסקים קיימים
                </div>
                <div class="card-body topics-list">
                    <div class="topic-item">
                        <h3>נושא / עסק 1</h3>
                        <p style="color: #666; font-size: 0.85rem;">לחץ לצפייה בפרטים וניהול הנושא</p>
                    </div>
                    <div class="topic-item">
                        <h3>נושא / עסק 2</h3>
                        <p style="color: #666; font-size: 0.85rem;">לחץ לצפייה בפרטים וניהול הנושא</p>
                    </div>
                    <div class="topic-item">
                        <h3>נושא / עסק 3</h3>
                        <p style="color: #666; font-size: 0.85rem;">לחץ לצפייה בפרטים וניהול הנושא</p>
                    </div>
                </div>
            </div>

            <!-- צד ימין: קובייה אחת מאוחדת של פרטי לקוח -->
            <div class="card">
                <div class="card-header">
                    👤 פרטי לקוח
                </div>
                <div class="card-body">
                    <h4 style="color: var(--primary); margin-bottom: 8px;">פרטים אישיים</h4>
                    <div class="info-row"><span class="info-label">שם משתמש:</span> <span>רובי</span></div>
                    <div class="info-row"><span class="info-label">סטטוס חשבון:</span> <span>פעיל (מורשה מערכת)</span></div>
                    <div class="info-row"><span class="info-label">תאריך חיבור:</span> <span>מחובר כעת</span></div>
                    <div class="info-row"><span class="info-label">דואר אלקטרוני:</span> <span>user@example.com</span></div>
                    <div class="info-row"><span class="info-label">טלפון נייד:</span> <span>050-0000000</span></div>

                    <h4 style="color: var(--primary); margin-top: 15px; margin-bottom: 8px;">זכאות ותפעול</h4>
                    <div class="info-row"><span class="info-label">סוג מנוי:</span> <span>OptiFlow Enterprise AI</span></div>
                    <div class="info-row"><span class="info-label">מכסת ניתוחים:</span> <span>ללא הגבלה</span></div>
                    <div class="info-row"><span class="info-label">סטטוס שרתים:</span> <span>תקין לקבלה ולעיבוד</span></div>
                </div>
            </div>

            <!-- כפתור יצירת עסק חדש בצד שמאל למטה -->
            <button class="btn-create-business">➕ צור עסק חדש</button>

        </div>
    </div>

    <script>
        // ניווט בין המסכים
        function goToScreen(screenId) {
            const screens = ['screen-1', 'screen-2', 'screen-3', 'screen-main'];
            screens.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.add('hidden');
            });
            document.getElementById(screenId).classList.remove('hidden');
        }

        // צפייה / הסתרת סיסמה
        function togglePassword(inputId) {
            const input = document.getElementById(inputId);
            if (input.type === 'password') {
                input.type = 'text';
            } else {
                input.type = 'password';
            }
        }

        // התחברות למערכת למסך ראשי
        function handleLogin() {
            goToScreen('screen-main');
        }
    </script>
</body>
</html>
