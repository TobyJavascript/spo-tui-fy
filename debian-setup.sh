#!/bin/bash
set -e

echo "Setting up Spotify Control Panel..."

# --- Ask user for Spotify credentials ---
read -p "Enter your Spotify CLIENT_ID: " CLIENT_ID
read -p "Enter your Spotify CLIENT_SECRET: " CLIENT_SECRET

# --- Create project directory in home ---
PROJECT_DIR="$HOME/spotify_controller"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    echo "Created project directory at $PROJECT_DIR"
fi

# --- Create .env file with credentials ---
ENV_FILE="$PROJECT_DIR/spotify_credentials.env"
echo "Creating environment file..."
cat << EOF > "$ENV_FILE"
CLIENT_ID=$CLIENT_ID
CLIENT_SECRET=$CLIENT_SECRET
EOF
echo "Environment file created at $ENV_FILE"

# --- Copy remaining project files to project directory ---
echo "Copying project files..."
cp -r spotify_controller.py ascii_titles.py logos.txt requirements.txt "$PROJECT_DIR"/

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

echo "   _____                 ________  ______     ____     
  / ___/____  ____      /_  __/ / / /  _/    / __/_  __
  \__ \/ __ \/ __ \______/ / / / / // /_____/ /_/ / / /
 ___/ / /_/ / /_/ /_____/ / / /_/ // /_____/ __/ /_/ / 
/____/ .___/\____/     /_/  \____/___/    /_/  \__, /  
    /_/                                       /____/   "

echo ""
echo "Setup complete!"
echo "You can now control Spotify with command 'spotuify'"
echo ""
