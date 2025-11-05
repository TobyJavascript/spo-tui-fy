# Spotify TUI Control Panel

**Spotify TUI Control Panel** is a terminal-based interface that allows you to control Spotify playback directly from your terminal. With simple commands like **skip tracks**, **go back to previous tracks**, **pause/resume** playback, **view the currently playing track** etc. It provides a lightweight and intuitive way to interact with Spotify without leaving the command line.

---

## Features

- **Control playback**: Skip to the next/previous track, pause or resume playback.
- **Show current track**: Display information about the currently playing track (song name and artist).

---

## Requirements

- **Debian 13** (or compatible Linux distros).
- **Python 3.7+** and **virtual environment**.
- **Spotify Developer account** (for API access).

---

## Supported Shells
- bash

---

## Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/spotify-tui-control-panel.git
cd spotify-tui-control-panel
```

### Step 2: Run the Setup Script
Run the setup.sh script to automatically install the dependencies, set up a virtual environment, and configure everything:
```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Install required packages and dependencies.
- Set up a Python virtual environment.
- Install Python libraries listed in requirements.txt.
- Set up your Spotify API credentials (you need to fill in your Client ID, Client Secret, and Redirect URI in the script).
- Optionally create a shortcut command (spotuify) for easy access.

### Step 3: Configure Spotify API Credentials
1. Visit Spotify Developer Dashboard: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create app (Make up your own app name, but use http://127.0.0.1:8888/callback for redirect URI).
2. Note down your **Client ID** and **Client Secret**.
4. Update the `setup.sh` script with your **Client ID** and **Client Secret** under the `CLIENT_ID` and`CLIENT_SECRET` variables.

### Step 4: Run the Application
Once the setup is complete, you can start the Spotify TUI Control Panel by running:
```bash
spotuify
```

```bash
python spotify_controller.py
```
---

## Usage
Once running, you can use the following commands to control playback:
- next: Skip to the next track.
- prev: Go back to the previous track.
- pause: Pause or resume playback.
- show: Display information about the currently playing track.
- volume: Prompts user for a volume value (0-100).
- shuffle: Toggle shuffle on/off.
- repeat: Cycle repeat modes (off, context, track).
- progress: Show current track playback progress (minutes:seconds).
- quit: Exit the control panel.
