#!/usr/bin/env python3
import os
import discord
import random
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from googleapiclient.discovery import build

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

YOUTUBE_KEY = os.getenv('YOUTUBE_TOKEN')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
benjaId = 'UCZXjnHnk0KXhdyu580CPfJg'
beckId  = 'UCSkRzEUyoo9cS8RwfYZycdw'
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def getVideos(channelId):
    channel = youtube.channels().list(id=channelId, part="contentDetails").execute()
    playlistId = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    nextPageToken = None

    while True:
        results = youtube.playlistItems().list(
            playlistId=playlistId,
            part='snippet',
            maxResults=50,
            pageToken=nextPageToken
        ).execute()

        videos += results['items']
        nextPageToken = results.get('nextPageToken')

        if nextPageToken is None:
            break

    return videos

benjaList = getVideos(benjaId)
def getVideoIds(videos):
    videoIds = []
    for video in videos:
        videoId = video['snippet']['resourceId']['videoId']
        videoIds.append(videoId)

    return videoIds
    
with open('benja.txt', 'w') as f:
    for item in benjaList:
        f.write("%s\n" % item)

videoIds = getVideoIds(benjaList)

@bot.command()
async def benja(ctx):
    rng = random.randrange(len(videoIds))
    randVideo = "https://www.youtube.com/watch?v=" + str(videoIds[rng])
    await ctx.send(randVideo)

bot.run(TOKEN)
