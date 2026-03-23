import os; from os import path
import json
import requests
import io
import discord as dc
import convert_history
import setup

DISCORD_MAX_MESSAGE_LENGTH = 2000

DIR_PATH = f"{path.dirname(path.abspath(__file__))}"
OUTPUT_PATH = path.join(DIR_PATH, 'output')

TOKEN = ''
ADMINS = []


def create_server_dir(server_id: int) -> None:
    server_id = str(server_id)
    SERVER_DIR = path.join(OUTPUT_PATH, str(server_id))

    os.makedirs(OUTPUT_PATH, exist_ok=True)
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

def write_buffer_to_file(channel:dc.TextChannel, buffer:list[dict], with_attachments:bool = True) -> None:
    server = channel.guild
    create_server_dir(str(server.id))

    try:
        #Overwrites (!) archive.jsonl file
        ARCHIVE_FILE = path.join(OUTPUT_PATH, str(server.id), f"{str(channel.id)}.jsonl")

        with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(format_channel_header(channel)) + "\n")
            
            for msg in buffer:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
                
                if with_attachments:
                    for att in msg['attachments']:
                        download_attachment(server.id, att['url'], att['id'], att['filename'])
        
        print(f"Archived {len(buffer)} messages to {ARCHIVE_FILE}")
    
    except Exception as e:
        print(f"ERROR: writing to archive file failed: {e}")

async def archive_channel(channel:dc.channel) -> list[dict]:
    print(f'archiving: [{channel.guild.name}] #{channel.name}')

    buffer = []
    
    async for msg in channel.history(limit=None):
        buffer.append(format_message(msg))
    
    buffer.reverse()
    return buffer

def isAdmin(user = dc.Member) -> bool:
    out = False
    if str(user.id) in ADMINS:
        print(f"@<{user.id}> is defined in ADMIN file")
        out = True
    return out

class MyClient(dc.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_message(self, msg):
        print(f"[{msg.guild.name}]#{msg.channel.name} @{msg.author.name}: {msg.content}")


intents = dc.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
tree = dc.app_commands.CommandTree(client)

@tree.command(name="archive_channel", description="Archive a channel")
async def archive(
    interaction: dc.Interaction,
    channel: dc.TextChannel = None,
    with_attachments: bool = True
):

    if channel is None:
        channel = interaction.channel

    if not isAdmin(interaction.user):
        await interaction.response.send_message("YOU ARE NOT ADMIN!", ephemeral=True)
        return

    await interaction.response.defer()
    
    write_buffer_to_file(
        channel = channel,
        buffer = await archive_channel(channel), 
        with_attachments = with_attachments
    )
    
    await interaction.followup.send(f"Archived #{channel.name}!")

@tree.command(name="archive_server", description="Archive all channels in the server")
async def archive_all(interaction: dc.Interaction, with_attachments: bool = True):
    
    if not isAdmin(interaction.user):
        await interaction.response.send_message("YOU ARE NOT ADMIN!", ephemeral=True)
        return

    await interaction.response.defer()
    await interaction.followup.send("Archiving server...")
    
    for channel in interaction.guild.text_channels:
        write_buffer_to_file(
            channel = channel,
            buffer = await archive_channel(channel),
            with_attachments = with_attachments
        )

    await interaction.followup.send("Server archived!")

@tree.command(name="make_history", description="Sends channel history")
async def make_history_file(
    interaction: dc.Interaction,
    channel: dc.TextChannel = None,
    as_file: bool = True
):
    if channel is None:
        channel = interaction.channel

    if not isAdmin(interaction.user):
        await interaction.response.send_message("YOU ARE NOT ADMIN!", ephemeral=True)
        return

    await interaction.response.defer()
    await interaction.followup.send("Generating history file...")


    buffer = await archive_channel(channel)
    
    if as_file:
        inMemoryFile = io.BytesIO()
        writer = io.BufferedWriter(raw=inMemoryFile)

        for message in buffer:
            writer.write(f"{convert_history.format_message(message)}\n".encode('utf-8'))
        
        writer.flush()
        inMemoryFile.seek(0)

        await interaction.followup.send(
            content = f"#{channel.name} history file",
            file = dc.File(fp = inMemoryFile, filename='history.txt')
        )
        
        inMemoryFile.close()
    
    else:
        response_buffer = ""
        response_list = []
        
        for message in buffer:
            response = f"{convert_history.format_message(message)}\n"
            
            if len(response_buffer) + len(response) > DISCORD_MAX_MESSAGE_LENGTH:
                response_list.append(response_buffer[:-1])
                response_buffer = ""

            response_buffer += response

        for response in response_list:
            await interaction.followup.send(content = response)



if __name__ == '__main__':
    setup.create_dir_structure(DIR_PATH)
    
    try:
        with open(path.join(DIR_PATH, 'TOKEN'), 'r') as file:
            TOKEN = file.readline()
    except Exception as e:
        print(f"ERROR: Could not read TOKEN file\n{e}")
        exit()

    try:
        with open(path.join(DIR_PATH, 'ADMIN'), 'r') as file:
            for admin in file:
                if not setup.validate_user_id_string(admin, verbose=False):
                    continue
                else:
                    ADMINS.append(admin.rstrip('\n'))
        if len(ADMINS) == 0:
            print('WARNING: No valid user ID found in ADMIN file!')
    except Exception as e:
        print(f"WARNING: Could not read ADMIN file\n{e}")

    client.run(TOKEN)