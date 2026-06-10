import asyncio
import urllib.request
import urllib.parse
import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
import uvicorn
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import UserStatusOnline
from contextlib import asynccontextmanager

# --- 1. CONFIGURATION ---
# Using os.environ.get allows you to keep keys out of your code entirely.
API_ID = int(os.environ.get('TELEGRAM_API_ID', 0))                           
API_HASH = os.environ.get('TELEGRAM_API_HASH', 'YOUR_API_HASH_HERE') 
TARGET_USERNAME = os.environ.get('TARGET_USERNAME', '@YOUR_TARGET_USERNAME')                
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE') 
MY_CHAT_ID = os.environ.get('MY_CHAT_ID', 'YOUR_CHAT_ID_HERE') 

SESSION_STRING = os.environ.get('TELEGRAM_SESSION', '')

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  status TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def log_event(status):
    conn = sqlite3.connect('tracker.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO history (status, timestamp) VALUES (?, ?)", (status, timestamp))
    conn.commit()
    conn.close()

def get_recent_history(limit=50):
    try:
        conn = sqlite3.connect('tracker.db')
        c = conn.cursor()
        c.execute("SELECT status, timestamp FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"event": r[0], "time": r[1]} for r in rows]
    except Exception:
        return []

# --- 3. TELEGRAM CLIENT & STATE ---
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient('session_tracker', API_ID, API_HASH)

app_state = {
    "is_running": False,
    "target": TARGET_USERNAME,
    "current_status": "offline"
}

def send_telegram_notification(text):
    # Don't try to send if placeholders are still present
    if "YOUR_BOT_TOKEN" in BOT_TOKEN or "YOUR_CHAT_ID" in MY_CHAT_ID:
        print("[!] Notification skipped: Placeholders detected.")
        return
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={MY_CHAT_ID}&text={encoded_text}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"Failed to send bot notification: {e}")

# --- 4. ACTIVE POLLING BACKGROUND TASK ---
async def active_tracker_loop():
    """Forces Telegram to give us the status every 15 seconds"""
    print(f"[*] Started Active Polling for {TARGET_USERNAME}...")
    
    while app_state["is_running"]:
        try:
            # Prevent execution if configuration is missing
            if API_ID == 0 or "YOUR" in TARGET_USERNAME:
                print("[!] Polling paused: Please configure your environment variables.")
                await asyncio.sleep(60)
                continue

            entity = await client.get_entity(TARGET_USERNAME)
            is_currently_online = isinstance(entity.status, UserStatusOnline)
            
            if is_currently_online and app_state["current_status"] != "online":
                app_state["current_status"] = "online"
                log_event("online")
                msg = f"🔔 {TARGET_USERNAME} is now ONLINE!"
                send_telegram_notification(msg)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ALERT: User went Online.")
                
            elif not is_currently_online and app_state["current_status"] != "offline":
                app_state["current_status"] = "offline"
                log_event("offline")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ALERT: User went Offline.")
                
        except Exception as e:
            print(f"[!] Polling Error: {e}")
            
        await asyncio.sleep(15)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    if API_ID == 0:
        print("\n[!] WARNING: Running with default placeholders. Update your configuration.")
        yield
        return

    await client.connect()
    
    if not await client.is_user_authorized():
        print("\n[!] FATAL: Client unauthorized. Provide a valid TELEGRAM_SESSION.")
    else:
        app_state["is_running"] = True
        asyncio.create_task(active_tracker_loop())

    yield
    
    app_state["is_running"] = False
    await client.disconnect()

# --- 5. FASTAPI ROUTES ---
app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def intercept_head_requests(request: Request, call_next):
    if request.method == "HEAD":
        return Response(status_code=200)
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found.</h1>", status_code=404)

@app.get("/ping")
async def ping_server():
    return {"status": "alive", "time": datetime.now().isoformat()}

@app.get("/api/status")
async def get_status():
    response_data = app_state.copy()
    response_data["history"] = get_recent_history()
    return response_data

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="warning")
