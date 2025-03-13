import discord
import random
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
import re
import threading
import asyncio

# Создание Flask-приложения
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Настройки бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Функция для запуска Flask в отдельном потоке
def run_flask():
    app.run(host="0.0.0.0", port=10000)

TOKEN = os.getenv('TOKEN')

# ID каналов
COUNTING_CHANNEL_ID = 1344299177386967120  # Канал считалки
SCREENSHOT_CHANNEL_ID = 1344388680953106512  # Канал скриншотов

# Функция для поиска чисел в тексте
def find_numbers(text):
    return [int(num) for num in re.findall(r'\b\d+\b', text)]  # Ищет все числа в тексте

# GIF ответом на упоминание
gif_urls = [
    "https://cdn.discordapp.com/attachments/1346943612373569557/1347573414142939279/attachment.gif",
    "https://cdn.discordapp.com/attachments/1322781202851041358/1347037669388980274/attachment.gif",
    "https://cdn.discordapp.com/attachments/1309799105756790794/1309909672446398534/speechmemified_Half_Life_Deathmatch_Source.jpg.gif",
    "https://tenor.com/view/speech-bubble-gif-26412022",
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367007401115658/attachment.gif?ex=67d12e62&is=67cfdce2&hm=d861e9b134d390a39f71e529b60826e826b3bb9f883c89e6cb200865904cf2cf&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348366855894470697/attachment.gif?ex=67d12e3d&is=67cfdcbd&hm=0de0bb1905b43201f1a9d79a698a2c89bfb0bf4d09da89cad9095a0bba63e612&",
    "https://cdn.jacher.io/f3ac073b88487e1b.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367459392159744/attachment.gif?ex=67d12ecd&is=67cfdd4d&hm=225d51cec802d84090335c6ccbc92ceccfeac3cedd8b946198054399f40c4e45&",
]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions and message.reference is None:
        response_gif = random.choice(gif_urls)  # Выбираем ОДИН случайный GIF
        await message.reply(response_gif)  # Отправляем его
        return  # Прерываем дальнейшую обработку, если не нужно

    await bot.process_commands(message)  # Обрабатываем остальные команды
    
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

# Обработчик слэш-команды /boolean
@bot.tree.command(name="boolean", description="Randomly chooses between True and False")
@app_commands.describe(question="A question to answer")
async def boolean_command(interaction: discord.Interaction, question: str = None):
    if question is None:
        question = "Missing 💭"
    response = random.choice(["True ✅", "False ❌"])

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Question ❓", value=question, inline=False)
    embed.add_field(name="Random answer ✨", value=response, inline=False)

    await interaction.response.send_message(embed=embed)

# Обработчик слэш-команды /numbersrange
@bot.tree.command(name="range", description="Chooses a random number within a given range")
@app_commands.describe(start="Start of the range (integer)", end="End of the range (integer)")
async def numbersrange_command(interaction: discord.Interaction, start: int, end: int):
    if start > end:
        await interaction.response.send_message("Error: the start of the range is greater than the end. Try again.", ephemeral=True)
        return
    
    random_number = random.randint(start, end)

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Range ↔️", value=f"{start} - {end}", inline=False)
    embed.add_field(name="Selected number ✅", value=str(random_number), inline=False)

    await interaction.response.send_message(embed=embed)

# Обработчик слэш-команды /calculate
@bot.tree.command(name="calculate", description="Solves math expressions")
@app_commands.describe(number1="First number", operator="Operator (+, -, *, /)", number2="Second number")
async def calculate_command(interaction: discord.Interaction, number1: float, operator: str, number2: float):
    try:
        if operator not in ['+', '-', '*', '/']:
            raise ValueError("Unsupported operator. Use +, -, *, /")
        
        if operator == '+':
            result = number1 + number2
        elif operator == '-':
            result = number1 - number2
        elif operator == '*':
            result = number1 * number2
        elif operator == '/':
            if number2 == 0:
                raise ZeroDivisionError("Division by zero is not possible")
            result = number1 / number2

        # Убираем .0, если результат целое число
        if result.is_integer():
            result = int(result)

        # Преобразуем числа в строки без лишних нулей после запятой
        number1 = str(int(number1)) if number1.is_integer() else str(number1)
        number2 = str(int(number2)) if number2.is_integer() else str(number2)

        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="Expression", value=f"{number1} {operator} {number2}", inline=False)
        embed.add_field(name="Answer", value=str(result), inline=False)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# Команда выбора рандомного варианта
@bot.tree.command(name="choose", description="Chooses a random option from the provided ones")
@app_commands.describe(
    question="Question",
    option1="Required option 1",
    option2="Required option 2",
    option3="Optional option",
    option4="Optional option",
    option5="Optional option",
    option6="Optional option",
    option7="Optional option",
    option8="Optional option",
    option9="Optional option",
    option10="Optional option"
)
async def choose_command(
    interaction: discord.Interaction,
    option1: str,
    option2: str,
    question: str = None,
    option3: str = None,
    option4: str = None,
    option5: str = None,
    option6: str = None,
    option7: str = None,
    option8: str = None,
    option9: str = None,
    option10: str = None
):
    options = [option1, option2]
    extra_options = [option3, option4, option5, option6, option7, option8, option9, option10]
    
    # Добавляем дополнительные опции, если они не пустые
    options.extend(filter(None, extra_options))

    chosen_option = random.choice(options)  # Выбираем случайный вариант

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Question ❓", value=question if question else "Missing", inline=False)
    embed.add_field(name="Options 💬", value="\n".join(f"- {opt}" for opt in options), inline=False)
    embed.add_field(name="Selected ✅", value=f"- {chosen_option}", inline=False)

    await interaction.response.send_message(embed=embed)

# Команда чтобы получить аватар пользователя
@bot.tree.command(name="avatar", description="Gets the avatar of the specified user")
@app_commands.describe(user="The user whose avatar you want to see")
async def avatar_command(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"Here is the avatar of {user.display_name} 📸", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed)

# Команда таймера
@bot.tree.command(name="timer", description="Sets a timer and then pings you")
@app_commands.describe(seconds="Seconds", minutes="Minutes", hours="Hours")
async def timer_command(interaction: discord.Interaction, seconds: int = 0, minutes: int = 0, hours: int = 0):
    total_seconds = (hours * 3600) + (minutes * 60) + seconds

    if total_seconds <= 0:
        await interaction.response.send_message("You haven't entered any seconds, minutes, or hours!", ephemeral=True)
        return

    # Формируем текст для встроенного отсчета времени
    timer_message = f"The timer will go off in <t:{int((interaction.created_at.timestamp()) + total_seconds)}:R> ⏳"
    await interaction.response.send_message(timer_message)

    await asyncio.sleep(total_seconds)  # Ожидание заданного времени

    await interaction.channel.send(f"{interaction.user.mention}, the timer went off <t:{int((interaction.created_at.timestamp()) + total_seconds)}:R>‼️")

# Словарь с кодом Морзе для каждой буквы, цифры и знаков препинания (латиница + кириллица) (морзе)
morse_code_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',

    # Код Морзе для русских букв
    'А': '.-', 'Б': '-...', 'В': '.--', 'Г': '--.', 'Д': '-..-', 'Е': '.',
    'Ё': '.', 'Ж': '...-', 'З': '--..', 'И': '..', 'Й': '.---', 'К': '-.-',
    'Л': '.-..', 'М': '--', 'Н': '-.', 'О': '---', 'П': '.--.', 'Р': '.-.',
    'С': '...', 'Т': '-', 'У': '..-', 'Ф': '..-.', 'Х': '....', 'Ц': '-.-.',
    'Ч': '---.', 'Ш': '----', 'Щ': '--.-', 'Ъ': '--.--', 'Ы': '-.--',
    'Ь': '-..-', 'Э': '..-..', 'Ю': '..--', 'Я': '.-.-',

    # Код Морзе для символов
    '.': '.-.-.-', ',': '--..--', '?': '..--..', '!': '-.-.--', '/': '-..-.',
    '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', ';': '-.-.-.',
    '"': '.-..-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-',
    '$': '...-..-', '@': '.--.-.', "'": '.----.', ' ': '/'
}

# Функция для перевода текста в код Морзе (морзе)
def to_morse(text):
    text = text.upper()  # Переводим текст в верхний регистр
    morse_code = []
    
    for char in text:
        if char in morse_code_dict:  # Если символ есть в словаре
            morse_code.append(morse_code_dict[char])
        else:
            morse_code.append('?')  # Если символ не найден в коде Морзе, выводим ?
    
    return ' '.join(morse_code)

# Команда для преобразования текста в код Морзе (морзе)
@bot.tree.command(name='morse', description="Converts your text to Morse code, supports both Russian and English, as well as some symbols")
async def morse(interaction: discord.Interaction, *, text: str):
    morse_text = to_morse(text)

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Text 💬", value=f"`{text}`", inline=False)
    embed.add_field(name="Morse 👽", value=f"`{morse_text}`", inline=False)
    embed.set_footer(text='If you see "?", it means your character/language is not supported')

    await interaction.response.send_message(embed=embed)

# Синхронизация команд при запуске
@bot.event
async def on_ready():
    await asyncio.sleep(3)  # Даем боту немного времени перед синхронизацией
    try:
        await bot.tree.sync(guild=None)
        print("Slash-команды успешно синхронизированы!")
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")
    print(f"Бот {bot.user} запущен и готов к работе!")

# Запускаем Flask в отдельном потоке
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Запускаем бота
bot.run(TOKEN)
