# ------------------ Setup Spotify Controller on Windows ------------------ #
$ErrorActionPreference = "Stop"

Write-Host "Setting up Spotify Control Panel..." -ForegroundColor Cyan

# --- Check for Python installation ---
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion"
} catch {
    Write-Warning "Python not found. Please install Python 3.10+ from https://www.python.org/downloads/ and ensure 'python' is in PATH."
    exit 1
}

# --- Prompt for Spotify credentials ---
$CLIENT_ID = Read-Host "Enter your Spotify CLIENT_ID"
$CLIENT_SECRET = Read-Host "Enter your Spotify CLIENT_SECRET"

# --- Create project directory ---
$PROJECT_DIR = "$env:USERPROFILE\spotify_controller"
if (-not (Test-Path $PROJECT_DIR)) {
    New-Item -ItemType Directory -Path $PROJECT_DIR | Out-Null
    Write-Host "Created project directory at $PROJECT_DIR"
} else {
    Write-Host "Project directory already exists at $PROJECT_DIR"
}

# --- Create Spotify credentials env file ---
$ENV_FILE = "$PROJECT_DIR\spotify_credentials.env"
@"
CLIENT_ID=$CLIENT_ID
CLIENT_SECRET=$CLIENT_SECRET
"@ | Out-File -FilePath $ENV_FILE -Encoding ASCII -Force
Write-Host "Created Spotify credentials env file at $ENV_FILE"

# --- Copy Python scripts and resources ---
Write-Host "Copying script files..."
Copy-Item -Path "spotify_controller.py", "ascii_titles.py", "logos.txt", "requirements.txt" -Destination $PROJECT_DIR -Force

# --- Create Python virtual environment ---
$VENV_DIR = "$env:USERPROFILE\spotify_env"
if (-not (Test-Path $VENV_DIR)) {
    python -m venv $VENV_DIR
    Write-Host "Created Python virtual environment at $VENV_DIR"
} else {
    Write-Host "Virtual environment already exists at $VENV_DIR"
}

# --- Paths to venv Python and activation ---
$VENV_PYTHON = "$VENV_DIR\Scripts\python.exe"
$VENV_ACTIVATE_PS = "$VENV_DIR\Scripts\Activate.ps1"

# --- Activate virtual environment ---
Write-Host "Activating virtual environment..."
if (Test-Path $VENV_ACTIVATE_PS) {
    & $VENV_ACTIVATE_PS
} else {
    Write-Warning "Activate.ps1 not found, continuing using $VENV_PYTHON directly."
}

# --- Upgrade pip and install dependencies ---
Write-Host "Installing Python dependencies..."
& $VENV_PYTHON -m pip install --upgrade pip
& $VENV_PYTHON -m pip install -r "$PROJECT_DIR\requirements.txt"

# --- Create a .bat launcher command ---
$BAT_PATH = "$env:USERPROFILE\spotuify.bat"
Write-Host "Creating launcher command 'spotuify.bat' at $BAT_PATH..."
$batContent = @"
@echo off
REM Activates virtual environment and runs Spotify Controller
CALL "$VENV_DIR\Scripts\Activate.bat"
python "$PROJECT_DIR\spotify_controller.py" %*
"@
$batContent | Out-File -FilePath $BAT_PATH -Encoding ASCII -Force

Write-Host "   _____                 ________  ______     ____     
  / ___/____  ____      /_  __/ / / /  _/    / __/_  __
  \__ \/ __ \/ __ \______/ / / / / // /_____/ /_/ / / /
 ___/ / /_/ / /_/ /_____/ / / /_/ // /_____/ __/ /_/ / 
/____/ .___/\____/     /_/  \____/___/    /_/  \__, /  
    /_/                                       /____/   "
Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "You can now control Spotify with batch script spotuify.bat"