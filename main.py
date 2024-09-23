import os
import random

import discord
import requests
from environs import Env
from replit import db

env = Env()
env.read_env()
intents = discord.Intents.default()
#intents.message_content = True
client = discord.Client(intents=intents)

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
happy_words = ["happy", "joyful", "cheerful", "delighted", "glad"]

starter_encouragements = [
    "Cheer up!", "Hang in there.", "You are a great person / bot!"
]

starter_gratefullness = [
    "Happy for you!", "You are amazing!", "You are awesome!"
]

if "responding" not in db:
  db["responding"] = True


def get_quote():
  try:
    response = requests.get("https://zenquotes.io/api/random")
    response.raise_for_status()
    json_data = response.json()
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote
  except requests.RequestException as e:
    print(f"Error fetching quote: {e}")
    return "Sorry, I couldn't get a quote at the moment."


def update_encouragements(encouraging_message):
  if "encouragements" in db:
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]


def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
  db["encouragements"] = encouragements


@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith("$inspire"):
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db:
      options += db["encouragements"]

    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

    gratefullness = starter_gratefullness
    if "gratefullness" in db:
      gratefullness += db["gratefullness"]

    if any(word in msg for word in happy_words):
      await message.channel.send(random.choice(gratefullness))

  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ", 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  if msg.startswith("$del"):
    try:
      index = int(msg.split("$del ", 1)[1])
      delete_encouragement(index)
      encouragements = db["encouragements"]
      await message.channel.send(encouragements)
    except (ValueError, IndexError):
      await message.channel.send("Please provide a valid index to delete.")

  if msg.startswith("$list"):
    encouragements = db.get("encouragements", [])
    if encouragements:
      await message.channel.send("\n".join(encouragements))
    else:
      await message.channel.send("No encouragements found.")

  if msg.startswith("$responding"):
    value = msg.split("$responding ", 1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")


TOKEN = os.getenv("TOKEN")
if TOKEN is None:
  print("Error: TOKEN is not set in the environment.")
  exit(1)

client.run(TOKEN)
