import requests

BOT_TOKEN = "8719369445:AAHUE6TjKY-3pada4fX47FCSASPauE7IFR8"
CHAT_ID = "6434359737"

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": str(message)
    }

    response = requests.post(url, data=data)

    print(response.text)