import discord
from discord import message
from discord.ext import tasks
import shelve
import datetime
from datetime import time, timedelta, timezone

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
  global sc_channel
  if (str(message.author.id) == '1180377638766907463'):
    if (message.channel.id == int(sc_channel)):
      last_msg_desc = message.embeds[0].description
      print(last_msg_desc)
    

'''
with shelve.open('next_wm_time') as shelf_file:
  # 変数を取得する
  day = shelf_file['day']
  hour = shelf_file['hour']
  min = shelf_file['min']
  print(day)
  print(hour)
  print(min)
  d_today = datetime.date.today().strftime('%m-%d')
  print(d_today)
  print(datetime.datetime.strptime(day, '%m/%d').strftime('%m-%d'))
  print(datetime.datetime.strptime(day, '%m/%d').strftime('%m-%d') == d_today)

with shelve.open('next_fl_time') as shelf_file:
  # 変数を取得する
  day = shelf_file['day']
  hour = shelf_file['hour']
  min = shelf_file['min']
  print(day)
  print(hour)
  print(min)
  day_op = datetime.datetime.strptime(day,
                                      '%m/%d') - datetime.timedelta(days=2)
  print(day_op.strftime('%m-%d'))
'''