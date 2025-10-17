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

# Default scene configurations
DEFAULT_SCENES: Final = [
    {
        "id": 0,
        "name": "Scene 1 - Flat",
        "volumes": [0.5, 0.5, 0.5, 0.5],  # 50% all channels
        "mutes": [False, False, False, False],
        "sources": [0, 0, 0, 0],
        "standby": False,
        "eq": [
            # Channel 1-4: All flat/disabled
            DEFAULT_EQ_FLAT.copy(),
            DEFAULT_EQ_FLAT.copy(),
            DEFAULT_EQ_FLAT.copy(),
            DEFAULT_EQ_FLAT.copy(),
        ],
    },
    {
        "id": 1,
        "name": "Scene 2 - Bass Boost",
        "volumes": [0.7, 0.7, 0.6, 0.6],
        "mutes": [False, False, False, False],
        "sources": [1, 1, 1, 1],
        "standby": False,
        "eq": [
            # Channel 1-4: Low-shelf boost at 80Hz
            [
                {"enabled": 1, "type": 11, "q": 0.707, "slope": 1.0, "frequency": 80, "gain": 1.4},  # +3dB low shelf
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 5000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 1, "type": 11, "q": 0.707, "slope": 1.0, "frequency": 80, "gain": 1.4},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 5000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 1, "type": 11, "q": 0.707, "slope": 1.0, "frequency": 80, "gain": 1.4},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 5000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 1, "type": 11, "q": 0.707, "slope": 1.0, "frequency": 80, "gain": 1.4},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 5000, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
        ],
    },
    {
        "id": 2,
        "name": "Scene 3 - Vocal Clarity",
        "volumes": [0.8, 0.8, 0.5, 0.5],
        "mutes": [False, False, False, False],
        "sources": [2, 2, 2, 2],
        "standby": False,
        "eq": [
            # Channel 1-4: Presence boost at 2-4kHz
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 2500, "gain": 1.3},  # +2.3dB presence
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 4000, "gain": 1.2},  # +1.6dB clarity
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 2500, "gain": 1.3},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 4000, "gain": 1.2},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 2500, "gain": 1.3},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 4000, "gain": 1.2},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 2500, "gain": 1.3},
                {"enabled": 1, "type": 0, "q": 2.0, "slope": 1.0, "frequency": 4000, "gain": 1.2},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
        ],
    },
    {
        "id": 3,
        "name": "Scene 4 - Treble Enhance",
        "volumes": [0.6, 0.6, 0.4, 0.4],
        "mutes": [False, False, False, False],
        "sources": [0, 0, 0, 0],
        "standby": False,
        "eq": [
            # Channel 1-4: High-shelf boost
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 1, "type": 12, "q": 0.707, "slope": 1.0, "frequency": 8000, "gain": 1.35},  # +2.6dB high shelf
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 1, "type": 12, "q": 0.707, "slope": 1.0, "frequency": 8000, "gain": 1.35},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 1, "type": 12, "q": 0.707, "slope": 1.0, "frequency": 8000, "gain": 1.35},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
            [
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 100, "gain": 1.0},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 1000, "gain": 1.0},
                {"enabled": 1, "type": 12, "q": 0.707, "slope": 1.0, "frequency": 8000, "gain": 1.35},
                {"enabled": 0, "type": 0, "q": 1.0, "slope": 1.0, "frequency": 10000, "gain": 1.0},
            ],
        ],
    },
]

# Platforms
PLATFORMS: Final = [
    "switch",
    "number",
    "select",
    "sensor",
    "button",
]

# Data coordinator key
COORDINATOR: Final = "coordinator"
CLIENT: Final = "client"
SCENE_MANAGER: Final = "scene_manager"
ENTRY_ID: Final = "entry_id"

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

# Source options (-1 = muted, 0-31 = sources)
SOURCE_OPTIONS: Final = {
    "-1": "Muted",
    **{str(i): f"Source {i}" for i in range(32)},
}

# Service names
SERVICE_LOAD_PRESET: Final = "load_preset"
SERVICE_SET_VOLUME_DB: Final = "set_volume_db"
