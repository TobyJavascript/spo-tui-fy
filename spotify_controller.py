#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import os

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

def safe_call(func, success_msg=None):
    try:
        func()
        if success_msg:
            print(success_msg)
    except SpotifyException as e:
        reason = e.msg or str(e)
        print(f"[!] Spotify command failed: {reason}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

def next_track():
    safe_call(lambda: sp.next_track(), "\n[->] Skipped to next track.")

def previous_track():
    safe_call(lambda: sp.previous_track(), "\n[<-]  Went back to previous track.")

def pause_resume():
    try:
        print("")
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            safe_call(lambda: sp.pause_playback(), "[||] Paused playback.")
        else:
            safe_call(lambda: sp.start_playback(), "[>] Resumed playback.")
    except SpotifyException as e:
        print(f"[!] Could not pause/resume: {e.msg or str(e)}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

def show_current():
    try:
        print("")
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            item = playback["item"]
            name = item["name"]
            artist = item["artists"][0]["name"]
            print(f"Now playing: {name} — {artist}")
            show_progress()
        else:
            print("[||] No music playing.")
    except SpotifyException as e:
        print(f"[!] Could not fetch current track: {e.msg or str(e)}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        
def set_volume():
    try:
        print("")
        vol_input = input("Set volume (0-100): ").strip()
        vol = int(vol_input)
        if vol < 0:
            vol = 0
        elif vol > 100:
            vol = 100
        safe_call(lambda: sp.volume(vol), f"Volume set to {vol}%")
    except ValueError:
        print("[!] Invalid input. Please enter a number between 0 and 100.")
    except SpotifyException as e:
        print(f"[!] Could not set volume: {e.msg or str(e)}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        
def toggle_shuffle():
    try:
        print("")
        playback = sp.current_playback()
        if playback:
            current = playback['shuffle_state']
            safe_call(lambda: sp.shuffle(not current), f"Shuffle set to {not current}")
        else:
            print("[!] No active playback found.")
    except Exception as e:
        print(f"[!] Error toggling shuffle: {e}")

def cycle_repeat():
    try:
        print("")
        playback = sp.current_playback()
        if playback:
            current = playback['repeat_state']
            states = ['off', 'context', 'track']
            next_state = states[(states.index(current) + 1) % 3]
            safe_call(lambda: sp.repeat(next_state), f"Repeat set to {next_state}")
        else:
            print("[!] No active playback found.")
    except Exception as e:
        print(f"[!] Error changing repeat mode: {e}")

def show_progress():
    try:
        print("")
        playback = sp.current_playback()
        if playback and playback.get("item"):
            progress = playback["progress_ms"] // 1000
            duration = playback["item"]["duration_ms"] // 1000
            print(f"Progress: {progress//60}:{progress%60:02d} / {duration//60}:{duration%60:02d}")
        else:
            print("[!] No active track playing.")
    except Exception as e:
        print(f"[!] Could not fetch progress: {e}")

def list_playlists():
    try:
        print("")
        playlists = sp.current_user_playlists()
        for i, playlist in enumerate(playlists['items']):
            print(f"{i+1}: {playlist['name']} (Tracks: {playlist['tracks']['total']})")
    except Exception as e:
        print(f"[!] Could not fetch playlists: {e}")

def play_playlist():
    try:
        print("")
        playlists = sp.current_user_playlists()
        for i, playlist in enumerate(playlists['items']):
            print(f"{i+1}: {playlist['name']}")
        choice = int(input("Select playlist number to play: ").strip()) - 1
        if 0 <= choice < len(playlists['items']):
            uri = playlists['items'][choice]['uri']
            safe_call(lambda: sp.start_playback(context_uri=uri), f"Playing playlist: {playlists['items'][choice]['name']}")
        else:
            print("[!] Invalid playlist number.")
    except Exception as e:
        print(f"[!] Could not play playlist: {e}")

def play_track():
    try:
        print("")
        query = input("Enter track name to search: ").strip()
        results = sp.search(q=query, type='track', limit=5)
        tracks = results['tracks']['items']
        if not tracks:
            print("[!] No tracks found.")
            return
        for i, track in enumerate(tracks):
            print(f"{i+1}: {track['name']} — {track['artists'][0]['name']}")
        choice = int(input("Select track number to play: ").strip()) - 1
        if 0 <= choice < len(tracks):
            uri = tracks[choice]['uri']
            safe_call(lambda: sp.start_playback(uris=[uri]), f"Playing track: {tracks[choice]['name']}")
        else:
            print("[!] Invalid track number.")
    except Exception as e:
        print(f"[!] Could not play track: {e}")

def show_help():
    print("\nAvailable commands:")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd:<10} → {desc}")

COMMANDS = {
    "next": "Skip to next track",
    "prev": "Go back to previous track",
    "pause": "Pause or resume playback",
    "show": "Show currently playing track",
    "volume": "Set volume (0-100)",
    "shuffle": "Toggle shuffle on/off",
    "repeat": "Cycle repeat mode (off/context/track)",
    "progress": "Show playback progress of current track",
    "playlists": "List your playlists",
    "playlist": "Play a selected playlist",
    "track": "Search and play a specific track",
    "help": "Show this help message",
    "quit": "Exit the controller"
}

def main():
    print("Spotify Controller ready. Type a command:")
    while True:
        cmd = input("\nCommand (type 'help' to list all commands): ").strip().lower()
        
        if cmd == "next": next_track()
        elif cmd == "prev": previous_track()
        elif cmd == "pause": pause_resume()
        elif cmd == "show": show_current()
        elif cmd == "volume": set_volume()
        elif cmd == "shuffle": toggle_shuffle()
        elif cmd == "repeat": cycle_repeat()
        elif cmd == "progress": show_progress()
        elif cmd == "playlists": list_playlists()
        elif cmd == "playlist": play_playlist()
        elif cmd == "track": play_track()
        elif cmd == "help": show_help()
        elif cmd == "quit":
            print("Exiting Spotify Controller.")
            break
        else:
            print("Unknown command. Type 'help' to see all commands.")

if __name__ == "__main__":
    main()
