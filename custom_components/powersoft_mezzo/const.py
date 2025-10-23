"""Constants for the Powersoft Mezzo integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "powersoft_mezzo"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_TIMEOUT: Final = "timeout"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_CHANNEL_NAMES: Final = "channel_names"
CONF_SCENES: Final = "scenes"

# Default values
DEFAULT_PORT: Final = 8002
DEFAULT_TIMEOUT: Final = 2.0
DEFAULT_SCAN_INTERVAL: Final = 5  # seconds
DEFAULT_NAME: Final = "Mezzo Amplifier"

# Default EQ band (flat/bypass configuration)
DEFAULT_EQ_BAND_FLAT: Final = {
    "enabled": 0,  # Disabled
    "type": 0,  # Peaking
    "q": 1.0,
    "slope": 1.0,
    "frequency": 1000,  # 1kHz
    "gain": 1.0,  # Unity gain (linear)
}

# Default EQ configuration (4 bands, all flat)
DEFAULT_EQ_FLAT: Final = [
    DEFAULT_EQ_BAND_FLAT.copy(),
    DEFAULT_EQ_BAND_FLAT.copy(),
    DEFAULT_EQ_BAND_FLAT.copy(),
    DEFAULT_EQ_BAND_FLAT.copy(),
]

# Default scene configurations (empty - users create their own)
DEFAULT_SCENES: Final = []

# Platforms
PLATFORMS: Final = [
    "switch",
    "number",
    "select",
    "sensor",
    "button",
    "text",
]

# Data coordinator key
COORDINATOR: Final = "coordinator"
CLIENT: Final = "client"
SCENE_MANAGER: Final = "scene_manager"
ENTRY_ID: Final = "entry_id"
ACTIVE_SCENE_ID: Final = "active_scene_id"

# Attributes
ATTR_CHANNEL: Final = "channel"
ATTR_PRESET_ID: Final = "preset_id"
ATTR_SOURCE_ID: Final = "source_id"

# Entity unique ID prefixes
UID_POWER: Final = "power"
UID_VOLUME: Final = "volume_ch"
UID_MUTE: Final = "mute_ch"
UID_SOURCE: Final = "source_ch"
UID_SCENE: Final = "scene"
UID_TEMP_TRANSFORMER: Final = "temp_transformer"
UID_TEMP_HEATSINK: Final = "temp_heatsink"
UID_TEMP_CHANNEL: Final = "temp_ch"
UID_FAULT_CODE: Final = "fault_code"
UID_MUTE_CODES: Final = "mute_codes_ch"
UID_STANDBY_STATE: Final = "standby_state"
UID_EQ: Final = "eq_ch"

# Channel configuration
NUM_CHANNELS: Final = 4
CHANNEL_NUMBERS: Final = list(range(1, NUM_CHANNELS + 1))

# Source options (actual hardware source IDs → user-friendly names)
# Pattern: Analog inputs (1,5,9,13) interleaved with Dante (3,7)
SOURCE_OPTIONS: Final = {
    "1": "Input 1",
    "3": "Dante 1",
    "5": "Input 2",
    "7": "Dante 2",
    "9": "Input 3",
    "13": "Input 4",
}

# Service names
SERVICE_LOAD_PRESET: Final = "load_preset"
SERVICE_SET_VOLUME_DB: Final = "set_volume_db"
