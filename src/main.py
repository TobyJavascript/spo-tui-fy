from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Footer, Header, Input
from spotify_controller import SpotifyController

from PIL import Image
import requests
from io import BytesIO

def image_to_ascii_textual(url, width, height):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    char_aspect = 0.5
    target_height = max(1, int(height / char_aspect))
    img = img.resize((width, target_height))

    pixels = list(img.getdata())
    chars = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]

    ascii_str = ""
    for y in range(img.height):
        for x in range(width):
            r, g, b = pixels[y * width + x][:3]
            brightness = sum((r, g, b)) // 3
            char = chars[brightness * (len(chars)-1) // 255]
            ascii_str += f"[rgb({r},{g},{b})]{char}[/rgb({r},{g},{b})]"
        ascii_str += "\n"
    return ascii_str

TITLE = r"""
   _____                 ________  ______     ____     
  / ___/____  ____      /_  __/ / / /  _/    / __/_  __
  \__ \/ __ \/ __ \______/ / / / / // /_____/ /_/ / / /
 ___/ / /_/ / /_/ /_____/ / / /_/ // /_____/ __/ /_/ / 
/____/ .___/\____/     /_/  \____/___/    /_/  \__, /  
    /_/                                       /____/    
"""

class FourBoxesApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.spotifyController = SpotifyController()

    # --- Layout setup ---
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with Grid():
            yield Static(TITLE, classes="box", id="title-box")
            yield Static("Box 3", classes="box", id="image-box")
            yield Static("Box 2", classes="box", id="list-box")
            yield Static("Box 4", classes="box", id="song-box")
            yield Input(placeholder="Box 5", classes="box", id="command-box")

        yield Footer()

    def on_mount(self) -> None:
        """Runs once when the app starts."""
        self._adjust_layout(self.size.width)
        self.set_interval(1.0, self.refresh_boxes)

    def refresh_boxes(self) -> None:
        """Update boxes every second with live info."""
        track_info = self.spotifyController.get_current_track()
        song_box = self.query_one("#song-box", Static)
        image_box = self.query_one("#image-box", Static)

        if track_info:
            title = track_info["title"]
            artists = ", ".join(track_info["artists"])
            progress_ms = track_info["progress_ms"] or 0
            duration_ms = track_info["duration_ms"] or 1

            def ms_to_min_sec(ms):
                minutes = ms // 60000
                seconds = (ms % 60000) // 1000
                return f"{minutes}:{seconds:02}"

            elapsed = ms_to_min_sec(progress_ms)
            remaining = ms_to_min_sec(duration_ms - progress_ms)

            song_box.update(f"{title}\n{artists}\nElapsed: {elapsed} / Remaining: {remaining}")
        else:
            song_box.update("No song currently playing")

        if track_info and track_info.get("album_image_url"):
            terminal_width = self.size.width
            terminal_height = self.size.height

            width = max(10, int(terminal_width * 6 / 9)) // 2
            height = max(5, int(terminal_height * 6 / 10)) // 2

            ascii_art = image_to_ascii_textual(track_info["album_image_url"], width=width, height=height)
            image_box.update(ascii_art)
        else:
            image_box.update("No image available")

    def on_resize(self, event) -> None:
        """Called automatically when terminal is resized."""
        self._adjust_layout(event.size.width)

    def _adjust_layout(self, width: int) -> None:
        """
        Adjust column/row spans based on current terminal width.
        Tweak spans to fit your preferred arrangements.
        """

        if width < 100:
            title_box = self.query_one("#title-box")
            title_box.styles.display = "none"

            self.query_one("#image-box").styles.column_span = 5
            self.query_one("#image-box").styles.row_span = 6

            self.query_one("#list-box").styles.column_span = 4
            self.query_one("#list-box").styles.row_span = 6

            self.query_one("#song-box").styles.column_span = 9
            self.query_one("#song-box").styles.row_span = 2

            self.query_one("#command-box").styles.column_span = 9
            self.query_one("#command-box").styles.row_span = 1

        elif width > 150:
            title_box = self.query_one("#title-box")
            title_box.styles.display = "block"

            self.query_one("#title-box").styles.column_span = 3
            self.query_one("#title-box").styles.row_span = 2

            self.query_one("#image-box").styles.column_span = 6
            self.query_one("#image-box").styles.row_span = 6

            self.query_one("#list-box").styles.column_span = 3
            self.query_one("#list-box").styles.row_span = 6

            self.query_one("#song-box").styles.column_span = 6
            self.query_one("#song-box").styles.row_span = 2

            self.query_one("#command-box").styles.column_span = 9
            self.query_one("#command-box").styles.row_span = 1

        else:
            self.query_one("#title-box").styles.column_span = 3
            self.query_one("#title-box").styles.row_span = 2

            self.query_one("#image-box").styles.column_span = 6
            self.query_one("#image-box").styles.row_span = 6

            self.query_one("#list-box").styles.column_span = 3
            self.query_one("#list-box").styles.row_span = 6

            self.query_one("#song-box").styles.column_span = 6
            self.query_one("#song-box").styles.row_span = 2

            self.query_one("#command-box").styles.column_span = 9
            self.query_one("#command-box").styles.row_span = 1

    def on_input_submitted(self, event: Input.Submitted) -> None:
        input_widget = self.query_one("#command-box", Input)
        output_widget = self.query_one("#song-box", Static)

        command = input_widget.value.strip().lower()
        input_widget.value = ""

if __name__ == "__main__":
    FourBoxesApp().run()
