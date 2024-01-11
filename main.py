import discord
from discord import message
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from keep_alive import keep_alive
import urllib.parse
import aiohttp
import datetime
from datetime import time, timedelta, timezone
import pandas
import shelve

intents = discord.Intents.default()
intents.message_content = True

past_url = 'null'
past_updateinfo = 'null'
past_live_code = 'null'
past_json = 'null'
flag = 'false'
JST = timezone(timedelta(hours=+9), "JST")
times = [datetime.time(hour=11, minute=0, tzinfo=JST)]

client = discord.Client(intents=intents)

sc_channel = "1180364912002863164"

@client.event
async def on_ready():
  print(f'起動完了。今日も素敵なスクールアイドル応援ライフを。')
  channel = client.get_channel(1178586650360696912)
  url = 'https://link-like-lovelive.app/api/news.json'
  r = requests.get(url)
  text = r.text
  data = json.loads(text)
  id_list = [d.get('id') for d in data]
  id_list.reverse()
  global past_url, past_updateinfo, flag
  messages = [message async for message in channel.history(limit=1)]
  text2 = ' '.join(map(str, messages))
  msg_id = re.search(r'\d+', text2)
  last_msg = await channel.fetch_message(msg_id.group())
  last_msg_content = last_msg.embeds[0].url
  past_url = last_msg_content
  for id in id_list:
    str_updateinfo = id
    str_url = 'https://link-like-lovelive.app/news/%s' % str_updateinfo
    if (str_url == past_url):
      flag = 'true'
      past_updateinfo = str_updateinfo
      continue
    if (str_url != past_url and flag == 'true'):
      async with aiohttp.ClientSession() as session:
        async with session.get(str_url) as r2:
          soup = BeautifulSoup(await r2.text(), "html.parser")
          title = soup.select(
              '#root > div > article > section:nth-child(3) > h3')[0]
          desc = soup.select(
              '#root > div > article > section:nth-child(3) > div')[0]
          date = soup.select(
              '#root > div > article > section:nth-child(2) > h2')[0]
          img_url = 'https://assets.link-like-lovelive.app/news/img/'
          embed = discord.Embed(title=title.get_text(),
                                description=desc.get_text().replace(
                                    "　", "\n").replace("・", "\n・").replace(
                                        '&lt;', '<').replace('&gt;', '>'),
                                url=str_url,
                                color=0xf6d1d9)
          embed.add_field(name='date',
                          value=re.search(r'\d*?/\d*?/\d*? \d+:\d+',
                                          date.get_text()).group())
          if (soup.find('img')):
            for img in soup.find_all('img'):
              link = img.get('src')
              abs_url = urllib.parse.urljoin(img_url, link)
              embed.set_image(url=abs_url)
          await channel.send("お知らせが更新されました。")
          await channel.send(embed=embed)
          #re.sub(r'<.*?>', r'', )
          print('更新あり')
    else:
      print('更新なし')

  channel2 = client.get_channel(1180364912002863164)
  messages = [str(message) async for message in channel2.history(limit=50)]
  text_filter = [s for s in messages if r'ComebackTwitterEmbed' in s]
  id_dic = []
  for text in text_filter:
    id_dic.append(text[:text.find(' c') + len(' c')])
  id_list = []
  for id in id_dic:
    id_list.append(re.search('\d+', id).group())
  for id in id_list:
    last_msg = await channel2.fetch_message(id)
    last_msg_desc = last_msg.embeds[0].description
    if re.search(
        r'(?m)(?s)^(?=.*予告)(?=.*With×MEETS)(?=.*([0-9]|1[0-9]|2[0-3]):[0-5][0-9]より配信).*$',
        last_msg_desc):
      day = re.search(r'(?m)([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])\(',
                      last_msg_desc).group().replace('(', '')
      hhmm = re.search(r'(?m)^.*([0-9]|1[0-9]|2[0-3]):[0-5][0-9].*$',
                       last_msg_desc).group()
      hour = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):',
                       str(hhmm)).group().replace(':', '')
      min = re.search(r'(?m)(:[0-5][0-9])', str(hhmm)).group().replace(':', '')
      with shelve.open('next_wm_time', writeback=True) as shelf_file:
        shelf_file['day'] = day
        shelf_file['hour'] = hour
        shelf_file['min'] = min
      break
  for id in id_list:
    last_msg = await channel2.fetch_message(id)
    last_msg_desc = last_msg.embeds[0].description
    if re.search(
        r'(?m)(?s)^(?=.*開催決定)(?=.*([1-9]|1[0-2])月度Fes×LIVE)(?=.*場所:Link！Like！ラブライブ！).*$',
        last_msg_desc):
      day = re.search(r'(?m)([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])\(',
                      last_msg_desc).group().replace('(', '')
      hhmm = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):[0-5][0-9]', last_msg_desc)
      hour = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):',
                       str(hhmm)).group().replace(':', '')
      min = re.search(r'(?m)(:[0-5][0-9])', str(hhmm)).group().replace(':', '')
      with shelve.open('next_fl_time', writeback=True) as shelf_file:
        shelf_file['day'] = day
        shelf_file['hour'] = hour
        shelf_file['min'] = min
      break
  loop1.start()
  notice_wm.start()
  notice_fl.start()


@tasks.loop(minutes=5)
async def loop1():
  channel = client.get_channel(1178586650360696912)
  url = 'https://link-like-lovelive.app/api/news.json'
  r = requests.get(url)
  text = r.text
  data = json.loads(text)
  id_list = [d.get('id') for d in data]
  id_list.reverse()
  global flag
  flag = 'false'
  for id in id_list:
    str_updateinfo = id
    print(str_updateinfo)
    global past_updateinfo
    print(past_updateinfo)
    if (str_updateinfo == past_updateinfo):
      flag = 'true'
      continue
    if (str_updateinfo != past_updateinfo and flag == 'true'):
      past_updateinfo = str_updateinfo
      url2 = 'https://link-like-lovelive.app/news/%s' % str_updateinfo
      r2 = requests.get(url2)
      soup = BeautifulSoup(r2.content, "html.parser")
      title = soup.select(
          '#root > div > article > section:nth-child(3) > h3')[0]
      messages = [message async for message in channel.history(limit=1)]
      text2 = ' '.join(map(str, messages))
      msg_id = re.search(r'\d+', text2)
      last_msg = await channel.fetch_message(msg_id.group())
      last_msg_content = last_msg.embeds[0].title
      if (last_msg_content != title.get_text()):
        desc = soup.select(
            '#root > div > article > section:nth-child(3) > div')[0]
        date = soup.select(
            '#root > div > article > section:nth-child(2) > h2')[0]
        img_url = 'https://assets.link-like-lovelive.app/news/img/'
        embed = discord.Embed(title=title.get_text(),
                              description=desc.get_text().replace(
                                  "　", "\n").replace("・", "\n・").replace(
                                      '&lt;', '<').replace('&gt;', '>'),
                              url=url2,
                              color=0xf6d1d9)
        embed.add_field(name='date',
                        value=re.search(r'\d*?/\d*?/\d*? \d+:\d+',
                                        date.get_text()).group())
        if (soup.find('img')):
          for img in soup.find_all('img'):
            link = img.get('src')
            abs_url = urllib.parse.urljoin(img_url, link)
            embed.set_image(url=abs_url)
        await channel.send("お知らせが更新されました。")
        await channel.send(embed=embed)
        #re.sub(r'<.*?>', r'', )
        print('更新あり')
      else:
        print('更新なし')
    else:
      print('更新なし')
  dt_now = datetime.datetime.now(datetime.timezone(
      datetime.timedelta(hours=9)))
  print('更新完了 %s' % dt_now.strftime('%Y年%m月%d日 %H:%M:%S'))


@client.event
async def on_message(message):
  global sc_channel
  if (str(message.author) == 'ComebackTwitterEmbed#3134'):
    if (message.channel.id == int(sc_channel)):
      last_msg_desc = message.embeds[0].description
      if re.search(
          r'(?m)(?s)^(?=.*予告)(?=.*With×MEETS)(?=.*([0-9]|1[0-9]|2[0-3]):[0-5][0-9]より配信).*$',
          last_msg_desc):
        day = re.search(r'(?m)([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])\(',
                        last_msg_desc).group().replace('(', '')
        hhmm = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):[0-5][0-9]', last_msg_desc)
        hour = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):',
                         str(hhmm)).group().replace(':', '')
        min = re.search(r'(?m)(:[0-5][0-9])', str(hhmm)).group().replace(':', '')
        with shelve.open('next_wm_time', writeback=True) as shelf_file:
          shelf_file['day'] = day
          shelf_file['hour'] = hour
          shelf_file['min'] = min
          print("With×MEETSの配信日時データを更新しました。")
      elif re.search(
          r'(?m)(?s)^(?=.*開催決定)(?=.*([1-9]|1[0-2])月度Fes×LIVE)(?=.*Link！Like！ラブライブ！).*$',
          last_msg_desc):
        day = re.search(r'(?m)([1-9]|1[0-2])/([1-9]|[12][0-9]|3[01])\(',
                        last_msg_desc).group().replace('(', '')
        hhmm = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):[0-5][0-9]', last_msg_desc)
        hour = re.search(r'(?m)([0-9]|1[0-9]|2[0-3]):',
                         str(hhmm)).group().replace(':', '')
        min = re.search(r'(?m)(:[0-5][0-9])', str(hhmm)).group().replace(':', '')
        with shelve.open('next_fl_time', writeback=True) as shelf_file:
          shelf_file['day'] = day
          shelf_file['hour'] = hour
          shelf_file['min'] = min
          print("Fes×LIVEの配信日時データを更新しました。")

  elif (message.author != client.user):
    member_number = {
        '日野下花帆': '01',
        '乙宗梢': '03',
        '村野さやか': '02',
        '夕霧綴理': '04',
        '大沢瑠璃乃': '05',
        '藤島慈': '06',
    }
    mes = message.content
    if mes in member_number:
      num = member_number[mes]
      url = "https://lovelive-anime.jp/hasunosora/member/%s" % num
      r = requests.get(url)
      soup = BeautifulSoup(r.content, "html.parser")
      prof = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__text > p'
          % num)
      member_color = {
          '01': 0xf8b500,
          '03': 0x68be8d,
          '02': 0x5383c3,
          '04': 0xba2636,
          '05': 0xe7609e,
          '06': 0xc8c2c6,
      }
      col = member_color[num]
      grade = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__personal > dl:nth-child(1) > dd'
          % num)
      birth = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__personal > dl:nth-child(2) > dd'
          % num)
      height = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__personal > dl:nth-child(3) > dd'
          % num)
      hobby = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__personal > dl:nth-child(4) > dd'
          % num)
      spabi = soup.select(
          '#chara--%s > div > div.detail__spec > div.detail__spec__prof > div.detail__spec__prof__personal > dl:nth-child(5) > dd'
          % num)
      embed = discord.Embed(title=mes,
                            description=prof[0].contents[0],
                            color=col)
      embed.add_field(name="学年", value=grade[0].contents[0])
      embed.add_field(name="誕生日", value=birth[0].contents[0])
      embed.add_field(name="身長", value=height[0].contents[0])
      embed.add_field(name="趣味", value=hobby[0].contents[0])
      embed.add_field(name="特技", value=spabi[0].contents[0])
      embed.set_thumbnail(
          url=
          'https://lovelive-anime.jp/hasunosora/shared/img/member/%s_thumb.png'
          % num)
      await message.channel.send(embed=embed)

    elif mes.startswith('質問！') :
      await message.channel.send('＼ｵｩﾘｬﾘｬｰﾄｰﾘｬｰﾘｬｰ／')
      


@tasks.loop(time=times)
async def notice_wm():
  d_today = datetime.date.today().strftime('%m-%d')
  with shelve.open('next_wm_time') as shelf_file:
    day, hour, min = shelf_file['day'], shelf_file['hour'], shelf_file['min']
    if (datetime.datetime.strptime(day, '%m/%d').strftime('%m-%d') == d_today):
      channel = client.get_channel(1180364810483941406)
      await channel.send(
          '<@&1178584980092358698> \nWith×MEETSの配信待機場が開場しました。\n配信開始日時は%s %s:%sです。\n【注意事項】\n〇視聴・ギフトの送信忘れにご注意ください。'
          % (day, hour, min))


@tasks.loop(time=times)
async def notice_fl():
  d_today = datetime.date.today().strftime('%m-%d')
  with shelve.open('next_fl_time') as shelf_file:
    day, hour, min = shelf_file['day'], shelf_file['hour'], shelf_file['min']
  day_op = datetime.datetime.strptime(day,
                                      '%m/%d') - datetime.timedelta(days=2)
  if (day_op.strftime('%m-%d') == d_today):
    channel = client.get_channel(1180364810483941406)
    await channel.send(
        '<@&1178584980092358698> \nFes×LIVEのロビーが開場しました。\n配信開始日時は%s %s:%sです。\n【注意事項】\n〇視聴・ロビーへの入場忘れにご注意ください。\n※ロビーに入場しなかった場合、__**サークル対抗戦のプライズを受け取ることができません。**__\n　プライズを入手したい場合は必ずロビー開場中に入場してください。'
        % (day, hour, min))


keep_alive()
my_secret = os.environ['DISCODE_TOKEN']
try:
  client.run(my_secret)
except:
  os.system("kill")
