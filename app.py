from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
import json
import os

app = FastAPI(title="Yangi Yil Konkursi")

# Statik fayllar uchun papka
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# O'yinchilar ma'lumotlari
users_db = {
    "admin": {"password": "admin123", "score": 100},
    "test": {"password": "test123", "score": 50}
}

DB_FILE = "users_db.json"

def load_users():
    """Fayldan foydalanuvchilarni yuklash"""
    global users_db
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                users_db = json.load(f)
    except:
        users_db = {}

def save_users():
    """Foydalanuvchilarni faylga saqlash"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, ensure_ascii=False, indent=2)
    except:
        pass

load_users()

# HTML shablonlari
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎄 Yangi Yil Konkursi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial; }
        body { background: linear-gradient(135deg, #0a1931, #1a237e); color: white; min-height: 100vh; }
        .container { max-width: 450px; margin: 0 auto; padding: 20px; }
        .auth-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; margin-top: 50px; }
        .auth-header { text-align: center; margin-bottom: 30px; }
        .auth-logo { font-size: 70px; margin-bottom: 10px; }
        .auth-title { font-size: 28px; font-weight: 800; margin-bottom: 5px; }
        .auth-subtitle { opacity: 0.8; }
        .form-input { width: 100%; padding: 15px; margin: 10px 0; border-radius: 10px; border: 2px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; font-size: 16px; }
        .form-input:focus { outline: none; border-color: #4fc3f7; }
        .btn { width: 100%; padding: 15px; margin: 20px 0 10px 0; border: none; border-radius: 10px; background: linear-gradient(135deg, #1a73e8, #4fc3f7); color: white; font-size: 18px; font-weight: 600; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .message { padding: 10px; border-radius: 10px; margin: 10px 0; text-align: center; }
        .error { background: rgba(255,68,68,0.2); border: 1px solid rgba(255,68,68,0.3); color: #ff4444; }
        .success { background: rgba(0,255,136,0.2); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; }
        .auth-link { text-align: center; margin-top: 20px; }
        .auth-link a { color: #4fc3f7; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">🎅</div>
                <h1 class="auth-title">Yangi Yil Konkursi</h1>
                <p class="auth-subtitle">Hisobingizga kiring</p>
            </div>
            
            {% if error %}
            <div class="message error">{{ error }}</div>
            {% endif %}
            
            <form method="post" action="/login">
                <input type="text" name="username" class="form-input" placeholder="Foydalanuvchi nomi" required>
                <input type="password" name="password" class="form-input" placeholder="Parol" required>
                <button type="submit" class="btn">Kirish</button>
            </form>
            
            <div class="auth-link">
                Hisobingiz yo'qmi? <a href="/register">Ro'yxatdan o'tish</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎄 Ro'yxatdan o'tish</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial; }
        body { background: linear-gradient(135deg, #0a1931, #1a237e); color: white; min-height: 100vh; }
        .container { max-width: 450px; margin: 0 auto; padding: 20px; }
        .auth-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; margin-top: 50px; }
        .auth-header { text-align: center; margin-bottom: 30px; }
        .auth-logo { font-size: 70px; margin-bottom: 10px; }
        .auth-title { font-size: 28px; font-weight: 800; margin-bottom: 5px; }
        .auth-subtitle { opacity: 0.8; }
        .form-input { width: 100%; padding: 15px; margin: 10px 0; border-radius: 10px; border: 2px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; font-size: 16px; }
        .form-input:focus { outline: none; border-color: #4fc3f7; }
        .btn { width: 100%; padding: 15px; margin: 20px 0 10px 0; border: none; border-radius: 10px; background: linear-gradient(135deg, #1a73e8, #4fc3f7); color: white; font-size: 18px; font-weight: 600; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .message { padding: 10px; border-radius: 10px; margin: 10px 0; text-align: center; }
        .error { background: rgba(255,68,68,0.2); border: 1px solid rgba(255,68,68,0.3); color: #ff4444; }
        .success { background: rgba(0,255,136,0.2); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; }
        .auth-link { text-align: center; margin-top: 20px; }
        .auth-link a { color: #4fc3f7; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">📝</div>
                <h1 class="auth-title">Ro'yxatdan o'tish</h1>
                <p class="auth-subtitle">Yangi hisob yarating</p>
            </div>
            
            {% if error %}
            <div class="message error">{{ error }}</div>
            {% endif %}
            
            {% if success %}
            <div class="message success">{{ success }}</div>
            {% endif %}
            
            <form method="post" action="/register">
                <input type="text" name="username" class="form-input" placeholder="Foydalanuvchi nomi" required>
                <input type="password" name="password" class="form-input" placeholder="Parol" required>
                <input type="password" name="confirm_password" class="form-input" placeholder="Parolni takrorlang" required>
                <button type="submit" class="btn">Ro'yxatdan o'tish</button>
            </form>
            
            <div class="auth-link">
                Allaqachon hisobingiz bormi? <a href="/">Kirish</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Utility funksiyalari
def get_countdown():
    """Yangi yilgacha qolgan vaqtni hisoblash"""
    now = datetime.now()
    current_year = now.year
    new_year = datetime(current_year + 1, 1, 1, 0, 0, 0)
    diff = new_year - now
    
    if diff.total_seconds() <= 0:
        return {"days": "00", "hours": "00", "minutes": "00", "seconds": "00"}
    
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
        medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"{i+1}."))
        result.append({
            "rank": i + 1,
            "username": username,
            "score": data.get("score", 0),
            "medal": medal
        })
    
    return result

# Routes
@app.get("/")
async def home(request: Request):
    """Bosh sahifa (kirish)"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=".")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    """Kirish sahifasi"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=".")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    """Kirish"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=".")
    
    if username not in users_db or users_db[username]["password"] != password:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Noto'g'ri foydalanuvchi nomi yoki parol!"
        })
    
    # O'yin sahifasiga yo'naltirish
    response = RedirectResponse(url=f"/game/{username}", status_code=303)
    return response

@app.get("/register")
async def register_page(request: Request):
    """Ro'yxatdan o'tish sahifasi"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=".")
    return templates.TemplateResponse("register.html", {"request": request, "error": None, "success": None})

@app.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Ro'yxatdan o'tish"""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=".")
    
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Parollar mos kelmadi!",
            "success": None
        })
    
    if username in users_db:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Bu foydalanuvchi nomi band!",
            "success": None
        })
    
    users_db[username] = {
        "password": password,
        "score": 0,
        "joined": datetime.now().isoformat()
    }
    save_users()
    
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": None,
        "success": "Ro'yxatdan o'tdingiz! Endi kirishingiz mumkin."
    })

@app.get("/game/{username}")
async def game_page(request: Request, username: str):
    """O'yin sahifasi"""
    if username not in users_db:
        return RedirectResponse(url="/")
    
    countdown = get_countdown()
    top_users = get_top_users(10)
    user_score = users_db[username]["score"]
    
    # Leaderboard HTML yaratish
    leaderboard_html = ""
    for user in top_users:
        is_current = user["username"] == username
        leaderboard_html += f"""
        <div class="leaderboard-item" style="{'background: linear-gradient(90deg, rgba(255,51,102,0.2), rgba(51,204,255,0.2)); border-left: 4px solid #FFCC00;' if is_current else ''}">
            <div style="font-size: 20px; font-weight: 800; width: 40px; text-align: center;">{user['medal']}</div>
            <div style="flex: 1; padding: 0 15px; font-size: 18px; font-weight: 600;">{user['username']} {'⭐' if is_current else ''}</div>
            <div style="font-size: 22px; font-weight: 800; color: #FFCC00;">{user['score']} 🎄</div>
        </div>
        """
    
    if not leaderboard_html:
        leaderboard_html = '<div style="text-align:center; padding:30px; color:rgba(255,255,255,0.5)">Hali hech kim o\'ynamagan</div>'
    
    game_html = f"""
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎄 Yangi Yil Konkursi - {username}</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial; }}
            body {{ background: linear-gradient(135deg, #0a1931, #1a237e); color: white; min-height: 100vh; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 15px; }}
            .navbar {{ display: flex; justify-content: space-around; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 10px; margin-bottom: 20px; }}
            .nav-btn {{ background: transparent; border: none; color: white; padding: 10px 15px; border-radius: 10px; cursor: pointer; display: flex; flex-direction: column; align-items: center; font-size: 12px; }}
            .nav-btn.active {{ background: linear-gradient(135deg, #1a73e8, #4fc3f7); }}
            .page {{ display: none; }}
            .page.active {{ display: block; }}
            .card {{ background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 15px; }}
            .btn {{ background: linear-gradient(135deg, #1a73e8, #4fc3f7); color: white; border: none; padding: 15px; border-radius: 10px; width: 100%; cursor: pointer; margin-top: 20px; font-size: 18px; }}
            .countdown-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; text-align: center; margin: 20px 0; }}
            .countdown-box {{ background: linear-gradient(145deg, rgba(255,51,102,0.9), rgba(51,204,255,0.9)); padding: 15px 10px; border-radius: 10px; }}
            .countdown-value {{ font-size: 32px; font-weight: 900; color: white; }}
            .countdown-label {{ font-size: 14px; color: rgba(255,255,255,0.9); }}
            .tree {{ font-size: 150px; text-align: center; cursor: pointer; margin: 30px 0; animation: float 3s ease-in-out infinite; }}
            @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
            .score {{ font-size: 48px; font-weight: 800; color: #FFCC00; text-align: center; margin: 20px 0; }}
            .prizes-container {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }}
            .prize-item {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; text-align: center; }}
            .prize-medal {{ font-size: 40px; margin-bottom: 5px; }}
            .leaderboard-item {{ display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
            .tap-feedback {{ position: fixed; pointer-events: none; z-index: 1000; font-size: 24px; font-weight: 800; color: #FFCC00; animation: floatUp 1s ease-out forwards; }}
            @keyframes floatUp {{ 0% {{ opacity: 1; transform: translateY(0) scale(1); }} 100% {{ opacity: 0; transform: translateY(-100px) scale(1.5); }} }}
            @keyframes countdownPulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Navbar -->
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
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="font-size: 32px; margin-bottom: 10px;">🎄 Yangi Yil Konkursi 🎄</h1>
                    <div style="font-size: 24px; color: #33CCFF;">Xush kelibsiz, {username}!</div>
                </div>
                
                <div style="text-align: center; margin: 40px 0;">
                    <h3 style="margin-bottom: 20px;">⏳ Yangi Yilgacha:</h3>
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
                    <h3 style="margin-bottom: 15px;"><i class="fas fa-gift"></i> Sovg'alar</h3>
                    <div class="prizes-container">
                        <div class="prize-item">
                            <div class="prize-medal">🥇</div>
                            <div style="color: #FFCC00; font-weight: 700;">50 yulduz</div>
                            <div>1-o'rin</div>
                        </div>
                        <div class="prize-item">
                            <div class="prize-medal">🥈</div>
                            <div style="color: #FFCC00; font-weight: 700;">25 yulduz</div>
                            <div>2-o'rin</div>
                        </div>
                        <div class="prize-item">
                            <div class="prize-medal">🥉</div>
                            <div style="color: #FFCC00; font-weight: 700;">15 yulduz</div>
                            <div>3-o'rin</div>
                        </div>
                    </div>
                </div>
                
                <button class="btn" onclick="showPage('game')">
                    <i class="fas fa-play-circle"></i> O'ynashni boshlash
                </button>
            </div>
            
            <!-- O'yin sahifasi -->
            <div id="game" class="page">
                <div style="text-align: center; margin-bottom: 30px;">
                    <div class="card" style="display: inline-block; padding: 15px 30px;">
                        <div style="font-size: 16px; opacity: 0.9;">Joriy ochko:</div>
                        <div id="score" class="score">{user_score}</div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <h3 style="margin-bottom: 20px; color: #33CCFF;">Archani bosing! ⬇️</h3>
                    <div class="tree" onclick="tapTree()">🎄</div>
                </div>
                
                <button class="btn" onclick="showPage('leaderboard')">
                    <i class="fas fa-trophy"></i> Reytingni ko'rish
                </button>
            </div>
            
            <!-- Leaderboard sahifasi -->
            <div id="leaderboard" class="page">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h1 style="font-size: 28px;">🏆 TOP 10 O'yinchilar</h1>
                </div>
                
                <div class="card">
                    <div id="leaderboard-list">
                        {leaderboard_html}
                    </div>
                </div>
                
                <button class="btn" onclick="showPage('game')">
                    <i class="fas fa-arrow-left"></i> O'yin sahifasiga qaytish
                </button>
            </div>
        </div>
        
        <script>
            let currentUser = '{username}';
            let userScore = {user_score};
            let countdownInterval = null;
            let lastTapTime = 0;
            
            function updateCountdown() {{
                fetch('/api/countdown')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('days').textContent = data.days;
                        document.getElementById('hours').textContent = data.hours;
                        document.getElementById('minutes').textContent = data.minutes;
                        document.getElementById('seconds').textContent = data.seconds;
                    }});
            }}
            
            async function tapTree() {{
                const now = Date.now();
                if (now - lastTapTime < 100) return;
                lastTapTime = now;
                
                const response = await fetch('/api/tap', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
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
                
                setTimeout(() => feedback.remove(), 1000);
                
                // Har 10 ochkoda yangilash
                if (userScore % 10 === 0) {{
                    setTimeout(() => loadLeaderboard(), 500);
                }}
            }}
            
            async function loadLeaderboard() {{
                const response = await fetch('/api/leaderboard');
                const topUsers = await response.json();
                
                let html = '';
                for (const user of topUsers) {{
                    const isCurrent = user.username === currentUser;
                    html += `
                    <div class="leaderboard-item" style="${{isCurrent ? 'background: linear-gradient(90deg, rgba(255,51,102,0.2), rgba(51,204,255,0.2)); border-left: 4px solid #FFCC00;' : ''}}">
                        <div style="font-size: 20px; font-weight: 800; width: 40px; text-align: center;">${{user.medal}}</div>
                        <div style="flex: 1; padding: 0 15px; font-size: 18px; font-weight: 600;">${{user.username}} ${{isCurrent ? '⭐' : ''}}</div>
                        <div style="font-size: 22px; font-weight: 800; color: #FFCC00;">${{user.score}} 🎄</div>
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
                
                if (pageId === 'leaderboard') {{
                    loadLeaderboard();
                }}
            }}
            
            function logout() {{
                window.location.href = '/';
            }}
            
            function animateCountdown(elementId) {{
                const element = document.getElementById(elementId);
                const box = element.closest('.countdown-box');
                box.style.animation = 'countdownPulse 0.5s ease';
                setTimeout(() => box.style.animation = '', 500);
            }}
            
            // Sahifa yuklanganda
            document.addEventListener('DOMContentLoaded', function() {{
                updateCountdown();
                countdownInterval = setInterval(updateCountdown, 1000);
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=game_html)

# API endpoints
@app.get("/api/countdown")
async def api_countdown():
    return get_countdown()

@app.get("/api/leaderboard")
async def api_leaderboard():
    return get_top_users(10)

@app.post("/api/tap")
async def api_tap(request: Request):
    data = await request.json()
    username = data.get("username")
    
    if username not in users_db:
        return {{"error": "Foydalanuvchi topilmadi"}}
    
    users_db[username]["score"] = users_db[username].get("score", 0) + 1
    save_users()
    
    return {{
        "success": True,
        "new_score": users_db[username]["score"],
        "username": username
    }}

# Template fayllarini yaratish
def create_template_files():
    """Template fayllarini yaratish"""
    os.makedirs("templates", exist_ok=True)
    
    # login.html yaratish
    login_template = LOGIN_HTML.replace("{% if error %}", "{{% if error %}}").replace("{% endif %}", "{{% endif %}}")
    with open("templates/login.html", "w", encoding="utf-8") as f:
        f.write(login_template)
    
    # register.html yaratish
    register_template = REGISTER_HTML.replace("{% if error %}", "{{% if error %}}").replace("{% endif %}", "{{% endif %}}").replace("{% if success %}", "{{% if success %}}")
    with open("templates/register.html", "w", encoding="utf-8") as f:
        f.write(register_template)

# Dasturni ishga tushirish
if __name__ == "__main__":
    # Template fayllarini yaratish
    create_template_files()
    
    print("🎄 Yangi Yil Konkursi dasturi ishga tushmoqda...")
    print("🌐 Server http://localhost:8000 manzilida ishlaydi")
    print("\nTest foydalanuvchilar:")
    print("👤 admin | Parol: admin123")
    print("👤 test  | Parol: test123")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
