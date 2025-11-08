# Spotify TUI Control Panel

**Spotify TUI Control Panel** is a terminal-based interface that allows you to control Spotify playback directly from your terminal. With simple commands like **skip tracks**, **go back to previous tracks**, **pause/resume** playback, **view the currently playing track** etc. It provides a lightweight and intuitive way to interact with Spotify without leaving the command line.

---

## Requirements

- **Python 3** and **virtual environment**.
- **Spotify Developer account** (for API access).

---

## Supported Distros
- Debian-based
- Arch-based
- Windows 11
- All systems that can run python (with manual setup).

## Supported Shells
- bash
- powershell
- All shells that can run python (with manual setup).

---

## Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/TobyJavascript/spotify-tui-control-panel.git
cd spotify-tui-control-panel
```

### Step 2: Configure Spotify API Credentials
1. Visit Spotify Developer Dashboard: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create app (Make up your own app name, but use http://127.0.0.1:8888/callback for redirect URI).
2. Note down your **Client ID** and **Client Secret**.

### Step 3: Run the Setup Script
There are different setup scripts based on what disto you use.


This script will:
- Install required packages and dependencies.
- Set up a Python virtual environment.
- Install Python libraries listed in requirements.txt.
- Set up your Spotify API credentials (you need to fill in your Client ID, and Client Secret in the script).
- Create a shortcut command (spotuify) for easy access.
- Create `.env` file with credentials from user input.

#### Linux
The setup script supports **Debian-based** and **Arch-based** distributions.
Simply run the `linux-setup.sh` script to begin:
```bash
chmod +x linux-setup.sh
./linux-setup.sh
```
You’ll be prompted to select your distribution. Choose the option that matches your system.

#### Windows 11
**IMPORTANT:** For the Windows version, make sure Python is installed and added to PATH before running setup.
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\windows-setup.ps1
```

### Step 4: Run the Application
Once the setup is complete, you can:

#### Linux
Launch the Spotify TUI Control Panel on **linux** by running:
```bash
spotuify
```

#### Windows 11
Launch the panel on **windows** by running the batch script:
```powershell
.\spotuify.bat
```

#### Python
Or manually run the python script:
```bash
python spotify_controller.py
```
---

## Usage
Once running, you can use the following commands to control playback:
- `next`: Skip to the next track.
- `prev`: Go back to the previous track.
- `pause`: Pause or resume playback.
- `show`: Display information about the currently playing track.
- `queue`: Show upcoming tracks in the queue.
- `add`: Search and add a track to the queue.
- `volume`: Prompts user for a volume value (0-100).
- `shuffle`: Toggle shuffle on/off.
- `repeat`: Cycle repeat modes (off, context, track).
- `showlists`: List your playlists.
- `showlist`: List tracks in playlist.
- `playlist `: Play a selected playlist.
- `createlist`: Create a new playlist.
- `addtolist`: Add a song to a playlist.
- `removefromlist`: Remove a song from a list.
- `track`: Search and play a specific track.
- `help`: Prints out all commands for user to see.
- `quit`: Exit the control panel.
