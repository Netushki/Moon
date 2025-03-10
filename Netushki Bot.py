import discord
import random  # Для генерации случайных значений
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask
import re

# Настройки Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

# Запуск Flask в отдельном потоке
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

# Настройки бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv('TOKEN')

# ID каналов
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344388680953106512  # Канал скриншотов

# Функция для поиска чисел в тексте
def find_numbers(text):
    return [int(num) for num in re.findall(r'\b\d+\b', text)]  # Ищет все числа в тексте

# Словарь для отслеживания использованных GIF
used_gifs = {}

# Список возможных GIF
gif_urls = [
    "https://cdn.discordapp.com/attachments/1346943612373569557/1347573414142939279/attachment.gif",
    "https://cdn.discordapp.com/attachments/1322781202851041358/1347037669388980274/attachment.gif",
    "https://cdn.discordapp.com/attachments/1309799105756790794/1309909672446398534/speechmemified_Half_Life_Deathmatch_Source.jpg.gif",
    "https://tenor.com/view/speech-bubble-gif-26412022",
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif"
]

# Обработчик сообщений в разных каналах
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Проверка сообщений в канале считалки
    if message.channel.id == COUNTING_CHANNEL_ID:
        numbers_in_message = find_numbers(message.content)
        if not numbers_in_message:
            await message.delete()
            warning = await message.channel.send(
                f"{message.author.mention}, твоё сообщение должно содержать число больше прошлого на 1, не нарушай цепочку!"
            )
            await warning.delete(delay=3)
            return

    # Проверка сообщений в канале для скриншотов
    if message.channel.id == SCREENSHOT_CHANNEL_ID:
        if not message.attachments:
            await message.delete()
            warning = await message.channel.send(
                f"{message.author.mention}, ты должен отправить скриншот предыдущего сообщения, не нарушай цепочку!"
            )
            await warning.delete(delay=3)
            return

    await bot.process_commands(message)

# Запуск Flask в отдельном потоке
Thread(target=run_flask).start()

# Запуск бота
bot.run(TOKEN)










