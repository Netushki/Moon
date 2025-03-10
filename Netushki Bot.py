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
    
# Проверяем, что бот упомянут в сообщении, и что сообщение не является ответом на его собственное сообщение
    if bot.user in message.mentions and message.reference is None:
        user_id = message.author.id

        # Если для пользователя уже были использованы все GIF, сбрасываем список
        if user_id in used_gifs and len(used_gifs[user_id]) == len(gif_urls):
            used_gifs[user_id] = []  # Сбросить использованные GIF

        # Выбираем GIF, который еще не был использован этим пользователем
        available_gifs = [gif for gif in gif_urls if gif not in used_gifs.get(user_id, [])]
        gif_url = random.choice(available_gifs)

        # Добавляем выбранный GIF в список использованных
        if user_id not in used_gifs:
            used_gifs[user_id] = []
        used_gifs[user_id].append(gif_url)

        await message.reply(gif_url)

    # Обрабатываем остальные команды только после обработки сообщений
    await bot.process_commands(message)
    
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

    # Обработчик слэш-команды /random
@bot.tree.command(name="random", description="Случайно выбирает между True и False")
@app_commands.describe(question="Вопрос, на который нужно ответить")
async def random_command(interaction: discord.Interaction, question: str = None):
    if question is None:
        question = "Отсутствует"
    response = random.choice(["True", "False"])

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Вопрос", value=question, inline=False)
    embed.add_field(name="Случайный ответ", value=response, inline=False)

    await interaction.response.send_message(embed=embed)

# Обработчик слэш-команды /numbersrange
@bot.tree.command(name="numbersrange", description="Выбирает случайное число в заданном диапазоне")
@app_commands.describe(start="Начало диапазона (целое число)", end="Конец диапазона (целое число)")
async def numbersrange_command(interaction: discord.Interaction, start: int, end: int):
    if start > end:
        await interaction.response.send_message("Ошибка: начало диапазона больше конца. Попробуйте снова.", ephemeral=True)
        return
    
    random_number = random.randint(start, end)

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Диапазон", value=f"{start} - {end}", inline=False)
    embed.add_field(name="Выбранное число", value=str(random_number), inline=False)

    await interaction.response.send_message(embed=embed)

# Обработчик слэш-команды /calculate
@bot.tree.command(name="calculate", description="Решает примеры")
@app_commands.describe(number1="Первое число", operator="Оператор (+, -, *, /)", number2="Второе число")
async def calculate_command(interaction: discord.Interaction, number1: float, operator: str, number2: float):
    try:
        if operator not in ['+', '-', '*', '/']:
            raise ValueError("Неподдерживаемый оператор. Используйте +, -, *, или /")
        
        if operator == '+':
            result = number1 + number2
        elif operator == '-':
            result = number1 - number2
        elif operator == '*':
            result = number1 * number2
        elif operator == '/':
            if number2 == 0:
                raise ZeroDivisionError("Деление на ноль невозможно")
            result = number1 / number2

        if result.is_integer():
            result = int(result)

        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="Пример", value=f"{number1} {operator} {number2}", inline=False)
        embed.add_field(name="Ответ", value=str(result), inline=False)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Ошибка: {e}", ephemeral=True)

# Запуск Flask в отдельном потоке
Thread(target=run_flask).start()

# Запуск бота
bot.run(TOKEN)










