import discord
import os
import json
from discord.ext import commands
import youtube_dl

with open("config.json", encoding="utf-8") as file:
    settings = json.load(file)["settings"]
client = commands.Bot(settings["prefix"])
download = False


@client.command()
async def documentation(ctx):
    help = [
        "!playing_mode: меняет способ воспроизведения:\nСкачать и слушать полностью: download\nСлушать без скачивания "
        "(не полностью): link\nПример: !playing_mode download",
        "!play: запускает музыку, в качестве параметра ссылка на видео с youtube\nПример: !play https://www.youtube.co"
        "m/watch?v=zxptc68Mpw4",
        "!pause: ставит музыку на паузу",
        "!resume: включает поставленную на паузу музыку",
        "!stop: выключает музыку\n ОБЯЗАТЕЛЬНО ВЫПОЛНИТЕ КОМАНДУ ЕСЛИ МУЗЫКА ВОСПРОИЗВОДИТСЯ,"
        " А ВЫ СОБИРАЕТЕСЬ ВКЛЮЧИТЬ ДРУГУЮ",
        "!leave: бот выходит из голосового канала",
        "!connect: бот подключается к голосовому каналу"
    ]
    for i in help:
        await ctx.send("\n\n:eight_spoked_asterisk: " + i)


@client.command()
async def playing_mode(ctx, typing: str):
    global download
    if typing in ["download"]:
        download = True
        await ctx.send(
            ":white_check_mark: Изменено. Теперь видео будет скачиваться перед запуском, но это займет больше времени"
        )
    else:
        if not download:
            return
        await ctx.send(
            ":white_check_mark: Изменено. Теперь видео не будет скачиваться перед запуском, но есть лимит времени"
        )
        download = False


@client.command()
async def play(ctx, url: str):
    for i in os.listdir():
        if i.endswith(".m4a") or i.endswith(".mp3") or i.endswith(".webm"):
            os.remove(i)
    if download:
        ydl_opts = {
            "format": "bestaudio",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url, download=True)
        for i in os.listdir():
            if i.endswith(".m4a") or i.endswith(".mp3") or i.endswith(".webm"):
                os.rename(i, "file.mp3")
        voiceChannel = ctx.author.voice.channel
        try:
            await voiceChannel.connect()
        except discord.ext.commands.errors.CommandInvokeError:
            pass
        except discord.errors.ClientException:
            pass
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        try:
            voice.play(discord.FFmpegPCMAudio("file.mp3"))
        except discord.errors.ClientException:
            voice.stop()
            voice.play(discord.FFmpegPCMAudio("file.mp3"))
        except discord.ext.commands.errors.CommandInvokeError:
            voice.stop()
            voice.play(discord.FFmpegPCMAudio("file.mp3"))
    else:
        ydl_opts = {
            "format": "bestaudio",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url, download=False)
        voiceChannel = ctx.author.voice.channel
        try:
            await voiceChannel.connect()
        except discord.ext.commands.errors.CommandInvokeError:
            pass
        except discord.errors.ClientException:
            pass
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        try:
            voice.play(discord.FFmpegPCMAudio(info["formats"][0]["url"]))
        except discord.errors.ClientException:
            voice.pause()
            voice.play(discord.FFmpegPCMAudio(info["formats"][0]["url"]))
        except discord.ext.commands.errors.CommandInvokeError:
            voice.pause()
            voice.play(discord.FFmpegPCMAudio(info["formats"][0]["url"]))
    if voice.is_playing():
        await ctx.send(f":headphones: сейчас играет:\n{info['title']}")


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
        await ctx.send(":white_check_mark: Бот успешно отключен от голосового канала")
    else:
        await ctx.send(":exclamation: Бот не подключен ни к какому голосовому каналу")
    for i in os.listdir():
        if i.endswith(".m4a") or i.endswith(".mp3") or i.endswith(".webm"):
            os.remove(i)


@client.command()
async def connect(ctx):
    voiceChannel = ctx.author.voice.channel
    try:
        await voiceChannel.connect()
        await ctx.send(":white_check_mark: Бот успешно подключен к голосовому каналу")
    except discord.ext.commands.errors.CommandInvokeError:
        await ctx.send(":exclamation: Бот уже подключен к голосовому каналу")
    except discord.errors.ClientException:
        await ctx.send(":exclamation: Бот уже подключен к голосовому каналу")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send(":white_check_mark: Музыка поставлена на паузу, чтобы включить введите !resume")
    else:
        await ctx.send(":exclamation: Музыка уже на паузе, чтобы включить введите !resume")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send(":exclamation: Музыка не на паузе, чтобы поставить введите !pause")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()
    await ctx.send(":white_check_mark: Музыка выключена")
    for i in os.listdir():
        if i.endswith(".m4a") or i.endswith(".mp3") or i.endswith(".webm"):
            os.remove(i)


if __name__ == "__main__":
    for i in os.listdir():
        if i.endswith(".m4a") or i.endswith(".mp3") or i.endswith(".webm"):
            os.remove(i)
    client.run(settings["token"])
