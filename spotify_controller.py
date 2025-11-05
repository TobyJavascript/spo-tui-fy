#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

def safe_call(func, success_msg=None):
    """Safely execute a Spotify API call with friendly error handling."""
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
    safe_call(lambda: sp.next_track(), "[->] Skipped to next track.")

def previous_track():
    safe_call(lambda: sp.previous_track(), "[<-]  Went back to previous track.")

def pause_resume():
    try:
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
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            item = playback["item"]
            name = item["name"]
            artist = item["artists"][0]["name"]
            print(f"Now playing: {name} — {artist}")
        else:
            print("[||] No music playing.")
    except SpotifyException as e:
        print(f"[!] Could not fetch current track: {e.msg or str(e)}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

def main():
    print("Spotify Controller ready. Type a command:")
    while True:
        cmd = input("Command (next, prev, pause, show, quit): ").strip().lower()
        if cmd == "next":
            next_track()
        elif cmd == "prev":
            previous_track()
        elif cmd == "pause":
            pause_resume()
        elif cmd == "show":
            show_current()
        elif cmd == "quit":
            print("Exiting Spotify Controller.")
            break
        else:
            print("Unknown command. Try: next, prev, pause, show, quit")

if __name__ == "__main__":
    main()
