import discord
import random  # Для генерации случайных значений
from discord.ext import commands
from discord import app_commands
import os

# Настройки бота
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv('TOKEN')

# Словарь для отслеживания использованных GIF
used_gifs = {}

# Список возможных GIF
gif_urls = [
    "https://cdn.discordapp.com/attachments/1346943612373569557/1347573414142939279/attachment.gif?ex=67cef40a&is=67cda28a&hm=b1b5b846ec7bf21b1dcb93e393b78dd8dc3dea112e0e8c8d9460308d517e6b84&",
    "https://cdn.discordapp.com/attachments/1322781202851041358/1347037669388980274/attachment.gif",
    "https://cdn.discordapp.com/attachments/1309799105756790794/1309909672446398534/speechmemified_Half_Life_Deathmatch_Source.jpg.gif?ex=67cf0af2&is=67cdb972&hm=6cd814dd9f531de8eb5e9a6ecdc7c18ad39c13bbfbd120cbe1e235799d7ee9ea&",
    "https://tenor.com/view/speech-bubble-gif-26412022",
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif?ex=67cee89a&is=67cd971a&hm=54602311db4c7128af5c90aefa3e74a4f78985de1b054016fcb2b694e7f85a4a&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348366855894470697/attachment.gif?ex=67cf33fd&is=67cde27d&hm=b973f19cdfbfbed725153a92c50776435f70ca6181edde63854f3626d93ef791&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367007401115658/attachment.gif?ex=67cf3422&is=67cde2a2&hm=34336e5ea5a22862ee676ebb2287b053cd686eb64e3b5d70fcfa946dc1037f42&",
    "https://cdn.jacher.io/f3ac073b88487e1b.gif",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367459392159744/attachment.gif?ex=67cf348d&is=67cde30d&hm=c228de0ae418b42862b759ba41e54a2f434d438f22d465bdfb38c5a89ce49e6e&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367494766919740/attachment.gif?ex=67cf3496&is=67cde316&hm=5124d61b87c8cd107cdfd91416e273baedd9550eb44d5f37e123e35805ddcfd2&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348367679962091531/attachment.gif?ex=67cf34c2&is=67cde342&hm=60514011f732c063d000e51c4164f1bfcc8f9e395fac4d336b44316aa6d33645&",
    "https://tenor.com/view/speech-bubble-gif-26412022",
    "https://media.discordapp.net/attachments/1055080776808546353/1177601225542352927/attachment.gif?ex=67cee89a&is=67cd971a&hm=54602311db4c7128af5c90aefa3e74a4f78985de1b054016fcb2b694e7f85a4a&",
    "https://cdn.discordapp.com/attachments/1207730830487855154/1348366855894470697/attachment.gif?ex=67cf33fd&is=67cde27d&hm=b973f19cdfbfbed725153a92c50776435f70ca6181edde63854f3626d93ef791&"
]

# Обработчик сообщений
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

# Событие при запуске бота
@bot.event
async def on_ready():
    print(f"Мы вошли как {bot.user}")

# Запуск бота
bot.run(TOKEN)


