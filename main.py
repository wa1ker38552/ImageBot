from discord.ext import commands
from bs4 import BeautifulSoup
from discord.utils import get
from replit import db
import requests
import discord
import time
import os

db['reactionpages'] = {}
client = commands.Bot(command_prefix='.', help_command=None)
process_time = 0

def query_image(query):
  links, urls = [], []

  htmldata = requests.get(
    f"https://www.google.com/search?q={query}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjF-KC3wYf3AhXoJ0QIHZ4hDJQQ_AUoAnoECAIQBA&biw=1745&bih=861&dpr=1.1"
  ).text
  soup = BeautifulSoup(htmldata, 'html.parser')
  for item in soup.find_all('img'):
    links.append(item['src'])
  print(links)
  for i in range(len(links)): # parse links
    try:
      if links[i][0:5] == 'https':
        urls.append(links[i])
    except: pass
  return urls

@client.event
async def on_ready():
  print(client.user)

@client.event
async def on_message(message):
  global process_time
  process_time = time.time()
  await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):
  if user != client.user:
    if str(reaction.message.id) in db['reactionpages']:
      object = db['reactionpages'][str(reaction.message.id)]
      embed = discord.Embed()
      if reaction.emoji == '⬅️':
        embed.set_image(url=object[1][object[0]-1])
        db['reactionpages'][str(reaction.message.id)][0]-=1
      elif reaction.emoji == '➡️':
        embed.set_image(url=object[1][object[0]+1])
        db['reactionpages'][str(reaction.message.id)][0]+=1
      await reaction.message.clear_reactions()
      await reaction.message.edit(embed=embed)
      await reaction.message.add_reaction('⬅️')
      await reaction.message.add_reaction('➡️')
    

@client.command()
async def debug(ctx):
  global process_time
  embed = discord.Embed()
  embed.title = 'Debug'
  embed.description = f'Latency: `{round(client.latency, 3)} ms`\nProcess Time: `{round(time.time()-process_time, 3)} ms`'
  embed.color = 0xc7c7c7
  await ctx.channel.send(embed=embed)

@client.command()
async def embed(ctx):
  msg = str(ctx.message.content)
  embed = discord.Embed()
  embed.title = msg.split('\n')[1]
  embed.description = '\n'.join(msg.split('\n')[2:])
  embed.color = 0xc7c7c7
  await ctx.channel.send(embed=embed)
  await ctx.message.delete()

@client.command()
async def image(ctx, *query):
  urls = query_image('+'.join(query))
  embed = discord.Embed()
  embed.set_image(url=urls[0])
  m = await ctx.channel.send(embed=embed)
  await m.add_reaction('⬅️')
  await m.add_reaction('➡️')
  print(len(urls))
  db['reactionpages'][str(m.id)] = [0, urls]

@client.command()
async def help(ctx):
  embed = discord.Embed()
  embed.title = 'UtilityBot Help'
  embed.description = '''
Commands for UtilityBot

`.image`: Queries image with paremeters

`.debug`: Shows debug information
`.help`: Shows help page
  '''
  embed.color = 0xc7c7c7
  await ctx.channel.send(embed=embed)

client.run(os.environ['TOKEN'])
