from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

GITHUB_STATE_FILE = DATA_DIR / "github.json"
STEAM_STATE_FILE = DATA_DIR / "steam.json"
MC_STATE_FILE = DATA_DIR / "minecraft.json"