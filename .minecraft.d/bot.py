import discord

_TOKEN = ''  # Add the token here
client = discord.Client()

@client.event
async def on_connect():
    await client.change_presence(activity=discord.Game(name='Server Online'))

@client.event
async def on_disconnect():
    await client.close()

if __name__ == '__main__':
    client.run(_TOKEN)
