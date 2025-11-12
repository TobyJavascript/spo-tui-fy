#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# ------------------ Load environment variables ------------------ #
dotenv_path = Path(__file__).parent / "spotify_credentials.env"
load_dotenv(dotenv_path)

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
CACHE_PATH = Path(__file__).parent / ".cache"

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("CLIENT_ID or CLIENT_SECRET not found in spotify_credentials.env")


class SpotifyController:
    """A pure backend Spotify controller with no UI dependencies."""

    def __init__(self):
        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    redirect_uri=REDIRECT_URI,
                    scope=SCOPE,
                    cache_path=str(CACHE_PATH)
                )
            )
        except SpotifyException as e:
            raise RuntimeError(f"Spotify authentication failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during Spotify setup: {e}")

    # ------------------ Basic playback ------------------ #
    def pause(self):
        """Toggle pause/play."""
        playback = self.sp.current_playback()
        if playback and playback.get("is_playing"):
            self.sp.pause_playback()
            return {"status": "paused"}
        else:
            self.sp.start_playback()
            return {"status": "resumed"}

    def next(self):
        self.sp.next_track()
        return {"status": "next"}

    def previous(self):
        self.sp.previous_track()
        return {"status": "previous"}

    def set_volume(self, volume: int):
        """Set playback volume 0–100."""
        vol = max(0, min(100, int(volume)))
        self.sp.volume(vol)
        return {"volume": vol}

    def shuffle(self, state: bool | None = None):
        """Toggle or set shuffle."""
        playback = self.sp.current_playback()
        if not playback:
            return None
        current = playback["shuffle_state"]
        new_state = not current if state is None else bool(state)
        self.sp.shuffle(new_state)
        return {"shuffle": new_state}

    def repeat(self, mode: str | None = None):
        """Cycle or set repeat mode."""
        playback = self.sp.current_playback()
        if not playback:
            return None
        states = ["off", "context", "track"]
        current = playback["repeat_state"]
        next_state = states[(states.index(current) + 1) % 3] if not mode else mode
        self.sp.repeat(next_state)
        return {"repeat": next_state}

    # ------------------ Track info ------------------ #
    def get_current_track(self) -> dict | None:
        """Retrieve currently playing track info."""
        try:
            playback = self.sp.current_playback()
            if not playback or not playback.get("item"):
                return None
            item = playback["item"]
            album_images = item.get("album", {}).get("images", [])
            album_image_url = album_images[0]["url"] if album_images else None

            return {
                "title": item.get("name"),
                "artists": [a["name"] for a in item.get("artists", [])],
                "album": item.get("album", {}).get("name"),
                "album_image_url": album_image_url,  # <-- fixed
                "progress_ms": playback.get("progress_ms", 0),
                "duration_ms": item.get("duration_ms", 0),
                "is_playing": playback.get("is_playing", False),
                "shuffle": playback.get("shuffle_state", False),
                "repeat": playback.get("repeat_state", "off"),
            }
        except Exception:
            return None

    # ------------------ Search and playback ------------------ #
    def search_tracks(self, query: str, limit: int = 5):
        """Search for tracks."""
        results = self.sp.search(q=query, type="track", limit=limit)["tracks"]["items"]
        return [
            {
                "name": t["name"],
                "artists": [a["name"] for a in t["artists"]],
                "uri": t["uri"],
                "album": t["album"]["name"]
            }
            for t in results
        ]

    def play_track(self, track_uri: str):
        """Play a specific track by URI."""
        self.sp.start_playback(uris=[track_uri])
        return {"playing": track_uri}

    def add_to_queue(self, track_uri: str):
        """Add track to queue."""
        self.sp.add_to_queue(track_uri)
        return {"queued": track_uri}

    # ------------------ Playlist operations ------------------ #
    def list_playlists(self):
        """List user playlists."""
        pls = self.sp.current_user_playlists()["items"]
        return [
            {
                "name": p["name"],
                "id": p["id"],
                "uri": p["uri"],
                "total_tracks": p["tracks"]["total"]
            }
            for p in pls
        ]

    def show_playlist_tracks(self, playlist_id: str):
        """Get all tracks in a playlist."""
        tracks = []
        offset = 0
        limit = 100
        while True:
            response = self.sp.playlist_items(playlist_id, offset=offset, limit=limit)
            items = response["items"]
            if not items:
                break
            tracks.extend(items)
            offset += len(items)
            if len(items) < limit:
                break
        return [
            {
                "name": t["track"]["name"],
                "artists": [a["name"] for a in t["track"]["artists"]],
                "uri": t["track"]["uri"]
            }
            for t in tracks
        ]

    def play_playlist(self, playlist_uri: str):
        """Play a playlist."""
        self.sp.start_playback(context_uri=playlist_uri)
        return {"playing_playlist": playlist_uri}

    def create_playlist(self, name: str, description: str = "", public: bool = False):
        """Create a new playlist."""
        user_id = self.sp.me()["id"]
        playlist = self.sp.user_playlist_create(user_id, name, public=public, description=description)
        return {"playlist": playlist["id"]}

    def add_to_playlist(self, playlist_id: str, track_uri: str):
        """Add a track to playlist."""
        self.sp.playlist_add_items(playlist_id, [track_uri])
        return {"added": track_uri}

    def remove_from_playlist(self, playlist_id: str, track_uri: str):
        """Remove a track from playlist."""
        self.sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        return {"removed": track_uri}
