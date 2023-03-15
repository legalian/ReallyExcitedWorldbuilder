import os
import discord
import openai
import asyncio
from discord import app_commands
from dotenv import load_dotenv
from stateful import *
from interpret import *
from personal import *

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

  hist = [a async for a in channel.history(limit=8)]

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

  # bestway_memories = getpersonal(
  #   "bestway",
  #   lambda name:f"What is the best way to get {name} to participate in a game jam with you?",
  #   state,
  #   unique_authors
  # )
  game_ideas = getpersonal(
    body,
    "gameidea",
    lambda name:f"What is {name}'s idea for a game? What stops them from developing it and submitting it to a game jam?",
    state,
    unique_authors,readable_names
  )

  motivational_matrix = [f"""
Jambot: {game_ideas[author.id]}
""".strip() for author in unique_authors]

  doublenewl = "\n"

  for attempt in range(2):
    prompt=f"""
Jambot's ultimate goal is to participate in a game jam with his friends.
Here is what Jambot knows about his friends' game ideas:
{doublenewl.join(motivational_matrix)}

If something is preventing his friends from working on their game ideas, Jambot always asks what it is, and offers advice.
Jambot is inspired by his friends' creativity, and he always wants to know more about his friends' game ideas, so he sometimes subtly steers the conversation towards game ideas.

Jambot is talking with his friends in a group chat.
{body}
Jambot:
""".strip()
    print(prompt)
    nextlines = interpret_conversation_completion(openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=500,
      temperature=0.7,
    ).choices[0].text.strip(),readable_names.values())
    # print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n"*4)
    # print(body)
    # print(intentions)
    # print(nextlines)

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











