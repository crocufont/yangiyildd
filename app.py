from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Yangi Yil Konkursi")

# Templates konfiguratsiyasi
templates = Jinja2Templates(directory="templates")

# Statik fayllar uchun papka (agar kerak bo'lsa)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# O'yinchilar ma'lumotlari (vaqtinchalik xotirada)
users_db = {
    "admin": {"password": "admin123", "score": 100, "joined": "2024-01-01"},
    "test": {"password": "test123", "score": 50, "joined": "2024-12-01"}
}

# Saqlash uchun JSON fayl
DB_FILE = "users_db.json"

def load_users():
    """Fayldan foydalanuvchilarni yuklash"""
    global users_db
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                users_db = json.load(f)
    except Exception as e:
        print(f"Fayl yuklashda xato: {e}")
        users_db = {}

def save_users():
    """Foydalanuvchilarni faylga saqlash"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Fayl saqlashda xato: {e}")

# Dasturni ishga tushirganda ma'lumotlarni yuklash
load_users()

# Yangi yil sanasini hisoblash
def get_new_year_date():
    now = datetime.now()
    current_year = now.year
    # Agar yangi yil o'tib bo'lsa, keyingi yilni olish
    if now.month == 1 and now.day == 1:
        return datetime(current_year + 1, 1, 1, 0, 0, 0)
    return datetime(current_year + 1, 1, 1, 0, 0, 0)

def get_countdown():
    """Yangi yilgacha qolgan vaqtni hisoblash"""
    new_year = get_new_year_date()
    now = datetime.now()
    diff = new_year - now
    
    if diff.total_seconds() <= 0:
        return {"days": 0, "hours": 0, "minutes": 0, "seconds": 0}
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    seconds = diff.seconds % 60
    
    return {
        "days": str(days).zfill(2),
        "hours": str(hours).zfill(2),
        "minutes": str(minutes).zfill(2),
        "seconds": str(seconds).zfill(2)
    }

def get_top_users(limit=10):
    """Eng yaxshi o'yinchilarni olish"""
    sorted_users = sorted(
        users_db.items(),
        key=lambda x: x[1].get("score", 0),
        reverse=True
    )[:limit]
    
    result = []
    for i, (username, data) in enumerate(sorted_users):
        result.append({
            "rank": i + 1,
            "username": username,
            "score": data.get("score", 0),
            "medal": "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"{i+1}."))
        })
    
    return result

# HTML sahifasi (bitta faylda)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🎅 Yangi Yil Konkursi 2025</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    <style>
        :root {
            --primary: #FF3366;
            --secondary: #33CCFF;
            --accent: #FFCC00;
            --dark: #0F1A30;
            --light: #F8F9FF;
            --success: #00D4A4;
            --warning: #FF9966;
            --glass: rgba(255, 255, 255, 0.15);
            --glass-dark: rgba(15, 26, 48, 0.85);
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            --gradient: linear-gradient(135deg, var(--primary), var(--secondary));
            --gradient-alt: linear-gradient(135deg, var(--accent), var(--warning));
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--dark);
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(255, 51, 102, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(51, 204, 255, 0.2) 0%, transparent 50%),
                url('https://images.unsplash.com/photo-1454789476662-53eb23ba5907?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }

        .snow {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .snowflake {
            position: absolute;
            background: white;
            border-radius: 50%;
            opacity: 0.8;
            animation: fall linear infinite;
        }

        @keyframes fall {
            to {
                transform: translateY(100vh);
            }
        }

        .container {
            max-width: 100%;
            width: 100%;
            margin: 0 auto;
            padding: 15px;
            position: relative;
            z-index: 2;
        }

        .auth-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            animation: fadeIn 0.8s ease-out;
        }

        .auth-card {
            background: var(--glass-dark);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px 25px;
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: var(--shadow);
            animation: slideUp 0.6s ease-out;
        }

        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .auth-logo {
            font-size: 60px;
            margin-bottom: 15px;
            display: block;
            animation: bounce 2s infinite;
        }

        .auth-title {
            font-size: 28px;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .auth-subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 16px;
        }

        .input-group {
            position: relative;
            margin-bottom: 20px;
        }

        .input-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--secondary);
            font-size: 18px;
        }

        .form-input {
            width: 100%;
            padding: 18px 20px 18px 55px;
            border: 2px solid rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--secondary);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 3px rgba(51, 204, 255, 0.3);
        }

        .form-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            padding: 18px;
            border: none;
            border-radius: 15px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .btn-primary {
            background: var(--gradient);
            color: white;
            box-shadow: 0 5px 15px rgba(255, 51, 102, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(255, 51, 102, 0.5);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.25);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.35);
        }

        .btn-icon {
            font-size: 20px;
        }

        .auth-link {
            text-align: center;
            margin-top: 25px;
            color: rgba(255, 255, 255, 0.7);
        }

        .auth-link a {
            color: var(--secondary);
            text-decoration: none;
            font-weight: 600;
        }

        .auth-link a:hover {
            text-decoration: underline;
        }

        .message {
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: center;
            font-weight: 600;
        }

        .error-message {
            background: rgba(255, 51, 102, 0.2);
            color: #FF3366;
            border: 1px solid rgba(255, 51, 102, 0.3);
        }

        .success-message {
            background: rgba(0, 212, 164, 0.2);
            color: #00D4A4;
            border: 1px solid rgba(0, 212, 164, 0.3);
        }

        #app-page {
            display: none;
            animation: fadeIn 0.8s ease-out;
        }

        .navbar {
            display: flex;
            justify-content: space-around;
            background: var(--glass-dark);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            position: sticky;
            top: 10px;
            z-index: 100;
        }

        .nav-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            padding: 12px 10px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
            min-width: 70px;
        }

        .nav-btn i {
            font-size: 20px;
        }

        .nav-btn.active {
            background: var(--gradient);
            color: white;
            box-shadow: 0 5px 15px rgba(255, 51, 102, 0.4);
            transform: scale(1.05);
        }

        .page {
            display: none;
            animation: slideIn 0.5s ease-out;
        }

        .page.active {
            display: block;
        }

        .card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: var(--shadow);
            animation: fadeInUp 0.6s ease-out;
        }

        .card-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-title i {
            color: var(--accent);
        }

        .welcome-section {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
        }

        .welcome-title {
            font-size: 32px;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            animation: pulse 2s infinite;
        }

        .welcome-user {
            font-size: 24px;
            color: var(--light);
            font-weight: 600;
        }

        .countdown-container {
            text-align: center;
            margin: 40px 0;
        }

        .countdown-title {
            font-size: 24px;
            margin-bottom: 25px;
            color: var(--light);
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .countdown-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }

        .countdown-box {
            background: linear-gradient(145deg, rgba(255, 51, 102, 0.9), rgba(51, 204, 255, 0.9));
            border-radius: 15px;
            padding: 20px 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }

        .countdown-box:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .countdown-box:active {
            transform: translateY(-5px) scale(1.02);
        }

        .countdown-value {
            font-size: 36px;
            font-weight: 900;
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 2;
        }

        .countdown-label {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            position: relative;
            z-index: 2;
        }

        @keyframes countdownPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .countdown-animation {
            animation: countdownPulse 0.5s ease;
        }

        .prizes-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }

        .prize-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px 15px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .prize-item:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .prize-medal {
            font-size: 40px;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 10px rgba(255, 204, 0, 0.5));
        }

        .prize-stars {
            font-size: 20px;
            color: var(--accent);
            font-weight: 700;
        }

        .game-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .score-container {
            display: inline-block;
            background: var(--gradient);
            padding: 15px 30px;
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(255, 51, 102, 0.4);
        }

        .score-label {
            font-size: 16px;
            opacity: 0.9;
        }

        .score-value {
            font-size: 48px;
            font-weight: 800;
        }

        .tree-container {
            text-align: center;
            margin: 40px 0;
            perspective: 1000px;
        }

        .christmas-tree {
            font-size: 150px;
            cursor: pointer;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(0, 255, 157, 0.5));
            transition: transform 0.1s ease;
            user-select: none;
        }

        .christmas-tree:active {
            transform: scale(0.9) rotate(5deg);
            filter: drop-shadow(0 0 30px rgba(0, 255, 157, 0.8));
        }

        .tap-instruction {
            color: var(--secondary);
            font-size: 18px;
            margin-top: 15px;
            animation: blink 2s infinite;
            font-weight: 600;
        }

        .tap-feedback {
            position: fixed;
            pointer-events: none;
            z-index: 1000;
            font-size: 24px;
            font-weight: 800;
            color: var(--accent);
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            animation: floatUp 1s ease-out forwards;
        }

        @keyframes floatUp {
            0% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
            100% {
                opacity: 0;
                transform: translateY(-100px) scale(1.5);
            }
        }

        .leaderboard-header {
            text-align: center;
            margin-bottom: 25px;
        }

        .leaderboard-title {
            font-size: 28px;
            font-weight: 800;
            background: var(--gradient-alt);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .leaderboard-list {
            background: var(--glass-dark);
            border-radius: 20px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .leaderboard-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.3s ease;
        }

        .leaderboard-item:last-child {
            border-bottom: none;
        }

        .leaderboard-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(5px);
        }

        .leaderboard-rank {
            font-size: 20px;
            font-weight: 800;
            width: 40px;
            text-align: center;
        }

        .leaderboard-user {
            flex: 1;
            padding: 0 15px;
            font-size: 18px;
            font-weight: 600;
        }

        .leaderboard-score {
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
        }

        .current-user {
            background: linear-gradient(90deg, rgba(255, 51, 102, 0.25), rgba(51, 204, 255, 0.25));
            border-radius: 15px;
            border-left: 4px solid var(--accent);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        @keyframes slideIn {
            from { transform: translateX(20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes fadeInUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        @media (max-width: 480px) {
            .container {
                padding: 10px;
            }
            
            .auth-card {
                padding: 25px 20px;
                margin: 10px;
            }
            
            .auth-logo {
                font-size: 50px;
            }
            
            .auth-title {
                font-size: 24px;
            }
            
            .countdown-value {
                font-size: 32px;
            }
            
            .countdown-box {
                padding: 15px 8px;
            }
            
            .christmas-tree {
                font-size: 130px;
            }
            
            .score-value {
                font-size: 40px;
            }
            
            .navbar {
                padding: 8px;
            }
            
            .nav-btn {
                min-width: 60px;
                padding: 10px 5px;
                font-size: 11px;
            }
            
            .nav-btn i {
                font-size: 18px;
            }
            
            .prizes-container {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .countdown-grid {
                gap: 10px;
            }
            
            .welcome-title {
                font-size: 28px;
            }
        }

        @media (min-width: 768px) {
            .container {
                max-width: 750px;
            }
            
            .countdown-value {
                font-size: 42px;
            }
            
            .christmas-tree {
                font-size: 180px;
            }
        }
    </style>
</head>
<body>
    <!-- Qor effekti -->
    <div class="snow" id="snow"></div>

    <!-- Kirish sahifasi -->
    <div id="login-page" class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">🔑</div>
                <h1 class="auth-title">Yangi Yil Konkursi</h1>
                <p class="auth-subtitle">Hisobingizga kiring</p>
            </div>
            
            {% if login_error %}
            <div class="message error-message">
                {{ login_error }}
            </div>
            {% endif %}
            
            {% if login_success %}
            <div class="message success-message">
                {{ login_success }}
            </div>
            {% endif %}
            
            <form action="/login" method="post">
                <div class="input-group">
                    <i class="input-icon fas fa-user"></i>
                    <input type="text" name="username" class="form-input" placeholder="Foydalanuvchi nomi" required>
                </div>
                
                <div class="input-group">
                    <i class="input-icon fas fa-lock"></i>
                    <input type="password" name="password" class="form-input" placeholder="Parol" required>
                </div>
                
                <button type="submit" class="btn btn-primary">
                    <i class="btn-icon fas fa-sign-in-alt"></i>
                    Kirish
                </button>
            </form>
            
            <div class="auth-link">
                Hisobingiz yo'qmi? 
                <a href="/register">Ro'yxatdan o'tish</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Bosh sahifa (kirish sahifasi)"""
    return HTMLResponse(content=HTML_TEMPLATE)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Ro'yxatdan o'tish sahifasi"""
    register_html = """
    <!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🎅 Yangi Yil Konkursi - Ro'yxatdan o'tish</title>
    <style>
        :root {
            --primary: #FF3366;
            --secondary: #33CCFF;
            --accent: #FFCC00;
            --dark: #0F1A30;
            --light: #F8F9FF;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--dark);
            color: var(--light);
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(255, 51, 102, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(51, 204, 255, 0.2) 0%, transparent 50%);
        }
        
        .auth-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 30px;
            width: 100%;
            max-width: 450px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .auth-logo {
            font-size: 60px;
            margin-bottom: 15px;
            display: block;
        }
        
        .auth-title {
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .auth-subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 16px;
        }
        
        .form-input {
            width: 100%;
            padding: 15px 20px;
            margin: 10px 0;
            border: 2px solid rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--secondary);
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            margin: 20px 0 10px 0;
            border: none;
            border-radius: 15px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-3px);
        }
        
        .message {
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .error-message {
            background: rgba(255, 51, 102, 0.2);
            color: #FF3366;
            border: 1px solid rgba(255, 51, 102, 0.3);
        }
        
        .success-message {
            background: rgba(0, 212, 164, 0.2);
            color: #00D4A4;
            border: 1px solid rgba(0, 212, 164, 0.3);
        }
        
        .auth-link {
            text-align: center;
            margin-top: 20px;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .auth-link a {
            color: var(--secondary);
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="auth-header">
            <div class="auth-logo">🎅</div>
            <h1 class="auth-title">Ro'yxatdan o'tish</h1>
            <p class="auth-subtitle">Yangi hisob yarating</p>
        </div>
        
        {% if error %}
        <div class="message error-message">
            {{ error }}
        </div>
        {% endif %}
        
        {% if success %}
        <div class="message success-message">
            {{ success }}
        </div>
        {% endif %}
        
        <form action="/register" method="post">
            <input type="text" name="username" class="form-input" placeholder="Foydalanuvchi nomi" required>
            <input type="password" name="password" class="form-input" placeholder="Parol" required>
            <input type="password" name="confirm_password" class="form-input" placeholder="Parolni takrorlang" required>
            <button type="submit" class="btn">Ro'yxatdan o'tish</button>
        </form>
        
        <div class="auth-link">
            Allaqachon hisobingiz bormi? 
            <a href="/">Kirish</a>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=register_html)

@app.post("/register")
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Ro'yxatdan o'tish"""
    if password != confirm_password:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial; background: #0F1A30; color: white; padding: 20px; }}
                .error {{ background: rgba(255,51,102,0.2); padding: 15px; border-radius: 10px; margin: 20px; }}
                a {{ color: #33CCFF; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">⚠️ Parollar mos kelmadi!</div>
            <p><a href="/register">← Ortga qaytish</a></p>
        </body>
        </html>
        """)
    
    if username in users_db:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial; background: #0F1A30; color: white; padding: 20px; }}
                .error {{ background: rgba(255,51,102,0.2); padding: 15px; border-radius: 10px; margin: 20px; }}
                a {{ color: #33CCFF; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">⚠️ Bu foydalanuvchi nomi band!</div>
            <p><a href="/register">← Ortga qaytish</a></p>
        </body>
        </html>
        """)
    
    users_db[username] = {
        "password": password,
        "score": 0,
        "joined": datetime.now().isoformat()
    }
    save_users()
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background: #0F1A30; color: white; padding: 20px; text-align: center; }}
            .success {{ background: rgba(0,212,164,0.2); padding: 15px; border-radius: 10px; margin: 20px; }}
            a {{ color: #33CCFF; text-decoration: none; font-weight: bold; }}
            .container {{ max-width: 500px; margin: 50px auto; }}
        </style>
        <meta http-equiv="refresh" content="3;url=/" />
    </head>
    <body>
        <div class="container">
            <div style="font-size: 60px; margin: 20px;">🎉</div>
            <div class="success">✅ Ro'yxatdan o'tdingiz! 3 soniyadan so'ng kirish sahifasiga yo'naltirilmoqdasiz...</div>
            <p><a href="/">Kirish sahifasiga o'tish</a></p>
        </div>
    </body>
    </html>
    """)

@app.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Kirish"""
    if username not in users_db or users_db[username]["password"] != password:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial; background: #0F1A30; color: white; padding: 20px; }}
                .error {{ background: rgba(255,51,102,0.2); padding: 15px; border-radius: 10px; margin: 20px; }}
                a {{ color: #33CCFF; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">⚠️ Noto'g'ri foydalanuvchi nomi yoki parol!</div>
            <p><a href="/">← Ortga qaytish</a></p>
        </body>
        </html>
        """)
    
    # Asosiy sahifani qaytarish
    return get_main_page(username)

def get_main_page(username: str):
    """Asosiy o'yin sahifasini qaytarish"""
    countdown = get_countdown()
    top_users = get_top_users(10)
    user_score = users_db[username]["score"]
    
    leaderboard_html = ""
    for user in top_users:
        is_current = user["username"] == username
        leaderboard_html += f"""
        <div class="leaderboard-item {'current-user' if is_current else ''}">
            <div class="leaderboard-rank">{user['medal']}</div>
            <div class="leaderboard-user">{user['username']} {'⭐' if is_current else ''}</div>
            <div class="leaderboard-score">{user['score']} 🎄</div>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>🎅 Yangi Yil Konkursi - {username}</title>
        <script>
            let currentUser = '{username}';
            let userScore = {user_score};
            let countdownInterval = null;
            
            function createSnow() {{
                const snow = document.getElementById('snow');
                snow.innerHTML = '';
                
                for (let i = 0; i < 50; i++) {{
                    const snowflake = document.createElement('div');
                    snowflake.classList.add('snowflake');
                    
                    const size = Math.random() * 5 + 3;
                    const left = Math.random() * 100;
                    const opacity = Math.random() * 0.6 + 0.4;
                    const duration = Math.random() * 10 + 10;
                    
                    snowflake.style.width = `${{size}}px`;
                    snowflake.style.height = `${{size}}px`;
                    snowflake.style.left = `${{left}}%`;
                    snowflake.style.opacity = opacity;
                    snowflake.style.animationDuration = `${{duration}}s`;
                    snowflake.style.animationDelay = `${{Math.random() * 5}}s`;
                    
                    snow.appendChild(snowflake);
                }}
            }}
            
            function updateCountdown() {{
                const days = document.getElementById('days');
                const hours = document.getElementById('hours');
                const minutes = document.getElementById('minutes');
                const seconds = document.getElementById('seconds');
                
                // Python serverdan yangi ma'lumot olish
                fetch('/api/countdown')
                    .then(response => response.json())
                    .then(data => {{
                        days.textContent = data.days;
                        hours.textContent = data.hours;
                        minutes.textContent = data.minutes;
                        seconds.textContent = data.seconds;
                    }});
            }}
            
            async function tapTree() {{
                // Serverga ochko yuborish
                const response = await fetch('/api/tap', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{username: currentUser}})
                }});
                
                const data = await response.json();
                userScore = data.new_score;
                document.getElementById('score').textContent = userScore;
                
                // Xabar effekti
                const messages = ["🎉", "🌟", "✨", "🎄", "⛄", "🎁", "🔥", "💫"];
                const randomMsg = messages[Math.floor(Math.random() * messages.length)];
                
                const feedback = document.createElement('div');
                feedback.classList.add('tap-feedback');
                feedback.textContent = randomMsg;
                feedback.style.left = '50%';
                feedback.style.top = '50%';
                document.body.appendChild(feedback);
                
                setTimeout(() => {{
                    feedback.remove();
                }}, 1000);
                
                // Har 10 ochkoda yangilash
                if (userScore % 10 === 0) {{
                    setTimeout(() => {{
                        loadLeaderboard();
                    }}, 500);
                }}
            }}
            
            async function loadLeaderboard() {{
                const response = await fetch('/api/leaderboard');
                const topUsers = await response.json();
                
                let html = '';
                for (const user of topUsers) {{
                    const isCurrent = user.username === currentUser;
                    html += `
                    <div class="leaderboard-item ${{isCurrent ? 'current-user' : ''}}">
                        <div class="leaderboard-rank">${{user.medal}}</div>
                        <div class="leaderboard-user">${{user.username}} ${{isCurrent ? '⭐' : ''}}</div>
                        <div class="leaderboard-score">${{user.score}} 🎄</div>
                    </div>
                    `;
                }}
                
                document.getElementById('leaderboard-list').innerHTML = html;
            }}
            
            function showPage(pageId) {{
                // Sahifalarni yashirish
                document.querySelectorAll('.page').forEach(page => {{
                    page.style.display = 'none';
                    page.classList.remove('active');
                }});
                
                // Navbarni yangilash
                document.querySelectorAll('.nav-btn').forEach(btn => {{
                    btn.classList.remove('active');
                }});
                
                // Tanlangan sahifani ko'rsatish
                document.getElementById(pageId).style.display = 'block';
                document.getElementById(pageId).classList.add('active');
                
                // Tanlangan tugmani faollashtirish
                const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(btn => 
                    btn.textContent.includes(pageId === 'main' ? 'Asosiy' : 
                                           pageId === 'game' ? 'O\\'yin' : 
                                           pageId === 'leaderboard' ? 'Reyting' : '')
                );
                if (activeBtn) activeBtn.classList.add('active');
                
                if (pageId === 'game') {{
                    document.getElementById('score').textContent = userScore;
                }} else if (pageId === 'leaderboard') {{
                    loadLeaderboard();
                }}
            }}
            
            function logout() {{
                window.location.href = '/';
            }}
            
            function animateCountdown(elementId) {{
                const element = document.getElementById(elementId);
                const box = element.closest('.countdown-box');
                
                box.classList.add('countdown-animation');
                
                setTimeout(() => {{
                    box.classList.remove('countdown-animation');
                }}, 500);
            }}
            
            // Sahifa yuklanganda
            document.addEventListener('DOMContentLoaded', function() {{
                createSnow();
                updateCountdown();
                
                countdownInterval = setInterval(updateCountdown, 1000);
                
                setInterval(createSnow, 30000);
            }});
        </script>
        <style>
            /* Yuqoridagi CSS kodlar */
        </style>
    </head>
    <body>
        <div class="snow" id="snow"></div>
        
        <div id="app-page" class="container">
            <nav class="navbar">
                <button class="nav-btn active" onclick="showPage('main')">
                    <i class="fas fa-home"></i>
                    Asosiy
                </button>
                <button class="nav-btn" onclick="showPage('game')">
                    <i class="fas fa-gamepad"></i>
                    O'yin
                </button>
                <button class="nav-btn" onclick="showPage('leaderboard')">
                    <i class="fas fa-trophy"></i>
                    Reyting
                </button>
                <button class="nav-btn" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i>
                    Chiqish
                </button>
            </nav>
            
            <!-- Asosiy sahifa -->
            <div id="main" class="page active">
                <div class="welcome-section">
                    <h1 class="welcome-title">🎄 Yangi Yil Konkursi 🎄</h1>
                    <div class="welcome-user">🎉 Xush kelibsiz, <span style="color:#33CCFF">{username}</span>!</div>
                </div>
                
                <div class="countdown-container">
                    <h2 class="countdown-title">⏳ Yangi Yilgacha qoldi:</h2>
                    <div class="countdown-grid">
                        <div class="countdown-box" onclick="animateCountdown('days')">
                            <div id="days" class="countdown-value">{countdown['days']}</div>
                            <div class="countdown-label">Kun</div>
                        </div>
                        <div class="countdown-box" onclick="animateCountdown('hours')">
                            <div id="hours" class="countdown-value">{countdown['hours']}</div>
                            <div class="countdown-label">Soat</div>
                        </div>
                        <div class="countdown-box" onclick="animateCountdown('minutes')">
                            <div id="minutes" class="countdown-value">{countdown['minutes']}</div>
                            <div class="countdown-label">Minut</div>
                        </div>
                        <div class="countdown-box" onclick="animateCountdown('seconds')">
                            <div id="seconds" class="countdown-value">{countdown['seconds']}</div>
                            <div class="countdown-label">Sekund</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2 class="card-title"><i class="fas fa-gift"></i> Sovg'alar</h2>
                    <div class="prizes-container">
                        <div class="prize-item">
                            <div class="prize-medal">🥇</div>
                            <div class="prize-stars">50 yulduz</div>
                            <div>1-o'rin</div>
                        </div>
                        <div class="prize-item">
                            <div class="prize-medal">🥈</div>
                            <div class="prize-stars">25 yulduz</div>
                            <div>2-o'rin</div>
                        </div>
                        <div class="prize-item">
                            <div class="prize-medal">🥉</div>
                            <div class="prize-stars">15 yulduz</div>
                            <div>3-o'rin</div>
                        </div>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="showPage('game')">
                    <i class="fas fa-play-circle"></i>
                    O'ynashni boshlash
                </button>
            </div>
            
            <!-- O'yin sahifasi -->
            <div id="game" class="page">
                <div class="game-header">
                    <div class="score-container">
                        <div class="score-label">Joriy ochko:</div>
                        <div class="score-value" id="score">{user_score}</div>
                    </div>
                </div>
                
                <div class="tree-container">
                    <div class="christmas-tree" onclick="tapTree()">🎄</div>
                    <div class="tap-instruction">Archani bosing! ⬆️</div>
                </div>
                
                <button class="btn btn-secondary" onclick="showPage('leaderboard')">
                    <i class="fas fa-trophy"></i>
                    Reytingni ko'rish
                </button>
            </div>
            
            <!-- Leaderboard sahifasi -->
            <div id="leaderboard" class="page">
                <div class="leaderboard-header">
                    <h1 class="leaderboard-title">🏆 TOP 10 O'yinchilar</h1>
                </div>
                
                <div class="card">
                    <div id="leaderboard-list" class="leaderboard-list">
                        {leaderboard_html}
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="showPage('game')">
                    <i class="fas fa-arrow-left"></i>
                    O'yin sahifasiga qaytish
                </button>
            </div>
        </div>
        
        <script>
            // FontAwesome iconlar uchun
            if (!document.querySelector('script[src*="fontawesome"]')) {{
                const faScript = document.createElement('script');
                faScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js';
                document.head.appendChild(faScript);
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# API endpoints
@app.get("/api/countdown")
async def api_countdown():
    """Countdown ma'lumotlari"""
    return get_countdown()

@app.get("/api/leaderboard")
async def api_leaderboard():
    """Leaderboard ma'lumotlari"""
    return get_top_users(10)

@app.post("/api/tap")
async def api_tap(request: Request):
    """Archani bosish"""
    data = await request.json()
    username = data.get("username")
    
    if username not in users_db:
        return {"error": "Foydalanuvchi topilmadi"}
    
    users_db[username]["score"] = users_db[username].get("score", 0) + 1
    save_users()
    
    return {
        "success": True,
        "new_score": users_db[username]["score"],
        "username": username
    }

@app.get("/api/user/{username}")
async def api_user(username: str):
    """Foydalanuvchi ma'lumotlari"""
    if username not in users_db:
        return {"error": "Foydalanuvchi topilmadi"}
    
    return {
        "username": username,
        "score": users_db[username].get("score", 0),
        "joined": users_db[username].get("joined", "")
    }

if __name__ == "__main__":
    print("🎄 Yangi Yil Konkursi dasturi ishga tushmoqda...")
    print("🌐 Server http://localhost:8000 manzilida ishlaydi")
    print("📱 Telefonda kirish uchun: http://<kompyuter-ip>:8000")
    print("\nMavjud test foydalanuvchilar:")
    print("👤 admin | Parol: admin123")
    print("👤 test  | Parol: test123")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
