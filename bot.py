import os
import discord
import openai
import asyncio
from discord import app_commands
from dotenv import load_dotenv
from stateful import *
from interpret import *

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

openai.api_key = OPENAI_KEY

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
  await tree.sync()
  print("We have logged in as {0.user}".format(client))

@tree.command(name = "commandname", description = "My first application Command")# guild=discord.Object(id=12417128931)
async def first_command(interaction):
  print(interaction.response.send_message.__code__.co_varnames)
  await interaction.response.send_message("Hello!",ephemeral=True)



@client.event
async def on_message(message):
  if message.author == client.user: return
  if not message.guild:
    try:
      await message.channel.send("No DM support.")
    except discord.errors.Forbidden:
      return
  channel = message.channel or ctx.channel
  if "test" not in channel.name.lower() or "chamber" not in channel.name.lower(): return
  guild = message.guild or ctx.guild


  await asyncio.sleep(3)

  hist = [a async for a in channel.history(limit=10)]

  if hist[0] != message: return
  # trunc = next((i for i,v in enumerate(hist) if v.author==client.user),None)
  # if trunc!=None: hist = hist[:trunc]
  hist = hist[::-1]

  placeholder = await channel.send('[crafting response...]')


  memchannel = await getMemoryChannel("bot_memory",message.guild)
  state = await retrieveState(memchannel,client)


  unique_authors = list(set(h.author for h in hist if h.author!=client.user))
  readable_names = {}
  for author in unique_authors:
    key = "user"+shortid(author.id)
    if key not in state.keys():
      state[key] = author.name.replace(" ","")
    readable_names[author.id] = state[key]

  lines = []
  for mes in hist:
    authname = "Jambot" if mes.author == client.user else readable_names[mes.author.id]
    for line in mes.content.split("\n"):
      lines.append(f"{authname}: {line}")
  body = "\n".join(lines)

  intentions = {}
  for author in unique_authors:
    intentions[author.id] = f"{readable_names[author.id]}'s intentions are "+interpret_answer_no_convo(openai.Completion.create(
      engine="text-davinci-003",
      prompt=f"""
{body}

What are {readable_names[author.id]}'s intentions?
{readable_names[author.id]}'s intentions are
""".strip(),
      max_tokens=500,
      temperature=0.7,
    ).choices[0].text.strip(),readable_names.values())

  doublenewl = "\n\n"

  bot_intention = "Jambot's short-term intention is "+interpret_answer_no_convo(openai.Completion.create(
    engine="text-davinci-003",
    prompt=f"""
A conversation is taking place between Jambot and his friends.

Jambot's long-term intentions are to do a game jam with his friends. That will only happen if his friends like him and are in a creative mood, so he needs to be fun to talk to and encourage creativity.

{doublenewl.join([readable_names[author.id].strip() for author in unique_authors])}

What is Jambot's short-term intention?
Jambot's short-term intention is
""".strip(),
    max_tokens=500,
    temperature=0.7,
  ).choices[0].text.strip(),readable_names.values())


  for attempt in range(2):

    nextlines = interpret_conversation_completion(openai.Completion.create(
      engine="text-davinci-003",
      prompt=f"""
A conversation is taking place between Jambot and his friends.

f{bot_intention}

{body}
""".strip(),
      max_tokens=500,
      temperature=0.7,
    ).choices[0].text.strip(),readable_names.values())
    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"*4)
    print(body)
    print(intentions)
    print(bot_intention)
    print(nextlines)

    if nextlines:
      if nextlines.endswith(" What do you think?"):
        nextlines = nextlines[:-len(" What do you think?")]
      if nextlines.endswith(" What do you all think?"):
        nextlines = nextlines[:-len(" What do you all think?")]
      await placeholder.edit(content=nextlines)
      break
  else:
    await placeholder.delete()

  await saveState(memchannel,client,state)

  # old_overwrite = channel.overwrites_for(guild.default_role)
  # old_overwrite.send_messages = True
  # overwrite = channel.overwrites_for(guild.default_role)
  # overwrite.send_messages = False
  # await channel.set_permissions(client.user, overwrite=old_overwrite)
  # await channel.set_permissions(guild.default_role, overwrite=overwrite)


  # await channel.set_permissions(guild.default_role, overwrite=old_overwrite)

  return

  # await message.channel.send("response")


  # print(message)#create_text_channel
  # print(dir(message.guild))




# There is a conversation in a group chat with Lilac and Jambot.
# Lilac is a cool gal.

# Jambot's long-term intentions are to do a game jam with Lilac. That will only happen if Lilac likes him and is in a creative mood, so he needs to be fun to talk to and encourage creativity.

# Lilac appears to be suggesting that they can have fun by changing their nicknames and creating new channels whenever they want. She also encourages people to make decisions on where the new channels should go.

# What might Jambot's short-term intentions be?

# Jambot's short-term intentions might be to keep the conversation going by suggesting fun activities, such as creating new nicknames and creating new channels. He could also ask Lilac for her opinion on where the new channels should go, or ask her for ideas on other fun activities they could do. Additionally, he could ask her about her creative interests to better gauge her mood and enthusiasm for a game jam.


  # response = openai.Completion.create(
  #   engine="text-davinci-003",
  #   prompt=f"{message.content}",
  #   max_tokens=500,
  #   temperature=0.7,
  # ).choices[0].text





  # for channel in message.guild.text_channels:
  #   print("found channel: ",channel,dir(channel),channel.created_at)
  #   print("-=-=-")
  #   print(channel.name=="general")
  #   print(channel.type=="text")
  #   print(channel.members)
  #   print(channel.permissions_for)
  #   print("-=-=-")


      # text_channel_list.append(channel)


  # print([a for a in dir(message.guild) if a.startswith('create')])
  # print(message.guild.create_category.__code__.co_varnames)
  return
  # memory = retrieveState("botmemory")

  # targetthread = None
  # for thread in message.channel.threads:
  #   print("found a thread!",thread)
  #   async for message in thread.history():
  #     if message.author != client.user: continue
  #     print("me message: ",message)
  #   await thread.send("this is some test data!")
  #what if thread creation would fail due to unique thread names?
  if client.user not in message.mentions: return

  # Check if the bot is mentioned in the message
  # if client.user in message.mentions:

  response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=f"{message.content}",
    max_tokens=500,
    temperature=0.5,
  )

  # Send the response as a message
  await message.channel.send(response.choices[0].text)

# start the bot
client.run(TOKEN)











