#!/usr/bin/env python3
import os
import discord
import random
import re
import datetime
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from googleapiclient.discovery import build

# Load .env file that holds the tokens and API keys
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Read in discord token and Youtube API key from .env
TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_KEY = os.getenv('YOUTUBE_TOKEN')

# Set the Youtube channel ids
benjaId = 'UCZXjnHnk0KXhdyu580CPfJg'
beckId  = 'UCSkRzEUyoo9cS8RwfYZycdw'

# Connect to Youtube API
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

# Map that holds the start and end time for the bot to post
benjaTimeMap = {

    "start": datetime.time(12, 13, 0),
    "end"  : datetime.time(12, 14, 0)
}

# List of Benjabola videos and video ids
global benjaList
global videoIds

# Give bot permissions
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def getVideos(channelId):
    """Get a list of videos from a specified Youtube channel's upload playlist"""

    # Get the list of playlists from the youtube channel
    channel = youtube.channels().list(id=channelId, part="contentDetails").execute()

    # Get the uploads playlist
    playlistId = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # List of videos to be populated
    videos = []
    nextPageToken = None

    # Loop through each video result in the uploads playlist
    while True:
        results = youtube.playlistItems().list(
            playlistId=playlistId,
            part='snippet',
            maxResults=50,
            pageToken=nextPageToken
        ).execute()

        # Add the video result to the video results list
        videos += results['items']
        nextPageToken = results.get('nextPageToken')

        # Check if hit the end of the playlist
        if nextPageToken is None:
            break
    
    # Return the videos list
    return videos

def getVideoIds(videos):
    """Get a list of video ids from a provided list of video results"""

    # List of video ids to be populated from the videos list
    videoIds = []

    # Loop through the videos list
    for video in videos:

        # Get the video id and append it to the ids list
        videoId = video['snippet']['resourceId']['videoId']
        videoIds.append(videoId)

    # Return the video ids list
    return videoIds

def updateVideoList():
    """Update the list of Benjabola videos and video ids"""

    # Access global variables
    global benjaList
    global videoIds

    # Update the list of videos and video ids
    benjaList = getVideos(benjaId)
    videoIds = getVideoIds(benjaList)

@bot.event
async def on_ready():
    await benjaLoop.start()

@bot.command()
@commands.has_role('Benjabola')
async def benjatime(ctx, start=None):

    # Check if start and end time were provided
    if start is not None:

        # Regex to determine if bedtime was provided in correct format
        regex = re.search('^(2[0-3]|1[0-9]|[0-9]|[^0-9][0-9]):([0-5][0-9]|[0-9])$', start)
        if regex is not None:
            start += ":00" # Needed for strptime() function

            # Get the start and end time
            startTime = datetime.datetime.strptime(start,"%H:%M:%S").time()
            endTime = datetime.datetime.strptime(start,"%H:%M:%S")
            endTime += datetime.timedelta(minutes=1)
            endTime = endTime.time()
            
            # Set the start and end time in the time map
            benjaTimeMap["start"] = startTime
            benjaTimeMap["end"]   = endTime

    # Send message with bedtime (doesn't update if format was provided incorrectly)
    message = "Benjabola time is at " + str(benjaTimeMap["start"])
    await ctx.send(message)

@tasks.loop(seconds=60)
async def benjaLoop():

    # Access global video ids list
    global videoIds

    # Start and end time that benjabola video should be posted
    # Current time for comparison
    now = datetime.datetime.now().time()

    # Update the video list once a day in time range
    if time_in_range(benjaTimeMap["start"], benjaTimeMap["end"], now):
        updateVideoList()

    # Loop through all the servers that the bot is present in
    for guild in bot.guilds:

        # Post a random video at the specified time to the specified channel
        if time_in_range(benjaTimeMap["start"], benjaTimeMap["end"], now):

            # Get a random video from the list of videos
            rng = random.randrange(len(videoIds))
            randVideo = "Your daily dose of Benjabola\n https://www.youtube.com/watch?v=" + str(videoIds[rng])

            # Specifc channel for debugging
            # await bot.get_channel(830207640713953323).send(randVideo)

            # Post in the first available text channel in the server
            await guild.text_channels[0].send(randVideo)

bot.run(TOKEN)
