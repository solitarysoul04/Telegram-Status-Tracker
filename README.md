# Telgram Status tracker 📡

An asynchronous, event-driven web dashboard and background monitoring service that tracks the online/offline status of a target Telegram user in real-time. Built with **FastAPI**, **Telethon**, and a beautiful, high-fidelity dark-themed dashboard using **TailwindCSS**.

The service works by performing optimized background polling of the target's entity status on Telegram servers, logs state changes to a local SQLite database, and dispatches instant push notifications via a Telegram Bot directly to your personal chat.

---

# ✨ Features

- 🕒 **Real-Time Web Dashboard:** Minimalist, sleek UI with live clock, status badges, and dynamic visual indicators.
- 🗄️ **Persistent Event History:** Automatically tracks, logs, and dates every online/offline transition using a lightweight SQLite database.
- 🔔 **Instant Telegram Notifications:** Dispatches automated structural updates directly to your chat using the official Telegram Bot API.
- ⚡ **Fully Asynchronous Lifecycle:** Built completely on non-blocking Python code (`asyncio`, `FastAPI`, `Telethon`) ensuring optimal hardware utilization.
- ☁️ **Cloud Native Design:** Decoupled config utilizing environment variables, fully compatible with modern PaaS providers like Render.

---

## 🏗️ Repository Architecture

Your repository should be structured as follows:

```
├── main.py                # Core FastAPI application & Telethon polling engine
├── index.html             # High-fidelity dashboard frontend layout
├── generate_session.py    # Independent utility to generate authorization strings
├── requirements.txt       # App dependencies and framework configurations
├── .gitignore             # Git rule exclusions file (crucial for credential safety)
└── .env                   # Template explaining required configurations

```

---

## 🔐 Setup & Key Procurement Guide

To successfully bind this tracker to the Telegram ecosystem, you need to gather 4 distinct configuration parameters.

### 1. Telegram Developer Credentials (`API_ID` & `API_HASH`)

These credentials authorize a user-level application layer to authenticate queries.

1. Head to [my.telegram.org](https://my.telegram.org/) and log in with your primary Telegram phone number.
2. Navigate to **API development tools**.
3. Create a new application profile (Fill out a dummy title and short name).
4. Copy the unique **App api_id** (integer) and **App api_hash** (32-character string).

### 2. Notification Channel Engine (`BOT_TOKEN`)

The system dispatches system alerts via a standalone bot token.

1. Launch Telegram and search for the verified account **@BotFather**.
2. Initialize a session and send the command: `/newbot`.
3. Complete the initialization steps by giving your bot a name and a unique username ending in `_bot`.
4. Securely copy the generated **HTTP API Token** (formatted as `numbers:characters`).

### 3. Personal Communication Pathway (`MY_CHAT_ID`)

The unique identifier marking your personal chat space so the bot knows exactly where to route updates.

1. Search for **@userinfobot** or **@IDBot** in your Telegram app search bar.
2. Send any arbitrary text message to the bot (e.g., `/start`).
3. The bot will return your numerical user account ID (e.g., `123456789`). Copy this value.

---

## 🔑 Generating the Telegram Session String

Cloud providers like Render feature ephemeral filesystems and run purely headless, meaning you cannot log into your Telegram account interactively (via phone code verification) in production. We solve this by compiling authentication details down to a flat text string locally.

1. Ensure all system dependencies are installed:
```bash
pip install -r requirements.txt

```


2. Open your local copy of `generate_session.py` and replace the placeholder fields with your personal `api_id` and `api_hash`:
```python
api_id = 12345678  # Replace with your actual numerical API ID
api_hash = 'your_32_char_api_hash_here'

```


3. Execute the script from your terminal:
```bash
python generate_session.py

```


4. Enter your Telegram phone number (including country code) and the numeric login passcode sent to your device.
5. The console will print a long alpha-numeric string. **Copy this entire string.** This is your `TELEGRAM_SESSION` key and acts as your persistent cloud passport.

---

## 💻 Local Workspace Deployment

1. **Clone your workspace:**
```bash
git clone [https://github.com/your-username/telegram-tracker.git](https://github.com/your-username/telegram-tracker.git)
cd telegram-tracker

```


2. **Configure Local Environment Context:**
Create a hidden `.env` file in your project root using the configuration below:
```env
TELEGRAM_API_ID = 12345678
TELEGRAM_API_HASH = your_actual_api_hash_string
TARGET_USERNAME = @username_you_want_to_track
BOT_TOKEN = your_bot_father_token_string
MY_CHAT_ID = your_numerical_chat_id
TELEGRAM_SESSION = your_long_generated_string_session_from_step_above
PORT = 8000

```


3. **Boot the Engine:**
```bash
python main.py

```


4. Open your browser and navigate to `http://localhost:8000` to visualize the tracking matrix dashboard.

---

## ☁️ Continuous Production Deployment (Render)

This application is meticulously configured to align directly with [Render's](https://render.com/) architecture as a continuous production deployment.

1. Sign up/Log in to the **Render Dashboard**.
2. Click **New +** and select **Web Service**.
3. Connect your target GitHub repository containing these finalized scripts.
4. Fill out the service provisioning blueprint exactly as follows:
* **Name:** `telegram-tracker-service`
* **Runtime:** `Python 3`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`


5. Click on the **Advanced** drop-down menu and add your production environment variables (Render automatically abstracts away the local `.env` requirements):
* `TELEGRAM_API_ID`
* `TELEGRAM_API_HASH`
* `TARGET_USERNAME`
* `BOT_TOKEN`
* `MY_CHAT_ID`
* `TELEGRAM_SESSION`


6. Click **Create Web Service**. Render will securely clone, isolate, build, and host your service.

---

## ⏰ 24/7 Monitoring Stability via UptimeRobot

Render's free tier automatically suspends (spins down) runtime containers after 15 consecutive minutes of web inactivity. When the container sleeps, your background Telegram tracker loop stops running. To preserve round-the-clock telemetry, you must constantly keep the container awake.

1. Create a free account at [UptimeRobot](https://uptimerobot.com/).
2. Navigate to your dashboard and select **Add New Monitor**.
3. Configure the monitor setup fields:
* **Monitor Type:** `HTTP(s)`
* **Friendly Name:** `Telegram Tracker Continuous Pulse`
* **URL (or IP):** Paste your public Render web service deployment URL appended with the application's verification endpoint (e.g., `https://telegram-tracker-service.onrender.com/ping`).
* **Monitoring Interval:** Set it to check every `5 minutes`.


4. Save the configuration.

UptimeRobot will now systematically target your `/ping` endpoint every 5 minutes, tricking Render's container lifecycle manager into keeping your active background thread awake 24/7/365.

---

## ⚠️ Disclaimer & Legality

This repository is built explicitly as an open-source educational exploration of event-driven programming architectures and personal OSINT network telemetry. Users assume all structural risks and operational responsibilities. Always make sure your tracking use-cases respect personal boundaries and fully align with the Telegram Terms of Service.
