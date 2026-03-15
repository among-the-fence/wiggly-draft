import discord
import os
import dotenv

dotenv.load_dotenv()

# bot = discord.Bot()
bot = discord.Bot(debug_guilds=[os.getenv('DEFAULT_GUILD')])

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    emoji_list = list(bot.guilds[0].emojis)
    global io_moji
    io_moji_list = [x for x in emoji_list if x.name == "io"]
    io_moji = io_moji_list[0] if len(io_moji_list) >= 1 else None
    global pudge
    pudge_moji_list = [x for x in emoji_list if x.name == "pudge"]
    pudge = pudge_moji_list[0] if len(pudge_moji_list) >= 1 else None

    print(pudge)
    print(io_moji)

    for s in bot.guilds:
        for x in s.channels:
            if x.name == "bot":
                with open("message.txt", mode="r") as messagefile:
                    await bot.get_channel(x.id).send(messagefile.readline())

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(os.getenv('TOKEN'))