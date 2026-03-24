from alerts.telegram_alert import send_telegram


def trigger_alert(frame, message):

    print("ALERT:", message)

    send_telegram(message)