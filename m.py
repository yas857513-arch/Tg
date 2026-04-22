#!/usr/bin/env python3
import socket
import time
import threading
import ipaddress
from flask import Flask
import telebot

# ===== CONFIG =====
TOKEN = "8435736634:AAHht4_qXrW16W9pDLNv3Feb8F3nvrK4G5g"   # ⚠️ replace this
bot = telebot.TeleBot(TOKEN)

# ===== WEB SERVER (RENDER) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running ✅"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# ===== STATE =====
active_users = {}

# ===== TEST FUNCTION =====
def run_test(chat_id, ip, port, duration, rate, msg_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)

    packet = b"ping"
    sent = 0
    start = time.time()

    try:
        while time.time() - start < duration:
            sock.sendto(packet, (ip, port))
            sent += 1

            if sent % max(1, int(rate * 2)) == 0:
                try:
                    bot.edit_message_text(
                        f"🚀 Running...\n\nTarget: {ip}:{port}\nSent: {sent}",
                        chat_id,
                        msg_id
                    )
                except:
                    pass

            time.sleep(1 / rate)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

    finally:
        sock.close()
        active_users.pop(chat_id, None)

    bot.edit_message_text(
        f"✅ Test Finished\n\nTarget: {ip}:{port}\nPackets: {sent}\nAvg PPS: {round(sent/duration,2)}",
        chat_id,
        msg_id
    )

# ===== COMMANDS =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🤖 UDP Test Bot Ready\n\n"
        "Use:\n/test <ip> <port> <time> <rate>\n\n"
        "Example:\n"
        "/test 127.0.0.1 7777 20 2"
    )

@bot.message_handler(commands=['test'])
def test(msg):
    try:
        parts = msg.text.split()

        if len(parts) != 5:
            bot.reply_to(msg, "❌ Usage:\n/test <ip> <port> <time> <rate>")
            return

        ip = parts[1]
        port = int(parts[2])
        duration = int(parts[3])
        rate = float(parts[4])

        # ===== VALIDATION =====
        try:
            ipaddress.ip_address(ip)
        except:
            bot.reply_to(msg, "❌ Invalid IP")
            return

        if rate <= 0 or rate > 10000:
            bot.reply_to(msg, "⚠️ Rate: 1–10 PPS allowed")
            return

        if duration > 606666:
            bot.reply_to(msg, "⚠️ Max duration = 60 sec")
            return

        if msg.chat.id in active_users:
            bot.reply_to(msg, "⚠️ Test already running")
            return

        m = bot.send_message(msg.chat.id, f"🚀 Starting...\n\nTarget: {ip}:{port}")

        active_users[msg.chat.id] = True

        t = threading.Thread(
            target=run_test,
            args=(msg.chat.id, ip, port, duration, rate, m.message_id),
            daemon=True
        )
        t.start()

    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()

    print("Bot running...")
    bot.infinity_polling(skip_pending=True)
