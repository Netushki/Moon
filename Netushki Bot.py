import discord
import random  # Для генерации случайных значений
from discord.ext import commands
from discord import app_commands
import os
from threading import Thread
from flask import Flask
import re
import requests
from threading import Thread

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
@bot.tree.command(name="boolean", description="Случайно выбирает между True и False")
@app_commands.describe(question="Вопрос, на который нужно ответить")
async def boolean_command(interaction: discord.Interaction, question: str = None):
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



# Команда ссылок
@bot.tree.command(name="links", description="Ссылки на соцсети Netushki")
async def links_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🔗 Соцсети Netushki", color=discord.Color.blue())

    embed.add_field(
        name="### Просмотр",
        value=(
            "<:YouTube:1311661038453788772> **YouTube:** [Смотреть](https://youtube.com/channel/UCsGPCMtrGbO-xHm1P83yQdg)\n"
            "<:Twitch:1333125928426930236> **Twitch:** [Смотреть](https://www.twitch.tv/snow_netushki)"
        ),
        inline=False
    )

    embed.add_field(
        name="### Посты и чат",
        value=(
            "<:Telegram:1311660935139823697> **Telegram Канал:** [Перейти](https://t.me/+FqErRZgH_rg5YzZi)\n"
            "<:Discord:1330215982416789595> **Discord Сервер:** [Присоединиться](https://discord.com/invite/YyPdeKDESa)"
        ),
        inline=False
    )

    embed.add_field(
        name="### Остальное",
        value=(
            "<:DonationAlerts:1311660998481940542> **Донат (Donation Alerts):** [Поддержать](https://www.donationalerts.com/r/netushki)"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# Команда выбора рандомного варианта
@bot.tree.command(name="choose", description="Выбирает случайный вариант из предложенных")
@app_commands.describe(
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

    embed = discord.Embed(title="🎲 Случайный выбор", color=discord.Color.blue())
    embed.add_field(name="Варианты", value="\n".join(f"- {opt}" for opt in options), inline=False)
    embed.add_field(name="✅ Выбрано", value=f"**{chosen_option}**", inline=False)

    await interaction.response.send_message(embed=embed)

# Команда чтобы получить аватар пользователя
@bot.tree.command(name="avatar", description="Получает аватар указанного пользователя")
@app_commands.describe(user="Пользователь, чей аватар вы хотите увидеть")
async def avatar_command(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"Вот аватар пользователя {user.display_name}", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)

    await interaction.response.send_message(embed=embed)

import asyncio

# Команда таймера
@bot.tree.command(name="timer", description="Устанавливает таймер, а потом пингует вас")
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

# Словарь для хранения данных об игре (шарик)
games = {}

# Таймер для окончания игры при неактивности (шарик)
async def end_game_after_timeout(channel_id):
    await asyncio.sleep(5 * 60)  # 5 минут
    if channel_id in games:
        del games[channel_id]  # Закончить игру из-за неактивности
        channel = bot.get_channel(channel_id)
        await channel.send("Игра закончена из-за неактивности в течение 5 минут.")  # (шарик)

# Команда для старта игры с возможностью задать время (шарик)
@bot.command(name='шарик')
async def start_game(ctx, time_limit: int = 0):
    if ctx.channel.id in games:  # Проверка, если игра уже начата (шарик)
        await ctx.send("Игра уже запущена в этом канале!")  # (шарик)
        return

    # Загадать случайное число от 1 до 100 (шарик)
    secret_number = random.randint(1, 100)
    games[ctx.channel.id] = {
        "secret_number": secret_number,
        "players": {},
        "start_time": asyncio.get_event_loop().time(),  # Время начала игры (шарик)
        "time_limit": time_limit  # (шарик)
    }

    await ctx.send(f"Игра началась! Угадайте число от 1 до 100. Попробуйте угадать, отправив команду `/угадать [число]`.")

    if time_limit > 0:  # Если есть временной лимит (шарик)
        await ctx.send(f"У вас есть {time_limit} минут на угадывание.")  # (шарик)
        # Запуск таймера на окончание игры по времени (шарик)
        asyncio.create_task(end_game_after_timeout(ctx.channel.id))

# Команда для угадывания числа (шарик)
@bot.command(name='угадать')
async def guess_number(ctx, guess: int):
    # Проверка, запущена ли игра в этом канале (шарик)
    if ctx.channel.id not in games:
        await ctx.send("Игра не началась. Используйте команду `/шарик`, чтобы начать.")
        return

    game = games[ctx.channel.id]
    secret_number = game["secret_number"]

    # Проверка, делал ли игрок уже попытку (шарик)
    if ctx.author.id in game["players"]:
        await ctx.send(f"{ctx.author.mention}, вы уже пытались угадать число.")  # (шарик)
        return

    # Добавление игрока (шарик)
    game["players"][ctx.author.id] = guess

    # Проверка угадал ли игрок (шарик)
    if guess < secret_number:
        await ctx.send(f"{ctx.author.mention}, ваше число меньше!")  # (шарик)
    elif guess > secret_number:
        await ctx.send(f"{ctx.author.mention}, ваше число больше!")  # (шарик)
    else:
        await ctx.send(f"{ctx.author.mention}, поздравляю! Вы угадали число {secret_number}!")  # (шарик)
        del games[ctx.channel.id]  # Закрытие игры после правильного ответа (шарик)

    # Проверка, если время вышло (шарик)
    if game["time_limit"] > 0 and asyncio.get_event_loop().time() - game["start_time"] > game["time_limit"] * 60:  # (шарик)
        del games[ctx.channel.id]  # (шарик)
        await ctx.send(f"Время игры истекло! Игра завершена.")  # (шарик)

# Команда рандомных шуток
@bot.command(name='шутка')
async def joke(ctx):
    # API для случайной шутки
    url = "https://official-joke-api.appspot.com/random_joke"
    
    # Получаем шутку из API
    response = requests.get(url)
    
    if response.status_code == 200:
        joke_data = response.json()
        setup = joke_data['setup']  # Начало шутки
        punchline = joke_data['punchline']  # Концовка шутки
        
        await ctx.send(f"{setup} {punchline}")  # Отправляем шутку в чат
    else:
        await ctx.send("Не удалось получить шутку. Попробуйте позже.")  # В случае ошибки

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
@bot.command(name='morse', help="Превращает ваш текст в код морзе, поддерживается русский и английский, а также некоторые символы")
async def morse(ctx, *, text: str):
    morse_text = to_morse(text)  # Преобразуем текст в код Морзе
    await ctx.send(f"Код Морзе: {morse_text}")  # Отправляем результат

# Запуск Flask в отдельном потоке
Thread(target=run_flask).start()

# Запуск бота
bot.run(TOKEN)











