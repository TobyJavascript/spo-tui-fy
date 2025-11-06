#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ------------------ Spotify setup ------------------ #
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state"
CACHE_PATH = os.path.join(os.path.expanduser("~/spotify_controller"), ".cache")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=CACHE_PATH
))

local_queue = []
console = Console()

# ------------------ Help text ------------------ #
HELP_TEXT = {
    "next": "Skip to next track",
    "prev": "Go to previous track",
    "pause": "Pause or resume playback",
    "volume": "Set playback volume (0-100)",
    "shuffle": "Toggle shuffle on/off",
    "repeat": "Cycle repeat mode (off/context/track)",
    "queue": "Show local queue",
    "add": "Search and add a track to queue",
    "track": "Search and play a track",
    "show": "Show currently playing track",
    "playlists": "List user playlists",
    "playlist": "Play a selected playlist",
    "help": "Show this help message",
    "quit": "Exit the controller"
}

# ------------------ Utility ------------------ #
def safe_call(func, success_msg=None):
    try:
        func()
        if success_msg:
            console.print(f"[green]{success_msg}[/green]")
    except SpotifyException as e:
        reason = e.msg or str(e)
        console.print(f"[red][!] Spotify command failed: {reason}[/red]")
    except Exception as e:
        console.print(f"[red][!] Unexpected error: {e}[/red]")

def get_current_track():
    """Return current playing track info or None"""
    try:
        playback = sp.current_playback()
        if not playback or not playback.get("item"):
            return None
        item = playback["item"]
        return {
            "title": item.get("name"),
            "artists": ", ".join(a["name"] for a in item.get("artists", [])),
            "album": item.get("album", {}).get("name"),
            "progress": f"{playback.get('progress_ms',0)//60000}:{(playback.get('progress_ms',0)//1000)%60:02d} / {item.get('duration_ms',0)//60000}:{(item.get('duration_ms',0)//1000)%60:02d}",
            "is_playing": playback.get("is_playing", False)
        }
    except Exception:
        return None

def current_track_alone():
    current_track()
    console.input("\nPress Enter to continue...")

def current_track():
    track = get_current_track()
    if track:
        status = "▶ Playing" if track["is_playing"] else "⏸ Paused"
        console.print(Panel(f"[bold]{track['title']}[/bold] — {track['artists']}\nAlbum: {track['album']}\nProgress: {track['progress']}\nStatus: {status}", title="Now Playing"))
    else:
        console.print(Panel("[yellow]No track currently playing[/yellow]", title="Now Playing"))

# ------------------ Command wrappers ------------------ #
def cmd_next():
    safe_call(lambda: sp.next_track(), "Skipped to next track.")
    current_track()
    console.input("\nPress Enter to continue...")

def cmd_prev():
    safe_call(lambda: sp.previous_track(), "Went back to previous track.")
    current_track()
    console.input("\nPress Enter to continue...")

def cmd_pause_resume():
    playback = sp.current_playback()
    if playback and playback.get("is_playing"):
        safe_call(lambda: sp.pause_playback(), "Playback paused")
        current_track()
        console.input("\nPress Enter to unpause...")
        safe_call(lambda: sp.start_playback(), "Playback resumed")
    else:
        safe_call(lambda: sp.start_playback(), "Playback resumed")

def cmd_volume():
    vol = console.input("Set volume (0-100): ")
    try:
        vol = max(0, min(100, int(vol)))
        safe_call(lambda: sp.volume(vol), f"Volume set to {vol}%")
        console.print(f"\nVolume is now: [cyan]{vol}%[/cyan]")
    except ValueError:
        console.print("[red]Invalid input. Must be 0-100[/red]")
    finally:
        console.input("Press Enter to continue...")

def cmd_shuffle():
    playback = sp.current_playback()
    if playback:
        current = playback["shuffle_state"]
        new_state = not current
        safe_call(lambda: sp.shuffle(new_state), f"Shuffle set to {new_state}")
        console.print(f"\nCurrent shuffle state: [cyan]{new_state}[/cyan]")
    else:
        console.print("[red]No active playback found[/red]")
    console.input("Press Enter to continue...")

def cmd_repeat():
    playback = sp.current_playback()
    if playback:
        states = ["off", "context", "track"]
        current = playback["repeat_state"]
        next_state = states[(states.index(current) + 1) % 3]
        safe_call(lambda: sp.repeat(next_state), f"Repeat set to {next_state}")
        console.print(f"\nCurrent repeat state: [cyan]{next_state}[/cyan]")
    else:
        console.print("[red]No active playback found[/red]")
    console.input("Press Enter to continue...")

def cmd_show_queue():
    if not local_queue:
        console.print("[yellow]Local queue is empty[/yellow]")
    else:
        table = Table(title="Local Queue")
        table.add_column("Index", style="bold green")
        table.add_column("Title", style="yellow")
        table.add_column("Artists", style="cyan")
        for i, t in enumerate(local_queue):
            table.add_row(str(i+1), t['name'], t['artists'][0]['name'])
        console.print(table)
    current_track()
    console.input("\nPress Enter to continue...")

def cmd_add_track():
    query = console.input("Track name to add to queue: ").strip()
    results = sp.search(q=query, type="track", limit=5)["tracks"]["items"]
    if not results:
        console.print("[yellow]No tracks found[/yellow]")
        return
    table = Table(title="Search Results")
    table.add_column("Index", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Artists", style="cyan")
    for i, t in enumerate(results):
        table.add_row(str(i), t['name'], t['artists'][0]['name'])
    console.print(table)
    idx = int(console.input("Select track index: "))
    if 0 <= idx < len(results):
        track = results[idx]
        safe_call(lambda: sp.add_to_queue(track['uri']), f"Added {track['name']} to queue")
        local_queue.append(track)
    else:
        console.print("[red]Invalid track number[/red]")
    console.input("\nPress Enter to continue...")

def cmd_play_track_and_show_current():
    cmd_play_track()
    current_track()
    console.input("\nPress Enter to continue...")

def cmd_play_track():
    query = console.input("Track name to play: ").strip()
    results = sp.search(q=query, type="track", limit=5)["tracks"]["items"]
    if not results:
        console.print("[yellow]No tracks found[/yellow]")
        return
    table = Table(title="Search Results")
    table.add_column("Index", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Artists", style="cyan")
    for i, t in enumerate(results):
        table.add_row(str(i), t['name'], t['artists'][0]['name'])
    console.print(table)
    idx = int(console.input("Select track index: "))
    if 0 <= idx < len(results):
        track = results[idx]
        safe_call(lambda: sp.start_playback(uris=[track['uri']]), f"Playing {track['name']}")
    else:
        console.print("[red]Invalid track number[/red]")

def cmd_list_playlists():
    pls = sp.current_user_playlists()["items"]
    table = Table(title="User Playlists")
    table.add_column("Index", style="green")
    table.add_column("Name", style="yellow")
    table.add_column("Tracks", style="cyan")
    for i, p in enumerate(pls):
        table.add_row(str(i), p['name'], str(p['tracks']['total']))
    console.print(table)
    console.input("\nPress Enter to continue...")

def cmd_play_playlist():
    pls = sp.current_user_playlists()["items"]
    table = Table(title="User Playlists")
    table.add_column("Index", style="green")
    table.add_column("Name", style="yellow")
    for i, p in enumerate(pls):
        table.add_row(str(i), p['name'])
    console.print(table)
    idx = int(console.input("Select playlist index: "))
    if 0 <= idx < len(pls):
        safe_call(lambda: sp.start_playback(context_uri=pls[idx]['uri']), f"Playing {pls[idx]['name']}")
    else:
        console.print("[red]Invalid playlist number[/red]")
    console.input("\nPress Enter to continue...")

def show_help():
    """Show this help message"""
    table = Table(title="Available Commands")
    table.add_column("Command", style="bold green")
    table.add_column("Description", style="yellow")
    for name, desc in HELP_TEXT.items():
        table.add_row(name, desc)
    console.print(table)
    console.input("\nPress Enter to continue...")

# ------------------ Command dictionary ------------------ #
COMMANDS = {
    "next": cmd_next,
    "prev": cmd_prev,
    "pause": cmd_pause_resume,
    "volume": cmd_volume,
    "shuffle": cmd_shuffle,
    "repeat": cmd_repeat,
    "queue": cmd_show_queue,
    "add": cmd_add_track,
    "track": cmd_play_track_and_show_current,
    "show": current_track_alone,
    "playlists": cmd_list_playlists,
    "playlist": cmd_play_playlist,
    "help": show_help,
    "quit": exit,
}

# ------------------ Main Loop ------------------ #
def main():
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Spotify Controller[/bold cyan]\nType a command (help to list)", expand=False))
        cmd = console.input("Command: ").strip().lower()
        if cmd in COMMANDS:
            COMMANDS[cmd]()
        else:
            console.print(f"[red]Unknown command:[/red] {cmd}")

if __name__ == "__main__":
    main()
