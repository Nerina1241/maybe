import asyncio
import os
import shutil

import openpyxl

from bin.core.config import UserConfig
import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get
from colorama import Fore
import redis
from captcha.image import ImageCaptcha
import random
import mysql.connector

status_r = UserConfig["Status_Random"]

client = commands.Bot(command_prefix=UserConfig["BotPrefix"])
client.remove_command('help')

async def status_rotate():
    while status_r == "True":
        s_time = int(UserConfig["StatusChangeTime"])
        game1 = discord.Game(UserConfig["Status1"])
        await client.change_presence(status=discord.Status.online, activity=game1)
        await asyncio.sleep(s_time)

        game2 = discord.Game("Status : " + UserConfig["Status2"])
        await client.change_presence(status=discord.Status.online, activity=game2)
        await asyncio.sleep(s_time)

        onlineusers = int(r.get("ripple:online_users").decode("utf-8"))
        onlineusersstr = str(onlineusers)
        game3 = discord.Game("Online User : " + onlineusersstr)
        await client.change_presence(status=discord.Status.online, activity=game3)
        await asyncio.sleep(s_time)

        game4 = discord.Game(UserConfig["Status4"])
        await client.change_presence(status=discord.Status.online, activity=game4)
        await asyncio.sleep(s_time)

try:
    r = redis.Redis(host=UserConfig["RedisHost"], password=UserConfig["RedisPassword"], port=UserConfig["RedisPort"], db=UserConfig["RedisDb"])
    print(f"{Fore.GREEN}Connect to {Fore.RED}Redis!")
except Exception as e:
    print(f"{Fore.RED}Failed connecting to Redis! Abandoning!\n Error: {e}{Fore.RESET}")
    exit()

try:
    mydb = mysql.connector.connect(host=UserConfig["MysqlHost"], user=UserConfig["MysqlUser"], passwd=UserConfig["MysqlPassword"])
    print(f"{Fore.GREEN}Connect to {Fore.BLUE}MySQL")
except Exception as e:
    print(f"{Fore.RED}Failed connecting to MySQL\n Error: {e}{Fore.RESET}")
    exit()

mysql_db = UserConfig["MysqlDb"]
mycursor = mydb.cursor()
mycursor.execute(f"USE {mysql_db}")
mycursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

@client.event
async def on_ready():
    print(f"{Fore.RED}maybebot {Fore.LIGHTMAGENTA_EX}is ready")
    if status_r == "False":
        print(f"{Fore.BLUE}Status Type : " + UserConfig["Status"])
        game = discord.Game(UserConfig["Status"])
        await client.change_presence(status=discord.Status.online, activity=game)
    if status_r == "True":
        print(f"{Fore.BLUE}Status Type : Random" + "\n" + UserConfig["Status1"] + "\n" + UserConfig["Status2"] + "\n" + UserConfig["Status3"] + "\n" + UserConfig["Status4"])
        client.loop.create_task(status_rotate())
    queues.clear()
    print(f"{Fore.GREEN}Queue Cleared")

@client.command()
async def online(ctx):
    onlineusers = int(r.get("ripple:online_users").decode("utf-8"))
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Debian Online Users : ",
        description=onlineusers
    )
    embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/708248923185348628/708964286524948490/Debianlogo2.png")
    embed.set_footer(text="Via MaybeBot")

    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def ping(ctx):
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Ping?",
        description="Pong!"
    )
    embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
    embed.set_thumbnail(
        url="https://i.imgur.com/YanQUbG.jpg")
    embed.set_footer(text="Via MaybeBot")

    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def auth(ctx):
    Image_captcha = ImageCaptcha()
    a = ""
    for i in range(5):
        a += str(random.randint(0, 9))

    name = str(ctx.author.id) + ".png"
    Image_captcha.write(a, name)
    await ctx.channel.send(file=discord.File(name))

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await client.wait_for("message", timeout=60, check=check)
    except:
        await ctx.channel.send("Time Out!")
        return
    if msg.content == a:
        await ctx.channel.send("Welcome To Debian!")
        member = msg.author
        role = get(member.guild.roles, name=UserConfig["AuthRole"])
        rolen = UserConfig["AuthRole"]
        await ctx.author.add_roles(role)
        print(f"{member} was given {rolen}")
    else:
        await ctx.channel.send("Wrong answer")

@client.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"{Fore.YELLOW}Maybe has connected to {channel}\n")
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Joined Channel",
        description=f"Channel: {channel}"
    )
    embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
    embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
    embed.set_footer(text="Via MaybeBot")

    await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"{Fore.YELLOW}Maybe has left {channel}\n")
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Left Channel",
            description=f"Left Channel: {channel}"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
    else:
        print(f"{Fore.RED}Maybe wastold to leave voice channel, but was not in one")
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Error",
            description=f"I Think im not in a any voice channel"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)


@client.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    song_chk = os.path.isfile("/bin/music/Now/song.mp3")
    if song_chk:
        os.remove("/bin/music/Now/song.mp3")
    song_chk2 = os.path.isfile("song.mp3")
    if song_chk2:
        os.remove("song.mp3")

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    def check_queue():
        Queue_infile = os.path.isdir("./bin/music/Queue")

        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("bin/music/Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print(f"{Fore.RED}No more Queued Song(s)\n")
                queues.clear()
                return

            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("bin/music/Queue") + "/" + first_file)

            if length != 0:
                print(f"{Fore.RED}Song done, Playing Next Queued\n")
                print(f"{Fore.GREEN}Songs still in queue: {still_q}")
                song_there = os.path.isfile("./bin/music/Now/song.mp3")
                if song_there:
                    os.remove("./bin/music/Now/song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')
                        shutil.move('song.mp3', 'bin/music/Now')
                voice.play(discord.FFmpegPCMAudio("./bin/music/Now/song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

                nname = name[:-16]
                qnum = str(q_num)

            else:
                queues.clear()
                return
        else:
            queues.clear()
            print(f"{Fore.RED}No songs were queued before the ending of the last song\n")

    song_there = os.path.isfile("./bin/music/Now/song.mp3")
    queue_there = os.path.isdir("./bin/music/Queue")
    if song_there and queue_there is True:
        try:
            if song_there:
                Queue_infile = os.path.isdir("./bin/music/Queue")
                if Queue_infile is False:
                    os.mkdir("bin/music/Queue")
                DIR = os.path.abspath(os.path.realpath("bin/music/Queue"))
                q_num = len(os.listdir(DIR))
                q_num += 1
                add_queue = True
                while add_queue:
                    if q_num in queues:
                        q_num += 1
                    else:
                        add_queue = False
                        queues[q_num] = q_num

                embed1 = discord.Embed(
                    color=0xf0ff39,
                    title="Download Song Now!",
                    description=f"Pleas Wait A Some Second!"
                )
                embed1.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
                embed1.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
                embed1.set_footer(text="Via MaybeBot")
                embed1.add_field(name="Queue: ", value=str(q_num))
                await ctx.send(embed=embed1)

                queue_path = os.path.abspath(f"song{q_num}")

                ydl_opt = {
                    'format': 'bestaudio/best',
                    'quit': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

                with youtube_dl.YoutubeDL(ydl_opt) as ydl:
                    print(f"{Fore.LIGHTBLUE_EX} Downloading Song File now\n")
                    ydl.download([url])

                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        name = file
                        print(f"{Fore.GREEN} Renamed File: {file}")
                        os.rename(file, queue_path + ".mp3")
                        shutil.move(queue_path + ".mp3", 'bin/music/Queue')

                        nname = name[:-16]
                        embed = discord.Embed(
                            color=0xf0ff39,
                            title="Adding Song In The Queue:",
                            description=nname
                        )
                        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
                        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
                        embed.set_footer(text="Via MaybeBot")
                        embed.add_field(name="Queue: ", value=str(q_num), inline=False)
                        await ctx.send(embed=embed)

                        print(f"{Fore.YELLOW}Song added to queue \n")

        except PermissionError:
            print(f"{Fore.RED}I Cant Remove song file now")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description=f"Music Start Error"
            )
            embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
            embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
            embed.set_footer(text="Via MaybeBot")

            await ctx.send(embed=embed)
            return

    if song_there is False:
        embed = discord.Embed(
            color=0xf0ff39,
            title="Download Song Now!",
            description=f"Pleas Wait A Some Second!"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)

        voice = get(client.voice_clients, guild=ctx.guild)

        ydl_opt = {
            'format': 'bestaudio/best',
            'quit': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opt) as ydl:
            print(f"{Fore.LIGHTBLUE_EX} Downloading Song File now\n")
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"{Fore.GREEN} Renamed File: {file}")
                song_there = os.path.isfile("./bin/music/Now/song.mp3")
                if song_there:
                    os.remove("./bin/music/Now/song.mp3")
                os.rename(file, "song.mp3")
                shutil.move("song.mp3", "./bin/music/Now")

        voice.play(discord.FFmpegPCMAudio("./bin/music/Now/song.mp3"), after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07

        try:
            nname = name[:-16]
            embed = discord.Embed(
                color=0xf0ff39,
                title="Playing Now",
                description=f"{nname}"
            )
            embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
            embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
            embed.set_footer(text="Via MaybeBot")
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                color=0xf0ff39,
                title="Playing Now",
                description=f"Playing Now But idk, What is this Song Name?"
            )
            embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
            embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
            embed.set_footer(text="Via MaybeBot")
            await ctx.send(embed=embed)

        print(f"{Fore.GREEN} Playing {nname}\n")

@client.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print(f"{Fore.YELLOW}Music paused")
        voice.pause()
        embed = discord.Embed(
            color=0xf0ff39,
            title="Music Paused",
            description=f"If You Want to Resume? Use /resume"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
    else:
        print(f"{Fore.RED} Music Not Playing")
        embed = discord.Embed(
            color=0xff00000,
            title="Error",
            description=f"Music Not Playing NOW!"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print(f"{Fore.YELLOW}Music Resumed")
        voice.resume()
        embed = discord.Embed(
            color=0xf0ff39,
            title="Resumed Music",
            description=f"If You Want to Pause? Use /Pause"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
    else:
        print(f"{Fore.RED} Music is not paused : Not Playing Now")
        embed = discord.Embed(
            color=0xff0000,
            title="Error",
            description=f"Music is Not Playing Now"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    queues.clear()
    queue_infile = os.path.isdir("./Queue")

    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print(f"{Fore.YELLOW}Music Stopped")
        voice.stop()
        embed = discord.Embed(
            color=0xf0ff39,
            title="Music Stopped",
            description=f"Do you want Playing Music? Use /play"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
    else:
        print(f"{Fore.RED} No Music Playing now")
        embed = discord.Embed(
            color=0xff0000,
            title="Error",
            description=f"No Music Playing Now"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)

queues = {}

@client.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./bin/music/Queue")
    if Queue_infile is False:
        os.mkdir("bin/music/Queue")
    DIR = os.path.abspath(os.path.realpath("bin/music/Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(f"song{q_num}")

    ydl_opt = {
        'format': 'bestaudio/best',
        'quit': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opt) as ydl:
        embed = discord.Embed(
            color=0xf0ff39,
            title="Download Song Now!",
            description=f"Pleas Wait A Some Second!"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
        print(f"{Fore.LIGHTBLUE_EX} Downloading Song File now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"{Fore.GREEN} Renamed File: {file}")
            os.rename(file, queue_path + ".mp3")
            shutil.move(queue_path + ".mp3", 'bin/music/Queue')

    nname = name[:-16]
    embed = discord.Embed(
        color=0xf0ff39,
        title="Adding Song In The Queue:",
        description=nname
    )
    embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
    embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
    embed.set_footer(text="Via MaybeBot")
    embed.add_field(name="Queue: ", value=str(q_num), inline=False)
    await ctx.send(embed=embed)


    print(f"{Fore.YELLOW}Song added to queue \n")

@client.command(pass_context=True, aliases=['sk', 'ski'])
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print(f"{Fore.YELLOW}Skip Song")
        voice.stop()
        embed = discord.Embed(
            color=0xf0ff39,
            title="Skip Song",
            description=f"ok i'll skip song"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)
    else:
        print(f"{Fore.RED} No music playing failed to play next song")
        embed = discord.Embed(
            color=0xff0000,
            title="Error",
            description=f"No Music in the Next Queue"
        )
        embed.set_author(name="MayBe", icon_url="https://i.imgur.com/rlx3WnT.png")
        embed.set_thumbnail(url="https://i.imgur.com/5P4cCLB.png")
        embed.set_footer(text="Via MaybeBot")

        await ctx.send(embed=embed)


client.run(UserConfig["BotToken"])