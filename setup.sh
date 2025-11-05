#!/bin/bash
set -e

echo "Setting up Spotify Controll Panel..."

# --- Update and install dependencies ---
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl

# --- Create project directory in home ---
PROJECT_DIR="$HOME/spotify_controller"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    echo "Created project directory at $PROJECT_DIR"
fi

# --- Copy files from current folder to project directory ---
echo "Copying files..."
cp -r spotify_controller.py requirements.txt "$PROJECT_DIR"/

# --- Set up Python virtual environment ---
VENV_DIR="$HOME/spotify_env"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Created Python virtual environment at $VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# --- Install Python dependencies ---
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

# --- Create shortcut command ---
echo "Creating shortcut command 'spotuify'..."
cat << EOF | sudo tee /usr/local/bin/spotuify > /dev/null
#!/bin/bash
source "\$HOME/spotify_env/bin/activate"
python3 "\$HOME/spotify_controller/spotify_controller.py" "\$@"
EOF
sudo chmod +x /usr/local/bin/spotuify

echo "Setup complete!"
echo "You can now control Spotify with: spotuify"
echo
echo "Example commands once running:"
echo "  next      → skip to next track"
echo "  prev      → go back"
echo "  pause     → pause or resume"
echo "  show      → display current track"
echo "  volume    → change volume"
echo "  shuffle   → toggle shuffle on/off"
echo "  repeat    → cycle repeat modes (off, context, track)"
echo "  progress  → show current track playback progress (minutes:seconds)"
echo "  playlists → list your playlists"
echo "  playlist  → play a selected playlist"
echo "  track     → search and play a specific track"
echo "  quit      → exit"