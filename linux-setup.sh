#!/bin/bash
set -e

# --- Determine package manager based on user input ---
echo "   _____                 ________  ______     ____     
  / ___/____  ____      /_  __/ / / /  _/    / __/_  __
  \__ \/ __ \/ __ \______/ / / / / // /_____/ /_/ / / /
 ___/ / /_/ / /_/ /_____/ / / /_/ // /_____/ __/ /_/ / 
/____/ .___/\____/     /_/  \____/___/    /_/  \__, /  
    /_/                                       /____/   "
echo ""
echo "Welcome to Spo-TUI-fy setup script!"
echo ""
echo "Supported Linux distributions:"
echo "  [0] Debian-based"
echo "  [1] Arch-based"
echo "  [2] Not sure / Other"
echo ""
read -p "Enter the number for your system (0, 1, or 2): " SYSTEM_CHOICE

# --- Handle user input ---
if [ "$SYSTEM_CHOICE" == "0" ]; then
    FAMILY="debian"
elif [ "$SYSTEM_CHOICE" == "1" ]; then
    FAMILY="arch"
elif [ "$SYSTEM_CHOICE" == "2" ]; then
    echo ""
    echo "Choose your Linux distribution:"
    echo "  [0] Ubuntu"
    echo "  [1] Linux Mint"
    echo "  [2] Pop!_OS"
    echo "  [3] Debian"
    echo "  [4] MX Linux"
    echo "  [5] Kali Linux"
    echo "  [6] Arch Linux"
    echo "  [7] Manjaro"
    echo "  [8] EndeavourOS"
    echo "  [9] Garuda Linux"
    echo ""
    read -p "Enter the number for your distribution: " DISTRO_CHOICE

    case "$DISTRO_CHOICE" in
        0|1|2|3|4|5)
            FAMILY="debian"
            ;;
        6|7|8|9)
            FAMILY="arch"
            ;;
        *)
            echo "Invalid selection. Please run the script again and choose a valid number."
            exit 1
            ;;
    esac
else
    echo "Invalid selection. Please run the script again and choose 0, 1, or 2."
    exit 1
fi

# --- Determine package manager based on distro family ---
if [ "$FAMILY" == "debian" ]; then
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt update && sudo apt install -y python3 python3-pip python3-venv curl"
    echo "Detected Debian-based system. Using apt..."
elif [ "$FAMILY" == "arch" ]; then
    PKG_MANAGER="pacman"
    INSTALL_CMD="sudo pacman -Syu --noconfirm python python-pip python-virtualenv curl"
    echo "Detected Arch-based system. Using pacman..."
fi

echo ""
echo "Using package manager: $PKG_MANAGER"
echo ""

# --- Check for Python installation ---
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    eval "$INSTALL_CMD"
else
    echo "Python3 is already installed."
fi

echo ""
echo "Setting up Spotify Control Panel..."
echo ""

# --- Ask user for Spotify credentials ---
read -p "Enter your Spotify CLIENT_ID: " CLIENT_ID
read -p "Enter your Spotify CLIENT_SECRET: " CLIENT_SECRET

# --- Create project directory in home ---
PROJECT_DIR="$HOME/spotuify"
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
cp -r src/* "$PROJECT_DIR"/

# --- Set up Python virtual environment ---
VENV_DIR="$HOME/spotuify_env"
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
source "\$HOME/spotuify_env/bin/activate"
python3 "\$HOME/spotuify/rich_main.py" "\$@"
EOF
sudo chmod +x /usr/local/bin/spotuify

# --- ASCII Art and Finish Message ---
echo ""
echo "Setup complete!"
echo "You can now control Spotify with the command: spotuify"
echo ""