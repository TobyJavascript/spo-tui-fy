from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Static, Footer, Header, Input
from spotify_controller import SpotifyController

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

            self.query_one("#image-box").styles.column_span = 9
            self.query_one("#image-box").styles.row_span = 3

            self.query_one("#list-box").styles.column_span = 9
            self.query_one("#list-box").styles.row_span = 2

            self.query_one("#song-box").styles.column_span = 9
            self.query_one("#song-box").styles.row_span = 2

            self.query_one("#command-box").styles.column_span = 9
            self.query_one("#command-box").styles.row_span = 2

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
