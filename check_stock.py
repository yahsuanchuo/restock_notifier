import json
import os
import requests
from bs4 import BeautifulSoup

IN_STOCK_TEXT = "カートに入れる"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def check_stock(url: str) -> bool:
    """回傳 True 表示有庫存"""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return IN_STOCK_TEXT in soup.get_text()


def send_telegram(message: str):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
        timeout=10,
    )


def main():
    with open("products.json", encoding="utf-8") as f:
        products = json.load(f)

    restocked = []

    for product in products:
        name = product["name"]
        url = product["url"]
        try:
            in_stock = check_stock(url)
            status = "有庫存" if in_stock else "缺貨"
            print(f"[{status}] {name}")
            if in_stock:
                restocked.append((name, url))
        except Exception as e:
            print(f"[錯誤] {name}: {e}")

    if restocked:
        lines = ["【補貨通知】"]
        for name, url in restocked:
            lines.append(f"\n✅ {name}")
            lines.append(url)
        send_telegram("\n".join(lines))
        print(f"\n已發送通知，共 {len(restocked)} 件商品補貨")
    else:
        print("\n無補貨商品，不發送通知")


if __name__ == "__main__":
    main()
