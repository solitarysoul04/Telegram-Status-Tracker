from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 12345678 # Your API ID
api_hash = 'your_32_char_api_hash_here' # Your Hash

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n--- COPY THIS SESSION STRING ---")
    print(client.session.save())
    print("--------------------------------")
