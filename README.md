# Discord Archiver Bot

A Python-based Discord bot that enables server administrators to efficiently archive their entire Discord server—including all channels, messages, attachments, and metadata—for permanent preservation and offline access.

## Table of Contents

- [Features](#features)
- [Stack](#stack)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Features

- **Full Server Archival**: Archive all text channels in your server in a single command
- **Selective Archival**: Archive individual channels as needed
- **Attachment Preservation**: Automatically download and save all message attachments
- **Rich Message Data**: Capture complete message metadata including:
  - Author information and timestamps
  - Reactions and embeds
  - Message replies and edit history
  - Message IDs for reference
- **JSONL Output**: Machine-readable archive format for easy parsing and processing
- **Human-Readable Exports**: Convert archived data to readable text format
- **Channel Cleanup**: Clear channel content while preserving structure
- **Admin-Only Access**: Role-based access control for archive operations

## Stack

- **Language**: [![Python](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](https://www.python.org/)  
- **Discord Integration**: [![discord.py](https://img.shields.io/badge/discord.py-2.7%2B-blue?logo=discord)](https://discordpy.readthedocs.io/en/stable/)  
- **Data**: Stored in JSONL files following an ID based directory format 
- **Build/Package Manager**: [UV](https://docs.astral.sh/uv/) 

## Installation
1. Clone the Repository
    ```bash
    git clone https://codeberg.org/kappa-dev/discord-archiver-bot
    ```

2. Activate the virtual environment and install dependencies with [UV](https://docs.astral.sh/uv/):
    ```bash
    uv sync
    ```

3. Obtain a Discord Bot Token
    1. Go to the Discord Developer Portal
    2. Create a new application
    3. Navigate to the "Bot" section and create a bot
    4. Copy your bot token (keep this private!)
    5. Under "OAuth2" "URL Generator", select:
        - Scopes: bot, applications.commands
        - Permissions: Read Messages/View Channels, Read Message History, Send Messages, Attach Files, Manage Channels, Manage Messages

4. Run the setup script to create the necessary directory structure and configuration
    ```bash
    uv run setup.py
    ```

    This will prompt you to enter:
    1. TOKEN File
    Your Discord bot token. The bot will create a TOKEN file in the root directory.

    2. ADMIN File
    Discord user IDs of administrators who can execute archive commands. One ID per line.
    To find your Discord user ID:
        1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
        2. Right-click on your username and select "Copy User ID"

### Directory Structure
After setup, your project will have the following structure:
```
discord-archiver-bot/
├── main.py                     # Main bot file
├── setup.py                    # Setup and configuration script
├── convert_history.py          # History conversion module
├── TOKEN                       # Bot token (DO NOT COMMIT)
├── ADMIN                       # Admin user IDs 
├── output/                     # Archive output directory
│   └── {server_id}/            # Directory per archived server
│       ├── {channel_id}.jsonl  # Channel archive
│       └── attachments/        # Downloaded attachments
```

## Usage
### Running the Bot

```bash
uv run main.py
```
The bot will connect to Discord and make slash commands available in any server where it has permission.

### Accessing Commands

In Discord, use the `/` command prefix to access the bot's commands. All commands are restricted to administrators defined in your `ADMIN` file.

#### `/archive_channel`
Archives all messages from a specific text channel.

**Parameters:**
- `channel` (optional): The channel to archive. Defaults to the current channel.
- `with_attachments` (boolean, default: `True`): Whether to download and save attachments.

**Example:**
```
/archive_channel channel:#general with_attachments:true
```

**Output:** Messages are saved to `output/{server_id}/{channel_id}.jsonl`

#### `/archive_server`
Archives all text channels in the entire server.

**Parameters:**
- `with_attachments` (boolean, default: `True`): Whether to download and save attachments.

**Example:**
```
/archive_server with_attachments:true
```

**Output:** One `.jsonl` file per channel in `output/{server_id}/`

#### `/make_history`
Converts channel archive to a human-readable text format.

**Parameters:**
- `channel` (optional): The channel to export history from. Defaults to the current channel.
- `as_file` (boolean, default: `True`): Whether to send as a downloadable file or as Discord messages.

**Example:**
```
/make_history channel:#general as_file:true
```

**Output:** 
- If `as_file:true`: Sends a `.txt` file with formatted messages
- If `as_file:false`: Sends messages directly to Discord (split if exceeding message length limits)


#### `/clear_channels`
Clears all messages from channels matching a substring pattern. Useful for cleanup operations.

**Parameters:**
- `substring` (required): Pattern to match channel names.
- `do_it` (boolean, default: `False`): If `false`, shows matching channels without action. Set to `true` to execute.
- `delete_old` (boolean, default: `False`): Whether to delete old channels or rename them with `-old` suffix.

**Example (dry run):**
```
/clear_channels substring:test do_it:false
```

**Example (execute):**
```
/clear_channels substring:test do_it:true delete_old:false
```


## License
This project is licensed under the **GNU General Public License v3.0** - see the `LICENSE` file for details.

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bug reports and feature suggestions.

## Contact
Maintained by kappa-dev — codeberg@kappa-dev.de
