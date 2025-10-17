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

# Default values
DEFAULT_PORT: Final = 8002
DEFAULT_TIMEOUT: Final = 2.0
DEFAULT_SCAN_INTERVAL: Final = 5  # seconds
DEFAULT_NAME: Final = "Mezzo Amplifier"

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
UID_PRESET: Final = "preset"
UID_TEMP_TRANSFORMER: Final = "temp_transformer"
UID_TEMP_HEATSINK: Final = "temp_heatsink"
UID_TEMP_CHANNEL: Final = "temp_ch"
UID_FAULT_CODE: Final = "fault_code"
UID_MUTE_CODES: Final = "mute_codes_ch"
UID_STANDBY_STATE: Final = "standby_state"

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
