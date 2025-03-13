import discord
import random  # Для генерации случайных значений
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
import re
import threading
import asyncio
import requests

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
@bot.tree.command(name="правда", description="Случайно выбирает между True и False")
@app_commands.describe(question="Вопрос, на который нужно ответить")
async def boolean_command(interaction: discord.Interaction, question: str = None):
    if question is None:
        question = "Отсутствует"
    response = random.choice(["<:Checkmark:1349434107226226718> <:Checkmark:1349434107226226718> <:Checkmark:1349434107226226718>", "<:Cross:1349434180727210096> <:Cross:1349434180727210096> <:Cross:1349434180727210096>"])

    embed = discord.Embed(color=discord.Color.blue())
    embed.add_field(name="Вопрос", value=question, inline=False)
    embed.add_field(name="Случайный ответ", value=response, inline=False)

    await interaction.response.send_message(embed=embed)

# Обработчик слэш-команды /numbersrange
@bot.tree.command(name="диапазон", description="Выбирает случайное число в заданном диапазоне")
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
@bot.tree.command(name="вычислить", description="Решает примеры")
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

        # Убираем .0, если результат целое число
        if result.is_integer():
            result = int(result)

        # Преобразуем числа в строки без лишних нулей после запятой
        number1 = str(int(number1)) if number1.is_integer() else str(number1)
        number2 = str(int(number2)) if number2.is_integer() else str(number2)

        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="Пример", value=f"{number1} {operator} {number2}", inline=False)
        embed.add_field(name="Ответ", value=str(result), inline=False)

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Ошибка: {e}", ephemeral=True)

# Команда выбора рандомного варианта
@bot.tree.command(name="выбрать", description="Выбирает случайный вариант из предложенных")
@app_commands.describe(
    question="Вопрос",
    option1="Обязательный вариант 1",
    option2="Обязательный вариант 2",
    option3="Дополнительный вариант",
    option4="Дополнительный вариант",
    option5="Дополнительный вариант",
    option6="Дополнительный вариант",
    option7="Дополнительный вариант",
    option8="Дополнительный вариант",
    option9="Дополнительный вариант",
    option10="Дополнительный вариант"
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
    embed.add_field(name="Вопрос", value=question if question else "Отсутствует", inline=False)
    embed.add_field(name="Варианты", value="\n".join(f"- {opt}" for opt in options), inline=False)
    embed.add_field(name="Выбрано", value=f"- {chosen_option}", inline=False)

    await interaction.response.send_message(embed=embed)

# Команда чтобы получить аватар пользователя
@bot.tree.command(name="аватар", description="Получает аватар указанного пользователя")
@app_commands.describe(user="Пользователь, чей аватар вы хотите увидеть")
async def avatar_command(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"Вот аватар пользователя {user.display_name}", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed)

# Команда таймера
@bot.tree.command(name="таймер", description="Устанавливает таймер, а потом пингует вас")
@app_commands.describe(seconds="Секунды", minutes="Минуты", hours="Часы")
async def timer_command(interaction: discord.Interaction, seconds: int = 0, minutes: int = 0, hours: int = 0):
    total_seconds = (hours * 3600) + (minutes * 60) + seconds

    if total_seconds <= 0:
        await interaction.response.send_message("Вы не ввели ни секунды, ни минуты, ни часы!", ephemeral=True)
        return

    # Формируем текст для встроенного отсчета времени
    timer_message = f"Таймер сработает через <t:{int((interaction.created_at.timestamp()) + total_seconds)}:R> ⏳"
    await interaction.response.send_message(timer_message)

    await asyncio.sleep(total_seconds)  # Ожидание заданного времени

    await interaction.channel.send(f"{interaction.user.mention}, таймер сработал! ⏰")

# Рандомная гифка гд
TENOR_API_KEY = os.getenv('TENOR_API_KEY')

@bot.tree.command(name='гдгиф', description="Отправляет случайную GIF про Geometry Dash с Tenor")
async def gif(interaction: discord.Interaction):  
    await interaction.response.defer()  # Отложенный ответ

    apikey = os.getenv('TENOR_API_KEY')
    ckey = "my_test_app"
    search_terms = ["geometry dash", "geometry dash meme", "geometry dash level", "geometry dash icon"]  # Разные поисковые запросы
    lmt = 50  # Запрашиваем 50 гифок
    max_retries = 3  # Количество попыток для одного запроса
    max_search_attempts = 3  # Сколько раз менять поисковый запрос

    for search_attempt in range(max_search_attempts):  # Меняем поисковый запрос, если все попытки неудачны
        search_term = random.choice(search_terms)  # Выбираем случайный запрос
        url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={apikey}&client_key={ckey}&limit={lmt}"

        for attempt in range(max_retries):  # Делаем несколько попыток для текущего запроса
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()

                    if 'results' in data and data['results']:
                        gif_url = random.choice(data['results'])['url']  # Выбираем случайную из 100
                        await interaction.followup.send(gif_url)
                        return  # Выход из функции после успешного отправления
                elif response.status_code == 404:
                    print(f"Попытка {attempt + 1}: API вернул 404. Пробуем ещё раз...")  
                    continue  # Пробуем снова с тем же запросом
                else:
                    print(f"Ошибка API Tenor: {response.status_code}")
                    break  # Если другая ошибка, прерываем попытки
            except Exception as e:
                print("Ошибка:", e)

        print(f"Запрос '{search_term}' не дал результатов, пробуем другой...")
    
    await interaction.followup.send("Не удалось найти подходящую гифку после нескольких попыток.")

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
@bot.tree.command(name='морзе', description="Превращает ваш текст в код морзе, поддерживается русский и английский, а также некоторые символы")
async def morse(interaction: discord.Interaction, *, text: str):  # Используем interaction вместо ctx
    morse_text = to_morse(text)  # Преобразуем текст в код Морзе
    await interaction.response.send_message(morse_text)  # Используем send_message для interaction

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
bot.run(TOKEN)  # Замените на свой токен бота
