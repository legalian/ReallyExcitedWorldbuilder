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
  # game_ideas = getpersonal(
  #   body,
  #   "gameidea",
  #   lambda name:f"What is {name}'s idea for a game? What stops them from developing it and submitting it to a game jam?",
  #   state,
  #   unique_authors,readable_names
  # )
  game_ideas = getpersonal(
    body,
    "attitude",
    lambda name:f"What is {name}'s attitude towards you, videogames, and game jams?",
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

    if nextlines:
      await placeholder.edit(content=nextlines)
      break
  else:
    await placeholder.delete()

  await saveState(memchannel,client,state)
client.run(TOKEN)











