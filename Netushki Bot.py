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

        if result.is_integer():
            result = int(result)

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
        await channel.send("Игра закончена из-за неактивности в течение 5 минут.")

# Команда для старта игры с возможностью задать время (шарик)
@bot.command(name='шарик')
async def start_game(ctx, time_limit: int = 0):
    if ctx.channel.id in games:
        await ctx.send("Игра уже запущена в этом канале!")
        return

    # Загадать случайное число от 1 до 100 (шарик)
    secret_number = random.randint(1, 100)
    games[ctx.channel.id] = {
        "secret_number": secret_number,
        "players": {},
        "start_time": asyncio.get_event_loop().time(),  # Время начала игры
        "time_limit": time_limit
    }

    await ctx.send(f"Игра началась! Угадайте число от 1 до 100. Попробуйте угадать, отправив команду `/угадать [число]`.")

    if time_limit > 0:
        await ctx.send(f"У вас есть {time_limit} минут на угадывание.")

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
        await ctx.send(f"{ctx.author.mention}, вы уже пытались угадать число.")
        return

    # Добавление игрока (шарик)
    game["players"][ctx.author.id] = guess

    # Проверка угадал ли игрок (шарик)
    if guess < secret_number:
        await ctx.send(f"{ctx.author.mention}, ваше число меньше!")
    elif guess > secret_number:
        await ctx.send(f"{ctx.author.mention}, ваше число больше!")
    else:
        await ctx.send(f"{ctx.author.mention}, поздравляю! Вы угадали число {secret_number}!")
        del games[ctx.channel.id]  # Закрытие игры после правильного ответа (шарик)

    # Проверка, если время вышло (шарик)
    if game["time_limit"] > 0 and asyncio.get_event_loop().time() - game["start_time"] > game["time_limit"] * 60:
        del games[ctx.channel.id]
        await ctx.send(f"Время игры истекло! Игра завершена.")


# Запуск Flask в отдельном потоке
Thread(target=run_flask).start()

# Запуск бота
bot.run(TOKEN)










