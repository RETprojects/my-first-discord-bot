# This is a Discord bot that responds to new messages.

# This code is based on the following examples:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot
# https://www.freecodecamp.org/news/create-a-discord-bot-with-python/
# https://www.reddit.com/r/Discord_Bots/comments/xt0otl/comment/j3pet6o/?utm_source=share&utm_medium=web2x&context=3

import discord
import os
import requests
import json
import random
from replit import db  # storing data using the Replit database

intents = discord.Intents.default()
intents.typing = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = [
    "Cheer up!", "Hang in there.", "You are a great person / bot!"
]

# The "responding" key will tell us whether to respond to "sad" words.
if "responding" not in db.keys():
    db["responding"] = True


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


# Functions to allow users to edit the list of encouraging messages:


# Add a custom encouragement message to the list:
def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]


# Delete an encouragement message from the list:
def delete_encouragment(index):
    encouragements = db["encouragements"]
    if len(encouragements) > index:
        del encouragements[index]
    db["encouragements"] = encouragements


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # Don't respond to a message if it's posted by yourself (the bot).
    if message.author == client.user:
        return

    msg = message.content

    # If a $hello command was just posted, say Hello!
    if msg.startswith('$hello'):
        await message.channel.send('Hello!')

    # If a $inspire command is posted, fetch a quote from the zenquotes API.
    if msg.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if db["responding"]:
        options = starter_encouragements
        # If a user has submitted an encouragement message, add it to the list.
        if "encouragements" in db.keys():
            #options = options + db["encouragements"]
            options.extend(db["encouragements"])
        # When a message appears that contains a "sad" word, post an encouraging message.
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    # If a new message starts with $new, the text after is a new encouragement message.
    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")

    # If a message starts with $del, the number after is the index of the encouragement message to be deleted.
    if msg.startswith("$del"):
        encouragements = []
        if "encouragements" in db.keys():
            index = int(msg.split("$del", 1)[1])
            delete_encouragment(index)
            encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    # The $list command displays the list of encouraging messages.
    if msg.startswith("$list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    # The $responding command takes true or false as an argument and sets the "responding" key to true if the argument is true and false otherwise.
    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]

        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off.")


# The bot will greet a new member of the server.
# This code is based on this example: https://github.com/Rapptz/discord.py/blob/master/examples/new_member.py
async def on_member_join(member):
    if member.guild.channel is not None:
        await member.guild.channel.send(
            f'Hello, {member.mention}! Welcome to {member.guild}!')


try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
