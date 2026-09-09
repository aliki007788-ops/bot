import threading
import requests
import time
import os

def keep_alive():
    """هر ۱۰ دقیقه به سرور ping میزنه تا نخوابه"""
    
    url = os.getenv("APP_URL", "")
    
    if not url:
        print("⚠️ APP_URL تنظیم نشده - keep alive غیرفعال")
        return
    
    url = f"{url}/health"
    print(f"✅ Keep Alive شروع شد → {url}")
    
    while True:
        try:
            time.sleep(600)  # ۱۰ دقیقه
            res = requests.get(url, timeout=10)
            print(f"💓 Ping → {res.status_code}")
        except Exception as e:
            print(f"⚠️ Ping خطا: {e}")

def start_keep_alive():
    """در یه thread جداگانه اجرا میشه"""
    thread = threading.Thread(
        target=keep_alive,
        daemon=True  # با بسته شدن سرور این هم بسته میشه
    )
    thread.start()
