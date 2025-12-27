from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Yangi Yil Konkursi API", version="1.0.0")

# Ma'lumotlarni saqlash uchun oddiy lug'atlar
users_db = {}  # Foydalanuvchilar ma'lumotlari
leaderboard_data = []  # Reyting ma'lumotlari

# Saqlash fayli
DATA_FILE = "data.json"

# Modellar
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserScore(BaseModel):
    username: str
    score: int

# Ma'lumotlarni yuklash
def load_data():
    global users_db, leaderboard_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users_db = data.get('users', {})
                leaderboard_data = data.get('leaderboard', [])
    except Exception as e:
        print(f"Ma'lumotlarni yuklashda xatolik: {e}")

# Ma'lumotlarni saqlash
def save_data():
    try:
        data = {
            'users': users_db,
            'leaderboard': leaderboard_data,
            'last_updated': datetime.now().isoformat()
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ma'lumotlarni saqlashda xatolik: {e}")

# HTML sahifani qaytarish
@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Yangi Yil Konkursi API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #0F1A30, #2D1B69);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-top: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 {
                color: #FF3366;
                text-align: center;
            }
            h2 {
                color: #33CCFF;
                border-bottom: 2px solid #33CCFF;
                padding-bottom: 10px;
            }
            .endpoint {
                background: rgba(255, 255, 255, 0.15);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid #FFCC00;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #4CAF50; }
            .post { background: #2196F3; }
            .put { background: #FF9800; }
            code {
                background: rgba(0, 0, 0, 0.3);
                padding: 2px 5px;
                border-radius: 3px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-top: 30px;
            }
            .stat-box {
                background: linear-gradient(135deg, #FF3366, #33CCFF);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>🎄 Yangi Yil Konkursi API 🎄</h1>
        <div class="container">
            <h2>API Endpointlar</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/register</strong>
                <p>Yangi foydalanuvchi ro'yxatdan o'tkazish</p>
                <code>{ "username": "string", "password": "string" }</code>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/login</strong>
                <p>Foydalanuvchi tizimga kirishi</p>
                <code>{ "username": "string", "password": "string" }</code>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/users</strong>
                <p>Barcha foydalanuvchilar ro'yxati</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/user/{username}</strong>
                <p>Foydalanuvchi ma'lumotlari</p>
            </div>
            
            <div class="endpoint">
                <span class="method put">PUT</span>
                <strong>/update_score</strong>
                <p>Foydalanuvchi ochkosini yangilash</p>
                <code>{ "username": "string", "score": integer }</code>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/leaderboard</strong>
                <p>Reyting jadvali (TOP 10)</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/game_page</strong>
                <p>O'yin sahifasini olish (HTML)</p>
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>👥 Foydalanuvchilar</h3>
                    <p id="userCount">0</p>
                </div>
                <div class="stat-box">
                    <h3>🏆 Eng yuqori ochko</h3>
                    <p id="topScore">0</p>
                </div>
            </div>
        </div>
        
        <script>
            async function loadStats() {
                try {
                    const usersRes = await fetch('/users');
                    const users = await usersRes.json();
                    document.getElementById('userCount').textContent = users.length;
                    
                    if (users.length > 0) {
                        const topUser = users.reduce((max, user) => 
                            user.score > max.score ? user : max
                        );
                        document.getElementById('topScore').textContent = 
                            `${topUser.score} (${topUser.username})`;
                    }
                } catch (error) {
                    console.error('Statistika yuklashda xatolik:', error);
                }
            }
            
            loadStats();
        </script>
    </body>
    </html>
    """

# O'yin sahifasini qaytarish (asl HTML kod)
@app.get("/game_page", response_class=HTMLResponse)
async def get_game_page():
    html_content = """
    <!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>🎅 Yangi Yil Konkursi 2025</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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

        /* Snow Animation */
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

        /* Container */
        .container {
            max-width: 100%;
            width: 100%;
            margin: 0 auto;
            padding: 15px;
            position: relative;
            z-index: 2;
        }

        /* Auth Pages */
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

        /* Form Elements */
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

        /* Buttons */
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

        /* Link */
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

        /* App Pages */
        #app-page {
            display: none;
            animation: fadeIn 0.8s ease-out;
        }

        /* Navbar */
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

        /* Pages */
        .page {
            display: none;
            animation: slideIn 0.5s ease-out;
        }

        .page.active {
            display: block;
        }

        /* Cards */
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

        /* Welcome Section */
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

        /* Countdown - YANGILANGAN */
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

        /* Countdown uchun animatsiya */
        @keyframes countdownPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .countdown-animation {
            animation: countdownPulse 0.5s ease;
        }

        /* Prizes */
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

        /* Game Page */
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

        /* Xabar uchun konteyner - O'CHIRILDI */
        /* .message-container {
            min-height: 60px;
            margin: 20px 0;
            text-align: center;
        } */

        /* YANGI: Bosilganda chiqadigan xabar */
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

        /* Leaderboard */
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

        /* Current User Highlight */
        .current-user {
            background: linear-gradient(90deg, rgba(255, 51, 102, 0.25), rgba(51, 204, 255, 0.25));
            border-radius: 15px;
            border-left: 4px solid var(--accent);
        }

        /* Animations */
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

        @keyframes glow {
            0%, 100% { filter: drop-shadow(0 0 10px rgba(255, 204, 0, 0.7)); }
            50% { filter: drop-shadow(0 0 20px rgba(255, 204, 0, 1)); }
        }

        /* Responsive */
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

        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: var(--secondary);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Effects */
        .sparkle {
            position: absolute;
            width: 10px;
            height: 10px;
            background: white;
            border-radius: 50%;
            pointer-events: none;
            opacity: 0;
            animation: sparkle 0.5s ease-out;
        }

        @keyframes sparkle {
            0% { transform: scale(0); opacity: 1; }
            100% { transform: scale(1); opacity: 0; }
        }

        /* Confetti */
        .confetti {
            position: fixed;
            width: 10px;
            height: 10px;
            pointer-events: none;
            opacity: 0;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <!-- Qor effekti -->
    <div class="snow" id="snow"></div>

    <!-- Ro'yxatdan o'tish sahifasi -->
    <div id="register-page" class="auth-container" style="display:none;">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">🎅</div>
                <h1 class="auth-title">Yangi Yil Konkursi</h1>
                <p class="auth-subtitle">Qatnashing va yutib oling!</p>
            </div>
            
            <div class="input-group">
                <i class="input-icon fas fa-user"></i>
                <input type="text" id="reg-username" class="form-input" placeholder="Foydalanuvchi nomi" required>
            </div>
            
            <div class="input-group">
                <i class="input-icon fas fa-lock"></i>
                <input type="password" id="reg-password" class="form-input" placeholder="Parol" required>
            </div>
            
            <button class="btn btn-primary" onclick="register()">
                <i class="btn-icon fas fa-user-plus"></i>
                Ro'yxatdan o'tish
            </button>
            
            <div id="register-message" class="auth-link" style="margin-top:15px;"></div>
            
            <div class="auth-link">
                Allaqachon hisobingiz bormi? 
                <a href="#" onclick="showLogin()">Kirish</a>
            </div>
        </div>
    </div>

    <!-- Kirish sahifasi -->
    <div id="login-page" class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="auth-logo">🔑</div>
                <h1 class="auth-title">Hisobingizga kiring</h1>
                <p class="auth-subtitle">O'yinni davom ettiring</p>
            </div>
            
            <div class="input-group">
                <i class="input-icon fas fa-user"></i>
                <input type="text" id="login-username" class="form-input" placeholder="Foydalanuvchi nomi" required>
            </div>
            
            <div class="input-group">
                <i class="input-icon fas fa-lock"></i>
                <input type="password" id="login-password" class="form-input" placeholder="Parol" required>
            </div>
            
            <button class="btn btn-primary" onclick="login()">
                <i class="btn-icon fas fa-sign-in-alt"></i>
                Kirish
            </button>
            
            <div id="login-message" class="auth-link" style="margin-top:15px;"></div>
            
            <div class="auth-link">
                Hisobingiz yo'qmi? 
                <a href="#" onclick="showRegister()">Ro'yxatdan o'tish</a>
            </div>
        </div>
    </div>

    <!-- Asosiy app sahifasi -->
    <div id="app-page" class="container">
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
            <div class="welcome-section">
                <h1 class="welcome-title">🎄 Yangi Yil Konkursi 🎄</h1>
                <div class="welcome-user" id="welcome"></div>
            </div>

            <!-- Countdown -->
            <div class="countdown-container">
                <h2 class="countdown-title">⏳ Yangi Yilgacha qoldi:</h2>
                <div class="countdown-grid">
                    <div class="countdown-box" onclick="animateCountdown('days')">
                        <div id="days" class="countdown-value">00</div>
                        <div class="countdown-label">Kun</div>
                    </div>
                    <div class="countdown-box" onclick="animateCountdown('hours')">
                        <div id="hours" class="countdown-value">00</div>
                        <div class="countdown-label">Soat</div>
                    </div>
                    <div class="countdown-box" onclick="animateCountdown('minutes')">
                        <div id="minutes" class="countdown-value">00</div>
                        <div class="countdown-label">Minut</div>
                    </div>
                    <div class="countdown-box" onclick="animateCountdown('seconds')">
                        <div id="seconds" class="countdown-value">00</div>
                        <div class="countdown-label">Sekund</div>
                    </div>
                </div>
            </div>

            <!-- Sovg'alar -->
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
                    <div class="score-value" id="score">0</div>
                </div>
            </div>

            <div class="tree-container">
                <div class="christmas-tree" onclick="tapTree(event)">🎄</div>
                <div class="tap-instruction">Archani bosing! ⬆️</div>
            </div>

            <!-- Xabar konteyneri O'CHIRILDI -->

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
                <div id="leaderboard-list" class="leaderboard-list"></div>
            </div>

            <button class="btn btn-primary" onclick="showPage('game')">
                <i class="fas fa-arrow-left"></i>
                O'yin sahifasiga qaytish
            </button>
        </div>
    </div>

    <script>
        // API URL - o'zgartirilgan
        const API_BASE_URL = window.location.origin;
        
        // Global o'zgaruvchilar
        let currentUser = null;
        let countdownInterval = null;
        let snowInterval = null;
        let lastTapTime = 0;
        const tapDelay = 100; // 100ms delay between taps

        // Qor effekti yaratish
        function createSnow() {
            const snow = document.getElementById('snow');
            snow.innerHTML = '';
            
            for (let i = 0; i < 50; i++) {
                const snowflake = document.createElement('div');
                snowflake.classList.add('snowflake');
                
                const size = Math.random() * 5 + 3;
                const left = Math.random() * 100;
                const opacity = Math.random() * 0.6 + 0.4;
                const duration = Math.random() * 10 + 10;
                
                snowflake.style.width = `${size}px`;
                snowflake.style.height = `${size}px`;
                snowflake.style.left = `${left}%`;
                snowflake.style.opacity = opacity;
                snowflake.style.animationDuration = `${duration}s`;
                snowflake.style.animationDelay = `${Math.random() * 5}s`;
                
                snow.appendChild(snowflake);
            }
        }

        // Chayqalish effekti
        function createSparkle(x, y) {
            const sparkle = document.createElement('div');
            sparkle.classList.add('sparkle');
            sparkle.style.left = `${x}px`;
            sparkle.style.top = `${y}px`;
            
            document.body.appendChild(sparkle);
            
            setTimeout(() => {
                sparkle.remove();
            }, 500);
        }

        // YANGI: Bosilganda chiqadigan xabar
        function createTapFeedback(x, y, text) {
            const feedback = document.createElement('div');
            feedback.classList.add('tap-feedback');
            feedback.textContent = text;
            feedback.style.left = `${x}px`;
            feedback.style.top = `${y}px`;
            
            document.body.appendChild(feedback);
            
            setTimeout(() => {
                feedback.remove();
            }, 1000);
        }

        // Confetti effekti
        function createConfetti() {
            const colors = ['#FF3366', '#33CCFF', '#FFCC00', '#00D4A4', '#FF9966'];
            
            for (let i = 0; i < 30; i++) {
                const confetti = document.createElement('div');
                confetti.classList.add('confetti');
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.left = `${Math.random() * 100}vw`;
                confetti.style.top = `-10px`;
                
                const size = Math.random() * 10 + 5;
                confetti.style.width = `${size}px`;
                confetti.style.height = `${size}px`;
                confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
                
                document.body.appendChild(confetti);
                
                // Animatsiya
                const animation = confetti.animate([
                    { transform: `translateY(0) rotate(0deg)`, opacity: 1 },
                    { transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
                ], {
                    duration: Math.random() * 2000 + 1000,
                    easing: 'cubic-bezier(0.215, 0.610, 0.355, 1)'
                });
                
                animation.onfinish = () => confetti.remove();
            }
        }

        // YANGI: Countdown animatsiyasi
        function animateCountdown(elementId) {
            const element = document.getElementById(elementId);
            const box = element.closest('.countdown-box');
            
            // Animatsiya qo'shish
            box.classList.add('countdown-animation');
            
            // Animatsiyani tozalash
            setTimeout(() => {
                box.classList.remove('countdown-animation');
            }, 500);
            
            // Ovoz effekti (agar ruxsat bo'lsa)
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (e) {
                console.log('Audio context not supported');
            }
        }

        // Sahifalarni ko'rsatish
        function showRegister() {
            document.getElementById('login-page').style.display = 'none';
            document.getElementById('register-page').style.display = 'flex';
            document.getElementById('app-page').style.display = 'none';
        }

        function showLogin() {
            document.getElementById('register-page').style.display = 'none';
            document.getElementById('login-page').style.display = 'flex';
            document.getElementById('app-page').style.display = 'none';
        }

        // Ro'yxatdan o'tish (API orqali)
        async function register() {
            const username = document.getElementById('reg-username').value.trim();
            const password = document.getElementById('reg-password').value.trim();
            const message = document.getElementById('register-message');
            
            if (!username || !password) {
                showMessage(message, 'Iltimos, barcha maydonlarni to\'ldiring', 'error');
                return;
            }
            
            if (username.length < 3) {
                showMessage(message, 'Username kamida 3 belgidan iborat bo\'lishi kerak', 'error');
                return;
            }
            
            if (password.length < 4) {
                showMessage(message, 'Parol kamida 4 belgidan iborat bo\'lishi kerak', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/register`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMessage(message, '✅ Ro\'yxatdan o\'tdingiz! Endi kirishingiz mumkin', 'success');
                    createConfetti();
                    
                    setTimeout(() => {
                        showLogin();
                        document.getElementById('login-username').value = username;
                        document.getElementById('reg-username').value = '';
                        document.getElementById('reg-password').value = '';
                        message.innerHTML = '';
                    }, 2000);
                } else {
                    showMessage(message, data.detail || 'Xatolik yuz berdi', 'error');
                }
            } catch (error) {
                showMessage(message, 'Server bilan bog\'lanishda xatolik', 'error');
            }
        }

        // Kirish (API orqali)
        async function login() {
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value.trim();
            const message = document.getElementById('login-message');
            
            if (!username || !password) {
                showMessage(message, 'Iltimos, barcha maydonlarni to\'ldiring', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    currentUser = username;
                    
                    document.getElementById('login-page').style.display = 'none';
                    document.getElementById('register-page').style.display = 'none';
                    document.getElementById('app-page').style.display = 'block';
                    document.getElementById('welcome').innerHTML = `🎉 Xush kelibsiz, <span style="color:#33CCFF">${username}</span>!`;
                    
                    // Effektlarni boshlash
                    startCountdown();
                    updateUserData();
                    loadLeaderboard();
                    createConfetti();
                    
                    message.innerHTML = '';
                    document.getElementById('login-username').value = '';
                    document.getElementById('login-password').value = '';
                } else {
                    showMessage(message, data.detail || 'Noto\'g\'ri username yoki parol', 'error');
                }
            } catch (error) {
                showMessage(message, 'Server bilan bog\'lanishda xatolik', 'error');
            }
        }

        // Xabar ko'rsatish
        function showMessage(element, text, type) {
            element.innerHTML = `<span style="color:${type === 'error' ? '#FF3366' : '#00D4A4'}; font-weight:600;">${text}</span>`;
        }

        // App sahifalarni ko'rsatish
        function showPage(pageId) {
            // Sahifalarni yashirish
            document.querySelectorAll('.page').forEach(page => {
                page.style.display = 'none';
                page.classList.remove('active');
            });
            
            // Navbarni yangilash
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Tanlangan sahifani ko'rsatish
            document.getElementById(pageId).style.display = 'block';
            document.getElementById(pageId).classList.add('active');
            
            // Tanlangan tugmani faollashtirish
            const activeBtn = Array.from(document.querySelectorAll('.nav-btn')).find(btn => 
                btn.textContent.includes(pageId === 'main' ? 'Asosiy' : 
                                       pageId === 'game' ? 'O\'yin' : 
                                       pageId === 'leaderboard' ? 'Reyting' : '')
            );
            if (activeBtn) activeBtn.classList.add('active');
            
            // Sahifa o'zgarishida qo'shimcha amallar
            if (pageId === 'game') {
                updateUserData();
            } else if (pageId === 'leaderboard') {
                loadLeaderboard();
            }
        }

        // User ma'lumotlarini yangilash (API orqali)
        async function updateUserData() {
            if (!currentUser) return;
            
            try {
                const response = await fetch(`${API_BASE_URL}/user/${currentUser}`);
                if (response.ok) {
                    const user = await response.json();
                    document.getElementById('score').textContent = user.score || 0;
                }
            } catch (error) {
                console.error('Foydalanuvchi ma\'lumotlarini yuklashda xatolik:', error);
            }
        }

        // Archani bosish - API orqali yangilash
        async function tapTree(event) {
            // Anti-spam: har 100ms dan keyin bitta bosish
            const now = Date.now();
            if (now - lastTapTime < tapDelay) return;
            lastTapTime = now;
            
            if (!currentUser) return;
            
            try {
                // Avval joriy ochkoni olish
                const userResponse = await fetch(`${API_BASE_URL}/user/${currentUser}`);
                if (!userResponse.ok) return;
                
                const user = await userResponse.json();
                const newScore = (user.score || 0) + 1;
                
                // Ochkoni yangilash
                const updateResponse = await fetch(`${API_BASE_URL}/update_score`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: currentUser,
                        score: newScore
                    })
                });
                
                if (updateResponse.ok) {
                    // Yangilash
                    document.getElementById('score').textContent = newScore;
                    
                    // Effektlar yaratish
                    if (event) {
                        const x = event.clientX || event.touches[0].clientX;
                        const y = event.clientY || event.touches[0].clientY;
                        
                        createSparkle(x, y);
                        
                        // YANGI: Bosilganda chiqadigan xabarlar
                        const messages = ["🎉", "🌟", "✨", "🎄", "⛄", "🎁", "🔥", "💫"];
                        const randomMsg = messages[Math.floor(Math.random() * messages.length)];
                        createTapFeedback(x - 20, y - 50, randomMsg);
                    }
                    
                    // Har 10 ochkoda confetti
                    if (newScore % 10 === 0) {
                        createConfetti();
                    }
                }
            } catch (error) {
                console.error('Ochkoni yangilashda xatolik:', error);
            }
        }

        // Leaderboard yuklash (API orqali)
        async function loadLeaderboard() {
            try {
                const response = await fetch(`${API_BASE_URL}/leaderboard`);
                if (!response.ok) return;
                
                const leaderboard = await response.json();
                let html = '';
                
                if (leaderboard.length === 0) {
                    html = '<div style="text-align:center; padding:30px; color:rgba(255,255,255,0.5)">Hali hech kim o\'ynamagan</div>';
                } else {
                    leaderboard.forEach((user, index) => {
                        const isCurrent = user.username === currentUser;
                        const medal = index === 0 ? '🥇' : 
                                     index === 1 ? '🥈' : 
                                     index === 2 ? '🥉' : 
                                     `${index + 1}.`;
                        
                        html += `
                            <div class="leaderboard-item ${isCurrent ? 'current-user' : ''}">
                                <div class="leaderboard-rank">${medal}</div>
                                <div class="leaderboard-user">${user.username} ${isCurrent ? '⭐' : ''}</div>
                                <div class="leaderboard-score">${user.score || 0} 🎄</div>
                            </div>
                        `;
                    });
                }
                
                document.getElementById('leaderboard-list').innerHTML = html;
            } catch (error) {
                console.error('Leaderboard yuklashda xatolik:', error);
            }
        }

        // Countdown
        function startCountdown() {
            function updateCountdown() {
                const now = new Date();
                const uzTime = new Date(now.getTime() + (5 * 60 * 60 * 1000));
                const nextYear = uzTime.getUTCFullYear() + 1;
                const newYearDate = new Date(Date.UTC(nextYear, 0, 1, 0, 0, 0));
                const diff = newYearDate - uzTime;
                
                if (diff <= 0) {
                    document.getElementById('days').textContent = '00';
                    document.getElementById('hours').textContent = '00';
                    document.getElementById('minutes').textContent = '00';
                    document.getElementById('seconds').textContent = '00';
                    
                    // Yangi yil tabriki
                    if (document.getElementById('main').classList.contains('active')) {
                        document.querySelector('.welcome-title').innerHTML = '🎉 YANGI YIL MUBORAK! 🎉';
                        document.querySelector('.countdown-title').textContent = '🎉 Yangi Yil Keldi! 🎉';
                    }
                    return;
                }
                
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
                const minutes = Math.floor((diff / (1000 * 60)) % 60);
                const seconds = Math.floor((diff / 1000) % 60);
                
                document.getElementById('days').textContent = days.toString().padStart(2, '0');
                document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
                document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
                document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
            }
            
            updateCountdown();
            
            if (countdownInterval) {
                clearInterval(countdownInterval);
            }
            
            countdownInterval = setInterval(updateCountdown, 1000);
        }

        // Chiqish
        function logout() {
            currentUser = null;
            document.getElementById('app-page').style.display = 'none';
            document.getElementById('login-page').style.display = 'flex';
            
            if (countdownInterval) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
        }

        // Sahifa yuklanganda
        window.onload = function() {
            // Boshlang'ich sahifa sifatida kirish sahifasi ko'rsatilsin
            showLogin();
            createSnow();
            
            // Qorni yangilash
            if (snowInterval) clearInterval(snowInterval);
            snowInterval = setInterval(createSnow, 30000);
            
            // Telefon uchun optimallashtirish
            if ('ontouchstart' in window) {
                document.querySelector('.christmas-tree').style.cursor = 'pointer';
            }
            
            // Countdown boxlarga hover effekti
            document.querySelectorAll('.countdown-box').forEach(box => {
                box.addEventListener('touchstart', function() {
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                });
                
                box.addEventListener('touchend', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
        };

        // Ekran o'lchami o'zgarganda
        window.addEventListener('resize', createSnow);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# API Endpointlari
@app.post("/register")
async def register_user(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Bu username band, boshqa nom tanlang")
    
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username kamida 3 belgidan iborat bo'lishi kerak")
    
    if len(user.password) < 4:
        raise HTTPException(status_code=400, detail="Parol kamida 4 belgidan iborat bo'lishi kerak")
    
    users_db[user.username] = {
        "password": user.password,
        "score": 0,
        "joined": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }
    
    # Leaderboard ni yangilash
    update_leaderboard(user.username, 0)
    
    save_data()
    return {"message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi", "username": user.username}

@app.post("/login")
async def login_user(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    if users_db[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Noto'g'ri parol")
    
    # Oxirgi faollik vaqtini yangilash
    users_db[user.username]["last_active"] = datetime.now().isoformat()
    save_data()
    
    return {"message": "Kirish muvaffaqiyatli", "username": user.username}

@app.get("/users")
async def get_all_users():
    users_list = []
    for username, data in users_db.items():
        users_list.append({
            "username": username,
            "score": data.get("score", 0),
            "joined": data.get("joined"),
            "last_active": data.get("last_active")
        })
    return users_list

@app.get("/user/{username}")
async def get_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    return {
        "username": username,
        "score": users_db[username].get("score", 0),
        "joined": users_db[username].get("joined"),
        "last_active": users_db[username].get("last_active")
    }

@app.put("/update_score")
async def update_user_score(user_score: UserScore):
    if user_score.username not in users_db:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    
    # Eski ochkoni saqlab qo'yish
    old_score = users_db[user_score.username].get("score", 0)
    
    # Agar yangi ochko eski ochkodan kichik bo'lsa, yangilamaymiz
    if user_score.score < old_score:
        raise HTTPException(status_code=400, detail="Yangi ochko eski ochkodan kichik bo'lishi mumkin emas")
    
    users_db[user_score.username]["score"] = user_score.score
    users_db[user_score.username]["last_active"] = datetime.now().isoformat()
    
    # Leaderboard ni yangilash
    update_leaderboard(user_score.username, user_score.score)
    
    save_data()
    return {"message": "Ochko muvaffaqiyatli yangilandi", "username": user_score.username, "score": user_score.score}

@app.get("/leaderboard")
async def get_leaderboard():
    # Leaderboard ma'lumotlarini tayyorlash
    leaderboard = []
    for username, data in users_db.items():
        leaderboard.append({
            "username": username,
            "score": data.get("score", 0),
            "joined": data.get("joined")
        })
    
    # Ochko bo'yicha kamayish tartibida saralash
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    
    # Faqat TOP 10 ni qaytarish
    return leaderboard[:10]

# Leaderboard ni yangilash funksiyasi
def update_leaderboard(username: str, score: int):
    global leaderboard_data
    
    # Mavjud foydalanuvchini topish
    user_index = -1
    for i, user in enumerate(leaderboard_data):
        if user["username"] == username:
            user_index = i
            break
    
    # Yangi foydalanuvchi qo'shish yoki yangilash
    user_data = {
        "username": username,
        "score": score,
        "updated": datetime.now().isoformat()
    }
    
    if user_index >= 0:
        leaderboard_data[user_index] = user_data
    else:
        leaderboard_data.append(user_data)
    
    # Ochko bo'yicha saralash
    leaderboard_data.sort(key=lambda x: x["score"], reverse=True)
    
    # Faqat 10 ta eng yaxshisini saqlash
    leaderboard_data = leaderboard_data[:10]

# Ilova ishga tushganda ma'lumotlarni yuklash
@app.on_event("startup")
async def startup_event():
    load_data()
    print("Yangi Yil Konkursi API ishga tushdi!")
    print(f"Jami foydalanuvchilar: {len(users_db)}")
    print(f"API hujjatlariga kirish: http://localhost:8000/docs")
    print(f"O'yin sahifasi: http://localhost:8000/game_page")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
