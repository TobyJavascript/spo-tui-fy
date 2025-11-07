from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import os

console = Console()

def show_title(file_path: str, index: int = 0, color: str = "bold cyan", border_color: str = "green", indent: int = 0):
    """Load and display an ASCII art title from file."""
    if not os.path.exists(file_path):
        console.print(f"[red]Title file not found: {file_path}[/red]")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        titles = [(" " * indent) + block.strip("\n ") for block in f.read().split(":") if block.strip()]

    if index < 0 or index >= len(titles):
        console.print(f"[red]Invalid title index {index}[/red]")
        return

    text = Text(titles[index], style=color)
    panel = Panel(text, border_style=border_color, expand=False)
    console.print(panel)
