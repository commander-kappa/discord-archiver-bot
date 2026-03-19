import os; from os import path
import json
import requests
import discord as dc

DIR_PATH = f"{path.dirname(path.abspath(__file__))}"
OUTPUT_PATH = path.join(DIR_PATH, 'output')

TOKEN = ''
ADMIN_ID = ''
try:
    with open(path.join(DIR_PATH, 'TOKEN'), 'r') as t:
        TOKEN = t.readline()
except Exception as e:
    print(f"ERROR Could not read TOKEN file: {e}")
    exit()

try:
    with open(path.join(DIR_PATH, 'ADMIN'), 'r') as a:
        ADMIN_ID = a.readline()
except Exception as e:
    print(f"WARNING Could not read ADMIN file: {e}")

def create_server_dir(server_id: int) -> None:
    server_id = str(server_id)
    SERVER_DIR = path.join(OUTPUT_PATH, str(server_id))

    os.makedirs(SERVER_DIR, exist_ok=True)
    os.makedirs(path.join(SERVER_DIR, 'attachments'), exist_ok=True)

def format_channel_header(channel: dc.TextChannel) -> dict:
    return {
        "id": channel.id,
        "name": channel.name,
        "type": str(channel.type),
        "category": channel.category.name,
        "topic": channel.topic,
        "position": channel.position,
        "timestamp": channel.created_at.isoformat(),
    }

def get_server_info():
    pass

def format_message(message: dc.Message) -> dict:
    #Convert a Discord message to a standardized dictionary format.
    #Handles escaping and special characters automatically via JSON.

    return {
        "timestamp": message.created_at.isoformat(),
        "author": {
            "id": message.author.id,
            "name": message.author.name,
            "discriminator": message.author.discriminator,
            "is_bot": message.author.bot
        },
        "id": message.id,
        "content": message.content,
        "attachments": [
            {
                "id": att.id,
                "filename": att.filename,
                "url": att.url,
                "size": att.size
            }
            for att in message.attachments
        ],
        "embeds_count": len(message.embeds),
        "reactions": [
            {
                "emoji": str(reaction.emoji),
                "count": reaction.count
            }
            for reaction in message.reactions
        ],
        "is_reply": message.reference is not None,
        "edited_at": message.edited_at.isoformat() if message.edited_at else None
    }

def download_attachment(server_id:int, url:str, att_id:int, name:str) -> None:
    file_name = f"{str(att_id)}_{name}"
    ATTACHMENT_PATH = path.join(OUTPUT_PATH, str(server_id), 'attachments', file_name)
    if path.exists(ATTACHMENT_PATH):
        print(f"Attachment <{att_id}> already downloaded")
        return
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(ATTACHMENT_PATH, 'wb') as f:
            print(f"Downloaded Attachment: {ATTACHMENT_PATH}")
            f.write(response.content)
    
    except Exception as e:
        print(f"ERROR: Could not save attachment ({e})")

def write_buffer_to_file(server: dc.Guild, channel: dc.TextChannel, buffer: list[dict]) -> None:
    create_server_dir(str(server.id))

    try:
        #Overwrites (!) archive.jsonl file
        ARCHIVE_FILE = path.join(OUTPUT_PATH, str(server.id), f"{str(channel.id)}.jsonl")

        with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(format_channel_header(channel)) + "\n")
            for msg in buffer:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
                
                for att in msg['attachments']:
                    download_attachment(server.id, att['url'], att['id'], att['filename'])

        print(f"Archived {len(buffer)} messages to {ARCHIVE_FILE}")
    
    except Exception as e:
        print(f"ERROR: writing to archive file failed: {e}")

async def archive_channel(server: dc.Guild, channel: dc.channel) -> None:
    print(f'archiving: [{server.name}] #{channel.name}')

    buffer = []
    
    async for msg in channel.history():
        buffer.append(format_message(msg))
    
    buffer.reverse()
    write_buffer_to_file(server, channel, buffer)

def isAdmin(user = dc.Member) -> bool:
    out = False
    if str(user.id) == ADMIN_ID:
        print(f"@<{user.id}> is defined in ADMIN file")
        out = True
    if user.guild_permissions.administrator:
        print(user.guild_permissions.administrator)
        print(f"@{user.name} is Admin on this Server")
        out = True
    return out

class MyClient(dc.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
    
    async def on_message(self, msg):
        print(f"[{msg.guild.name}]#{msg.channel.name} @{msg.author.name}: {msg.content}")
        
        if msg.content.startswith('$archive'):
            print(f'archive triggered by @{msg.author.name}')
            if not isAdmin(msg.author):
                await msg.channel.send('YOU ARE NOT ADMIN!')
            else:
                await archive_channel(msg.guild, msg.channel)
        
        if msg.content.startswith('$archiveAll'):
            print(f'archiveAll triggered by @{msg.author.name}')
            if not isAdmin(msg.author):
                await msg.channel.send('YOU ARE NOT ADMIN!')
            else:
                await msg.channel.send('Archiving Server!')
                for channel in msg.guild.text_channels:
                    await archive_channel(msg.guild, channel)
                print(f"Finished Achiving [{msg.guild.name}]")


intents = dc.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)