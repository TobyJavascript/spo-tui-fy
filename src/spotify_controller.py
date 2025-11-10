#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from ascii_titles import show_title
from dotenv import load_dotenv
import time

# ------------------ Load environment variables ------------------ #
dotenv_path = Path(__file__).parent / "spotify_credentials.env"
load_dotenv(dotenv_path)

# ------------------ Spotify setup ------------------ #
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "playlist-read-private "
    "playlist-modify-public "
    "playlist-modify-private"
)
CACHE_PATH = os.path.join(os.path.expanduser("~/spotify_controller"), ".cache")

local_queue = []
console = Console()

if not CLIENT_ID or not CLIENT_SECRET:
    console.print("[red]Error: CLIENT_ID or CLIENT_SECRET not found in spotify_credentials.env[/red]")
    exit(1)

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH
    ))
except SpotifyException as e:
    console.print(f"[red]Spotify authentication failed: {e}[/red]")
    exit(1)
except Exception as e:
    console.print(f"[red]Unexpected error during Spotify setup: {e}[/red]")
    exit(1)

# ------------------ Help text ------------------ #
HELP_TEXT = {
    "next, n": "Skip to next track",
    "prev, p": "Go to previous track",
    "pause": "Pause or resume playback",
    "show, s": "Show currently playing track",
    "volume, v": "Set playback volume (0-100)",
    "track, t": "Search and play a track",
    "shuffle, sh": "Toggle shuffle on/off",
    "repeat, re": "Cycle repeat mode (off/context/track)",
    "queue, qu": "Show local queue",
    "add, a": "Search and add a track to queue",
    "showlists, sls": "List user playlists",
    "showlist, sl": "List tracks from a selected playlist",
    "playlist, pl": "Play a selected playlist",
    "createlist, cl": "Create a new playlist",
    "addtolist, atl": "Add a track to a playlist",
    "removefromlist, rfl": "Remove a track from a playlist",
    "help, h": "Show this help message",
    "quit, q": "Exit the controller"
}

# ------------------ Utility ------------------ #
def safe_call(func, success_msg=None):
    """
    Execute a function safely, handling Spotify exceptions and general errors.

    Parameters:
        func (callable): Function to execute.
        success_msg (str, optional): Message to display on successful execution.

    Returns:
        None
    """
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
    """
    Retrieve the currently playing track info.

    Returns:
        dict or None: Dictionary containing:
            - 'title': Track title (str)
            - 'artists': Comma-separated list of artist names (str)
            - 'album': Album name (str)
            - 'progress': Current playback time / total duration (str)
            - 'is_playing': Boolean indicating if track is playing
        Returns None if no track is playing or on error.
    """
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

def current_track():
    """
    Display detailed information about the currently playing track in a rich Panel.

    Returns:
        None
    """
    track = get_current_track()
    if track:
        status = "▶ Playing" if track["is_playing"] else "⏸ Paused"
        console.print(Panel(f"[bold]{track['title']}[/bold] — {track['artists']}\nAlbum: {track['album']}\nProgress: {track['progress']}\nStatus: {status}", title="Now Playing"))
    else:
        console.print(Panel("[yellow]No track currently playing[/yellow]", title="Now Playing"))

def print_title(console):
    """
    Display the ASCII title/logo if console dimensions are sufficient.

    Parameters:
        console (Console): Rich Console instance for printing.

    Returns:
        None
    """
    TITLE_FILE = Path(__file__).parent / "logos.txt"
    
    width = console.size.width
    height = console.size.height

    index = 5
    indent = 2

    if width > 59 and height > 17:

        if width <= 92 or height <= 42:
            index = 2
            indent = 3

        show_title(TITLE_FILE, index=index, color="bold green", border_color="cyan", indent=indent)

# ------------------ Command wrappers ------------------ #
def cmd_next():
    """Skip to the next track and display the currently playing track."""
    safe_call(lambda: sp.next_track(), "Skipped to next track.")
    time.sleep(0.5)
    current_track()

def cmd_prev():
    """Go back to the previous track and display the currently playing track."""
    safe_call(lambda: sp.previous_track(), "Went back to previous track.")
    time.sleep(0.5)
    current_track()

def cmd_pause_resume():
    """Pause playback if playing, or resume playback if paused."""
    playback = sp.current_playback()
    if playback and playback.get("is_playing"):
        safe_call(lambda: sp.pause_playback(), "Playback paused")
    else:
        safe_call(lambda: sp.start_playback(), "Playback resumed")
    current_track()

def cmd_volume():
    """Prompt user to set volume (0-100) and apply it."""
    vol = console.input("Set volume (0-100): ")
    try:
        vol = max(0, min(100, int(vol)))
        safe_call(lambda: sp.volume(vol), f"Volume set to {vol}%")
        console.print(f"\nVolume is now: [cyan]{vol}%[/cyan]")
    except ValueError:
        console.print("[red]Invalid input. Must be 0-100[/red]")

def cmd_shuffle():
    """Toggle shuffle mode on the current playback."""
    playback = sp.current_playback()
    if playback:
        current = playback["shuffle_state"]
        new_state = not current
        safe_call(lambda: sp.shuffle(new_state), f"Shuffle set to {new_state}")
        console.print(f"\nCurrent shuffle state: [cyan]{new_state}[/cyan]")
    else:
        console.print("[red]No active playback found[/red]")

def cmd_repeat():
    """Cycle the repeat mode through 'off', 'context', and 'track'."""
    playback = sp.current_playback()
    if playback:
        states = ["off", "context", "track"]
        current = playback["repeat_state"]
        next_state = states[(states.index(current) + 1) % 3]
        safe_call(lambda: sp.repeat(next_state), f"Repeat set to {next_state}")
        console.print(f"\nCurrent repeat state: [cyan]{next_state}[/cyan]")
    else:
        console.print("[red]No active playback found[/red]")

def cmd_show_queue():
    """Display the local queue of tracks added by the user."""
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

def cmd_add_track():
    """
    Search for a track by name, add it to Spotify queue, and append it to local_queue.
    
    Prompts the user to select a track from search results.
    """
    try:
        query = console.input("Track name to add to queue: ").strip()
        if not query:
            console.print("[red]Track name cannot be empty[/red]")
            return

        results = sp.search(q=query, type="track", limit=5)["tracks"]["items"]
        if not results:
            console.print("[yellow]No tracks found[/yellow]")
            return

        table = Table(title="Search Results")
        table.add_column("Index", style="green")
        table.add_column("Title", style="yellow")
        table.add_column("Artists", style="cyan")
        for i, t in enumerate(results):
            artists = ", ".join(a.get("name", "Unknown") for a in t.get("artists", []))
            table.add_row(str(i), t.get("name", "Unknown"), artists)
        console.print(table)

        idx = int(console.input("Select track index: "))
        if not (0 <= idx < len(results)):
            raise ValueError("Track index out of range")
        track = results[idx]
        safe_call(lambda: sp.add_to_queue(track["uri"]), f"Added {track.get('name', 'Unknown')} to queue")
        local_queue.append(track)

    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_play_track_and_show_current():
    """
    Prompt user to play a track by name and then display the currently playing track.
    """
    cmd_play_track()
    time.sleep(0.5)
    current_track()

def cmd_play_track():
    """
    Search for a track by user input and play the selected track.

    Prompts the user to enter a track name, displays search results,
    and allows the user to select which track to play.
    """
    try:
        query = console.input("Track name to play: ").strip()
        if not query:
            console.print("[red]Track name cannot be empty[/red]")
            return

        results = sp.search(q=query, type="track", limit=5)["tracks"]["items"]
        if not results:
            console.print("[yellow]No tracks found[/yellow]")
            return

        table = Table(title="Search Results")
        table.add_column("Index", style="green")
        table.add_column("Title", style="yellow")
        table.add_column("Artists", style="cyan")
        for i, t in enumerate(results):
            artists = ", ".join(a.get("name", "Unknown") for a in t.get("artists", []))
            table.add_row(str(i), t.get("name", "Unknown"), artists)
        console.print(table)

        idx_input = console.input("Select track index: ").strip()
        idx = int(idx_input)
        if not (0 <= idx < len(results)):
            raise ValueError("Track index out of range")

        track = results[idx]
        safe_call(lambda: sp.start_playback(uris=[track["uri"]]), f"Playing {track.get('name', 'Unknown')}")

    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def show_playlist_tracks(playlist_id: str):
    """
    Display all tracks in a given playlist.

    Args:
        playlist_id (str): The Spotify playlist ID to retrieve tracks from.
    """
    tracks = []
    offset = 0
    limit = 100

    while True:
        response = sp.playlist_items(playlist_id, offset=offset, limit=limit)
        items = response['items']
        if not items:
            break
        tracks.extend(items)
        offset += len(items)
        if len(items) < limit:
            break

    if not tracks:
        console.print("[yellow]Playlist is empty[/yellow]")
        return

    table = Table(title="Playlist Tracks")
    table.add_column("Index", style="green")
    table.add_column("Title", style="yellow")
    table.add_column("Artists", style="cyan")

    for i, item in enumerate(tracks, 1):
        track = item["track"]
        title = track["name"]
        artists = ", ".join(a["name"] for a in track["artists"])
        table.add_row(str(i), title, artists)

    console.print(table)

def cmd_show_playlist_tracks():
    """
    List user playlists, prompt to select one, and display its tracks.
    """
    try:
        pls = sp.current_user_playlists()["items"]
        if not pls:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(title="User Playlists")
        table.add_column("Index", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Tracks", style="cyan")
        for i, p in enumerate(pls):
            table.add_row(str(i), p.get('name', 'Unknown'), str(p.get('tracks', {}).get('total', 0)))
        console.print(table)

        idx_input = console.input("Select playlist index: ").strip()
        idx = int(idx_input)
        if not (0 <= idx < len(pls)):
            raise ValueError("Playlist index out of range")

        playlist_id = pls[idx].get('id')
        if not playlist_id:
            console.print("[red]Selected playlist has no ID[/red]")
            return

        show_playlist_tracks(playlist_id)

    except ValueError as ve:
        console.print(f"[red]Invalid input: {ve}[/red]")
    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_list_playlists():
    """
    Display all user playlists in a table with their total track count.
    """
    try:
        pls = sp.current_user_playlists()["items"]
        if not pls:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(title="User Playlists")
        table.add_column("Index", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Tracks", style="cyan")
        for i, p in enumerate(pls):
            name = p.get('name', 'Unknown')
            total_tracks = str(p.get('tracks', {}).get('total', 0))
            table.add_row(str(i), name, total_tracks)
        console.print(table)

    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_play_playlist():
    """
    Prompt user to select a playlist to play and display its tracks.
    """
    try:
        pls = sp.current_user_playlists()["items"]
        if not pls:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(title="User Playlists")
        table.add_column("Index", style="green")
        table.add_column("Name", style="yellow")
        for i, p in enumerate(pls):
            table.add_row(str(i), p.get('name', 'Unknown'))
        console.print(table)

        idx_input = console.input("Select playlist index: ").strip()
        idx = int(idx_input)
        if not (0 <= idx < len(pls)):
            raise ValueError("Playlist index out of range")

        playlist = pls[idx]
        playlist_uri = playlist.get('uri')
        playlist_id = playlist.get('id')
        playlist_name = playlist.get('name', 'Unknown')

        if not playlist_uri or not playlist_id:
            console.print("[red]Selected playlist is invalid[/red]")
            return

        safe_call(lambda: sp.start_playback(context_uri=playlist_uri), f"Playing {playlist_name}")
        show_playlist_tracks(playlist_id)
        time.sleep(0.5)
        current_track()

    except ValueError as ve:
        console.print(f"[red]Invalid input: {ve}[/red]")
    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_add_to_playlist():
    """
    Add a track to a selected playlist.

    Prompts the user to select a playlist, search for a track,
    and add the selected track to the chosen playlist.
    """
    try:
        pls = sp.current_user_playlists()["items"]
        if not pls:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(title="Your Playlists")
        table.add_column("Index", style="green")
        table.add_column("Name", style="yellow")
        for i, p in enumerate(pls):
            table.add_row(str(i), p.get("name", "Unknown"))
        console.print(table)

        idx_input = console.input("Select playlist index: ").strip()
        idx = int(idx_input)
        if not (0 <= idx < len(pls)):
            raise ValueError("Playlist index out of range")

        playlist = pls[idx]
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name", "Unknown")
        if not playlist_id:
            console.print("[red]Selected playlist is invalid[/red]")
            return

        query = console.input("Track name to add: ").strip()
        if not query:
            console.print("[red]Track name cannot be empty[/red]")
            return

        results = sp.search(q=query, type="track", limit=5)["tracks"]["items"]
        if not results:
            console.print("[yellow]No tracks found[/yellow]")
            return

        table = Table(title="Search Results")
        table.add_column("Index", style="green")
        table.add_column("Title", style="yellow")
        table.add_column("Artists", style="cyan")
        for i, t in enumerate(results):
            artists = ", ".join(a.get("name", "Unknown") for a in t.get("artists", []))
            table.add_row(str(i), t.get("name", "Unknown"), artists)
        console.print(table)

        t_idx_input = console.input("Select track index to add: ").strip()
        t_idx = int(t_idx_input)
        if not (0 <= t_idx < len(results)):
            raise ValueError("Track index out of range")

        track = results[t_idx]
        track_uri = track.get("uri")
        track_name = track.get("name", "Unknown")

        if not track_uri:
            console.print("[red]Selected track is invalid[/red]")
            return

        safe_call(
            lambda: sp.playlist_add_items(playlist_id, [track_uri]),
            f"Added [bold]{track_name}[/bold] to playlist [cyan]{playlist_name}[/cyan]"
        )

    except ValueError as ve:
        console.print(f"[red]Invalid input: {ve}[/red]")
    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_remove_from_playlist():
    """
    Remove a track from a selected playlist.

    Prompts the user to select a playlist, lists its tracks,
    and removes the selected track from the playlist.
    """
    try:
        pls = sp.current_user_playlists()["items"]
        if not pls:
            console.print("[yellow]No playlists found[/yellow]")
            return

        table = Table(title="Your Playlists")
        table.add_column("Index", style="green")
        table.add_column("Name", style="yellow")
        table.add_column("Tracks", style="cyan")
        for i, p in enumerate(pls):
            name = p.get("name", "Unknown")
            total_tracks = str(p.get("tracks", {}).get("total", 0))
            table.add_row(str(i), name, total_tracks)
        console.print(table)

        idx_input = console.input("Select playlist index: ").strip()
        idx = int(idx_input)
        if not (0 <= idx < len(pls)):
            raise ValueError("Playlist index out of range")

        playlist = pls[idx]
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name", "Unknown")
        if not playlist_id:
            console.print("[red]Selected playlist is invalid[/red]")
            return

        tracks = []
        offset = 0
        limit = 100
        while True:
            response = sp.playlist_items(playlist_id, offset=offset, limit=limit)
            items = response.get("items", [])
            if not items:
                break
            tracks.extend(items)
            offset += len(items)
            if len(items) < limit:
                break

        if not tracks:
            console.print("[yellow]Playlist is empty[/yellow]")
            return

        table = Table(title=f"Tracks in {playlist_name}")
        table.add_column("Index", style="green")
        table.add_column("Title", style="yellow")
        table.add_column("Artists", style="cyan")
        for i, item in enumerate(tracks):
            track = item.get("track", {})
            title = track.get("name", "Unknown")
            artists = ", ".join(a.get("name", "Unknown") for a in track.get("artists", []))
            table.add_row(str(i), title, artists)
        console.print(table)

        t_idx_input = console.input("Select track index to remove: ").strip()
        t_idx = int(t_idx_input)
        if not (0 <= t_idx < len(tracks)):
            raise ValueError("Track index out of range")

        track = tracks[t_idx].get("track", {})
        track_uri = track.get("uri")
        track_name = track.get("name", "Unknown")
        if not track_uri:
            console.print("[red]Selected track is invalid[/red]")
            return

        safe_call(
            lambda: sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri]),
            f"Removed [bold]{track_name}[/bold] from playlist [cyan]{playlist_name}[/cyan]"
        )

    except ValueError as ve:
        console.print(f"[red]Invalid input: {ve}[/red]")
    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def cmd_create_playlist():
    """
    Prompt user for playlist details and create a new Spotify playlist.
    """
    try:
        user_info = sp.me()
        user_id = user_info.get("id")
        if not user_id:
            console.print("[red]Could not retrieve user ID[/red]")
            return

        console.print("[bold cyan]--- Create a New Playlist ---[/bold cyan]")

        name = console.input("Enter playlist name: ").strip()
        if not name:
            console.print("[red]Playlist name cannot be empty[/red]")
            return

        desc = console.input("Enter playlist description (optional): ").strip()

        public_input = console.input("Make playlist public? (y/n): ").strip().lower()
        public = public_input == "y"

        safe_call(
            lambda: sp.user_playlist_create(user_id, name, public=public, description=desc),
            f"Playlist [bold green]{name}[/bold green] created successfully!"
        )

    except Exception as e:
        console.print(f"[red]Something went wrong: {e}[/red]")

def show_help():
    """
    Display all available commands with descriptions in a table.
    """
    try:
        table = Table(title="Available Commands")
        table.add_column("Command", style="bold green")
        table.add_column("Description", style="yellow")
        for name, desc in HELP_TEXT.items():
            table.add_row(name, desc)
        console.print(table)

    except Exception as e:
        console.print(f"[red]Something went wrong while displaying help: {e}[/red]")



# ------------------ Command dictionary ------------------ #
COMMANDS = {
    "next": cmd_next,
    "n": cmd_next,
    "prev": cmd_prev,
    "p": cmd_prev,
    "pause": cmd_pause_resume,
    "volume": cmd_volume,
    "v": cmd_volume,
    "shuffle": cmd_shuffle,
    "sh": cmd_shuffle,
    "repeat": cmd_repeat,
    "re": cmd_repeat,
    "queue": cmd_show_queue,
    "qu": cmd_show_queue,
    "add": cmd_add_track,
    "a": cmd_add_track,
    "track": cmd_play_track_and_show_current,
    "t": cmd_play_track_and_show_current,
    "show": current_track,
    "s": current_track,
    "showlists": cmd_list_playlists,
    "sls": cmd_list_playlists,
    "showlist": cmd_show_playlist_tracks,
    "sl": cmd_show_playlist_tracks,
    "playlist": cmd_play_playlist,
    "pl": cmd_play_playlist,
    "createlist": cmd_create_playlist,
    "cl": cmd_create_playlist,
    "addtolist": cmd_add_to_playlist,
    "atl": cmd_add_to_playlist,
    "removefromlist": cmd_remove_from_playlist,
    "rfl": cmd_remove_from_playlist,
    "help": show_help,
    "h": show_help,
    "quit": exit,
    "q": exit
}

# ------------------ Main Loop ------------------ #
def main():
    console.clear()
    print_title(console)
    console.print(Panel("[bold cyan]Spotify Controller[/bold cyan]\nType a command (help to list)", expand=False))
    
    while True:
        cmd = console.input("Command: ").strip().lower()
        console.clear()
        
        print_title(console)
        console.print(Panel("[bold cyan]Spotify Controller[/bold cyan]\nType a command (help to list)", expand=False))
        console.print("Command: " + cmd)
        if cmd in COMMANDS:
            COMMANDS[cmd]()
        else:
            console.print(f"[red]Unknown command:[/red] {cmd}")

if __name__ == "__main__":
    main()
