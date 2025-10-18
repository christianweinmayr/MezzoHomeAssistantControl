"""
Powersoft Mezzo Memory Map Constants.

This module defines all memory addresses and constants for the Powersoft Mezzo
amplifier PBus protocol based on the official protocol specification.
"""

# ============================================================================
# DEVICE INFORMATION AREA (0x00000000 - 0x00000510)
# ============================================================================

# Read-only device information
ADDR_DEVICE_INFO_START = 0x00000000
ADDR_DEVICE_INFO_END = 0x00000510

# Device identification (examples, adjust based on actual needs)
ADDR_MODEL_NAME = 0x00000000  # String identifier
ADDR_SERIAL_NUMBER = 0x00000014  # String identifier
ADDR_FIRMWARE_VERSION = 0x00000024  # Version string
ADDR_MAC_ADDRESS = 0x00000038  # MAC address


# ============================================================================
# NETWORK AREA (0x00001000 - 0x0000130c)
# ============================================================================

ADDR_NETWORK_START = 0x00001000
ADDR_NETWORK_END = 0x0000130c


# ============================================================================
# SOURCE SELECTION AREA (0x00002000 - 0x00002554)
# ============================================================================

# Amplifier input references
ADDR_ANALOG_REF = 0x00002000  # Float 4 bytes (linear)
ADDR_DIGITAL_REF = 0x00002004  # Float 4 bytes (linear)

# Source IDs for each channel (Enum representing source absolute IDs)
ADDR_SOURCE_ID_CH1 = 0x00002200  # 4 bytes
ADDR_SOURCE_ID_CH2 = 0x00002204  # 4 bytes
ADDR_SOURCE_ID_CH3 = 0x00002208  # 4 bytes
ADDR_SOURCE_ID_CH4 = 0x0000220c  # 4 bytes

# Priority Source index for each channel
ADDR_PRIORITY_SOURCE_CH1 = 0x00002210  # Enum 4 bytes
ADDR_PRIORITY_SOURCE_CH2 = 0x00002214  # Enum 4 bytes
ADDR_PRIORITY_SOURCE_CH3 = 0x00002218  # Enum 4 bytes
ADDR_PRIORITY_SOURCE_CH4 = 0x0000221c  # Enum 4 bytes

# Manual source selection (0 = disabled, -1 = muted, else source index)
ADDR_MANUAL_SOURCE_SELECTION = 0x00002224  # 4 bytes

# Source configuration
ADDR_SOURCE_CONFIG_START = 0x00002500
ADDR_SOURCE_CONFIG_END = 0x00002554


# ============================================================================
# MATRIX AREA (0x00003000 - 0x00003068)
# ============================================================================

ADDR_MATRIX_START = 0x00003000
ADDR_MATRIX_END = 0x00003068


# ============================================================================
# USER AREA (0x00004000 - 0x00004280)
# ============================================================================

# User Settings - Common
ADDR_USER_SETTINGS_START = 0x00004000
ADDR_USER_SETTINGS_END = 0x00004038

# User Gain (linear) for each channel
ADDR_USER_GAIN_CH1 = 0x00004000  # Float 4 bytes
ADDR_USER_GAIN_CH2 = 0x00004004  # Float 4 bytes
ADDR_USER_GAIN_CH3 = 0x00004008  # Float 4 bytes
ADDR_USER_GAIN_CH4 = 0x0000400c  # Float 4 bytes

# User Delay (seconds) for each channel
ADDR_USER_DELAY_CH1 = 0x00004010  # Float 4 bytes
ADDR_USER_DELAY_CH2 = 0x00004014  # Float 4 bytes
ADDR_USER_DELAY_CH3 = 0x00004018  # Float 4 bytes
ADDR_USER_DELAY_CH4 = 0x0000401c  # Float 4 bytes

# User Polarity for each channel
ADDR_USER_POLARITY_CH1 = 0x00004020  # uint8 1 byte
ADDR_USER_POLARITY_CH2 = 0x00004021  # uint8 1 byte
ADDR_USER_POLARITY_CH3 = 0x00004022  # uint8 1 byte
ADDR_USER_POLARITY_CH4 = 0x00004023  # uint8 1 byte

# User Mute for each channel
ADDR_USER_MUTE_CH1 = 0x00004024  # uint8 1 byte
ADDR_USER_MUTE_CH2 = 0x00004025  # uint8 1 byte
ADDR_USER_MUTE_CH3 = 0x00004026  # uint8 1 byte
ADDR_USER_MUTE_CH4 = 0x00004027  # uint8 1 byte

# User Shading
ADDR_USER_SHADING_CH1 = 0x00004028  # Float 4 bytes
ADDR_USER_SHADING_CH2 = 0x0000402c  # Float 4 bytes
ADDR_USER_SHADING_CH3 = 0x00004030  # Float 4 bytes
ADDR_USER_SHADING_CH4 = 0x00004034  # Float 4 bytes

# User EQ - 4-band parametric EQ per channel
ADDR_USER_EQ_START = 0x00004100
ADDR_USER_EQ_END = 0x00004280

# User EQ Channel 1 (4 BiQuad filters, 24 bytes each)
ADDR_USER_EQ_CH1_START = 0x00004100
ADDR_USER_EQ_CH1_BIQUAD1 = 0x00004100  # Band 1: 24 bytes
ADDR_USER_EQ_CH1_BIQUAD2 = 0x00004118  # Band 2: 24 bytes
ADDR_USER_EQ_CH1_BIQUAD3 = 0x00004130  # Band 3: 24 bytes
ADDR_USER_EQ_CH1_BIQUAD4 = 0x00004148  # Band 4: 24 bytes
ADDR_USER_EQ_CH1_END = 0x00004160

# User EQ Channel 2
ADDR_USER_EQ_CH2_START = 0x00004160
ADDR_USER_EQ_CH2_BIQUAD1 = 0x00004160
ADDR_USER_EQ_CH2_BIQUAD2 = 0x00004178
ADDR_USER_EQ_CH2_BIQUAD3 = 0x00004190
ADDR_USER_EQ_CH2_BIQUAD4 = 0x000041A8
ADDR_USER_EQ_CH2_END = 0x000041C0

# User EQ Channel 3
ADDR_USER_EQ_CH3_START = 0x000041C0
ADDR_USER_EQ_CH3_BIQUAD1 = 0x000041C0
ADDR_USER_EQ_CH3_BIQUAD2 = 0x000041D8
ADDR_USER_EQ_CH3_BIQUAD3 = 0x000041F0
ADDR_USER_EQ_CH3_BIQUAD4 = 0x00004208
ADDR_USER_EQ_CH3_END = 0x00004220

# User EQ Channel 4
ADDR_USER_EQ_CH4_START = 0x00004220
ADDR_USER_EQ_CH4_BIQUAD1 = 0x00004220
ADDR_USER_EQ_CH4_BIQUAD2 = 0x00004238
ADDR_USER_EQ_CH4_BIQUAD3 = 0x00004250
ADDR_USER_EQ_CH4_BIQUAD4 = 0x00004268
ADDR_USER_EQ_CH4_END = 0x00004280

# BiQuad structure (24 bytes per band):
# +0x00: Enabled (uint32, 4 bytes) - 0=disabled, 1=enabled
# +0x04: Type (uint32, 4 bytes) - Filter type enum
# +0x08: Q (Float, 4 bytes) - Quality factor
# +0x0C: Slope (Float, 4 bytes) - Filter slope
# +0x10: Frequency (uint32, 4 bytes) - Center frequency in Hz
# +0x14: Gain (Float, 4 bytes) - Gain in dB (range: -15.0 to +15.0)

# EQ Filter Types
EQ_TYPE_PEAKING = 0
EQ_TYPE_LOW_SHELVING = 11
EQ_TYPE_HIGH_SHELVING = 12
EQ_TYPE_LOW_PASS = 13
EQ_TYPE_HIGH_PASS = 14
EQ_TYPE_BAND_PASS = 15
EQ_TYPE_BAND_STOP = 16
EQ_TYPE_ALL_PASS = 17

# Number of EQ bands per channel
NUM_EQ_BANDS = 4
EQ_BIQUAD_SIZE = 24  # bytes per BiQuad


# ============================================================================
# LAYOUT AREA (0x00005000 - 0x000062f4)
# ============================================================================

ADDR_LAYOUT_START = 0x00005000
ADDR_LAYOUT_END = 0x000062f4

# Preset Type for each speaker
ADDR_PRESET_TYPE_SPK1 = 0x000062d4  # int32 4 bytes
ADDR_PRESET_TYPE_SPK2 = 0x000062d8  # int32 4 bytes
ADDR_PRESET_TYPE_SPK3 = 0x000062dc  # int32 4 bytes
ADDR_PRESET_TYPE_SPK4 = 0x000062e0  # int32 4 bytes


# ============================================================================
# WAYS AREA (0x00007000 - 0x00007950)
# ============================================================================

ADDR_WAYS_START = 0x00007000
ADDR_WAYS_END = 0x00007950

# Way State for each way (channel)
ADDR_WAY_STATE_CH1 = 0x00007090  # uint32 4 bytes
ADDR_WAY_STATE_CH2 = 0x00007094  # uint32 4 bytes
ADDR_WAY_STATE_CH3 = 0x00007098  # uint32 4 bytes
ADDR_WAY_STATE_CH4 = 0x0000709c  # uint32 4 bytes


# ============================================================================
# DANTE ROUTING AREA (0x00008500 - 0x00008518)
# ============================================================================

ADDR_DANTE_START = 0x00008500
ADDR_DANTE_END = 0x00008518

# Dante route gain for outputs
ADDR_DANTE_GAIN_OUT1 = 0x00008500  # float 4 bytes
ADDR_DANTE_GAIN_OUT2 = 0x00008504  # float 4 bytes
ADDR_DANTE_GAIN_OUT3 = 0x00008508  # float 4 bytes
ADDR_DANTE_GAIN_OUT4 = 0x0000850c  # float 4 bytes


# ============================================================================
# GPI CONFIGURATION AREA (0x00009000 - 0x00009004)
# ============================================================================

ADDR_GPI_CONFIG_START = 0x00009000
ADDR_GPI_CONFIG_END = 0x00009004

# GPI Mode configuration
ADDR_GPI_MODE_1 = 0x00009000  # uint8 1 byte (0=Gain, 1=Other)
ADDR_GPI_MODE_2 = 0x00009001  # uint8 1 byte
ADDR_GPI_MODE_3 = 0x00009002  # uint8 1 byte
ADDR_GPI_MODE_4 = 0x00009003  # uint8 1 byte


# ============================================================================
# GPO CONFIGURATION AREA (0x00009e00 - 0x00009e0c)
# ============================================================================

ADDR_GPO_CONFIG_START = 0x00009e00
ADDR_GPO_CONFIG_END = 0x00009e0c


# ============================================================================
# POWER CONFIG AREA (0x0000a000 - 0x0000a00c)
# ============================================================================

ADDR_POWER_CONFIG_START = 0x0000a000
ADDR_POWER_CONFIG_END = 0x0000a00c

# Standby trigger (Write: 1=activate standby, 0=deactivate)
ADDR_STANDBY_TRIGGER = 0x0000a000  # uint32 4 bytes (W)

# Auto turn on enable
ADDR_AUTO_TURN_ON_ENABLE = 0x0000a004  # uint32 4 bytes (R/W)

# Auto Power Down Enable (1=enable auto standby after 25 min, 0=disable)
ADDR_AUTO_POWER_DOWN_ENABLE = 0x0000a008  # uint32 4 bytes (R/W)


# ============================================================================
# READINGS AREA (0x0000b000 - 0x0000bbd0)
# ============================================================================

ADDR_READINGS_START = 0x0000b000
ADDR_READINGS_END = 0x0000bbd0

# ===== Slow Meters - Ali =====
ADDR_SLOW_METERS_ALI_START = 0x0000b000
ADDR_SLOW_METERS_ALI_END = 0x0000b020

# Temperatures and voltages
ADDR_TEMP_TRANSFORMER = 0x0000b000  # Float 4 bytes (R)
ADDR_TEMP_HEATSINK = 0x0000b004  # Float 4 bytes (R)
ADDR_V_MAINS_RMS = 0x0000b008  # Float 4 bytes (R)
ADDR_VCC_P = 0x0000b00c  # Float 4 bytes (R)
ADDR_VCC_N = 0x0000b010  # Float 4 bytes (R)
ADDR_FAN_CURRENT = 0x0000b014  # Float 4 bytes (R)
ADDR_V_AUX_P = 0x0000b018  # Float 4 bytes (R)
ADDR_V_AUX_N = 0x0000b01c  # Float 4 bytes (R)

# ===== Slow Meters - Ampli Channels =====
ADDR_TEMP_CH1 = 0x0000b0f4  # Float 4 bytes (R)
ADDR_TEMP_CH2 = 0x0000b0f8  # Float 4 bytes (R)
ADDR_TEMP_CH3 = 0x0000b0fc  # Float 4 bytes (R)
ADDR_TEMP_CH4 = 0x0000b100  # Float 4 bytes (R)

# ===== Slow Meters - Standby State =====
ADDR_STANDBY_STATE = 0x0000b638  # uint32 4 bytes (R) - 1=standby active, 0=not active

# ===== Slow Meters - Alarm Status =====
ADDR_ALARM_FAN = 0x0000b650  # uint8 1 byte (R)
ADDR_ALARM_HIGH_OVERTEMP = 0x0000b651  # uint8 1 byte (R) - 1 when temp > 95°C
ADDR_ALARM_PS_TEMP = 0x0000b653  # uint8 1 byte (R)
ADDR_ALARM_V_AUX = 0x0000b654  # uint8 1 byte (R)
ADDR_ALARM_GENERIC_FAULT = 0x0000b655  # uint8 1 byte (R)
ADDR_FAULT_CODE = 0x0000b656  # uint8 1 byte (R)
ADDR_GPO_RELAY_STATE = 0x0000b657  # uint8 1 byte (R) - 1=closed, 0=open
ADDR_FAULT_CODE_FLAGS = 0x0000b658  # uint32 4 bytes (R) - bitwise fault flags

# ===== Slow Meters - Mute Codes =====
# Bitwise description of all active mutes per channel
ADDR_MUTE_CODE_FLAGS_CH1 = 0x0000b700  # uint32 4 bytes (R)
ADDR_MUTE_CODE_FLAGS_CH2 = 0x0000b704  # uint32 4 bytes (R)
ADDR_MUTE_CODE_FLAGS_CH3 = 0x0000b708  # uint32 4 bytes (R)
ADDR_MUTE_CODE_FLAGS_CH4 = 0x0000b70c  # uint32 4 bytes (R)

# ===== Fast Meters =====
ADDR_FAST_METERS_START = 0x0000b800
ADDR_FAST_METERS_END = 0x0000bbd0


# ============================================================================
# AUTOSETUP AREA (0x0000c000 - 0x0000ef04)
# ============================================================================

ADDR_AUTOSETUP_START = 0x0000c000
ADDR_AUTOSETUP_END = 0x0000ef04


# ============================================================================
# ZONE BLOCK AREA (0x0000f000 - 0x0000f340)
# ============================================================================

ADDR_ZONE_BLOCK_START = 0x0000f000
ADDR_ZONE_BLOCK_END = 0x0000f340

# Zone Settings - Common
ADDR_ZONE_SETTINGS_START = 0x0000f000
ADDR_ZONE_SETTINGS_END = 0x0000f038

# Zone Enable for each channel
ADDR_ZONE_ENABLE_CH1 = 0x0000f000  # uint8 1 byte (R/W)
ADDR_ZONE_ENABLE_CH2 = 0x0000f001  # uint8 1 byte (R/W)
ADDR_ZONE_ENABLE_CH3 = 0x0000f002  # uint8 1 byte (R/W)
ADDR_ZONE_ENABLE_CH4 = 0x0000f003  # uint8 1 byte (R/W)

# Zone Mute for each channel
ADDR_ZONE_MUTE_CH1 = 0x0000f004  # uint8 1 byte (R/W)
ADDR_ZONE_MUTE_CH2 = 0x0000f005  # uint8 1 byte (R/W)
ADDR_ZONE_MUTE_CH3 = 0x0000f006  # uint8 1 byte (R/W)
ADDR_ZONE_MUTE_CH4 = 0x0000f007  # uint8 1 byte (R/W)

# Zone Gain (linear) for each channel
ADDR_ZONE_GAIN_CH1 = 0x0000f008  # Float 4 bytes (R/W)
ADDR_ZONE_GAIN_CH2 = 0x0000f00c  # Float 4 bytes (R/W)
ADDR_ZONE_GAIN_CH3 = 0x0000f010  # Float 4 bytes (R/W)
ADDR_ZONE_GAIN_CH4 = 0x0000f014  # Float 4 bytes (R/W)

# Zone Source GUID
ADDR_ZONE_SOURCE_GUID_CH1 = 0x0000f018  # uint32 4 bytes (R/W)
ADDR_ZONE_SOURCE_GUID_CH2 = 0x0000f01c  # uint32 4 bytes (R/W)
ADDR_ZONE_SOURCE_GUID_CH3 = 0x0000f020  # uint32 4 bytes (R/W)
ADDR_ZONE_SOURCE_GUID_CH4 = 0x0000f024  # uint32 4 bytes (R/W)

# Zone GUID
ADDR_ZONE_GUID_CH1 = 0x0000f028  # uint32 4 bytes (R/W)
ADDR_ZONE_GUID_CH2 = 0x0000f02c  # uint32 4 bytes (R/W)
ADDR_ZONE_GUID_CH3 = 0x0000f030  # uint32 4 bytes (R/W)
ADDR_ZONE_GUID_CH4 = 0x0000f034  # uint32 4 bytes (R/W)

# Zone EQ
ADDR_ZONE_EQ_START = 0x0000f100
ADDR_ZONE_EQ_END = 0x0000f340


# ============================================================================
# UXT CHIP AREA (0x00010000 - 0x000120b1)
# ============================================================================

ADDR_UXT_CHIP_START = 0x00010000
ADDR_UXT_CHIP_END = 0x000120b1


# ============================================================================
# OEM SPARE AREA (0x00013000 - 0x00013100)
# ============================================================================

ADDR_OEM_SPARE_START = 0x00013000
ADDR_OEM_SPARE_END = 0x00013100


# ============================================================================
# COMMANDS AREA (0x00100000 - 0x00100003)
# ============================================================================

# Blink command
ADDR_CMD_BLINK = 0x00100000  # 1 byte

# System reboot command
ADDR_CMD_REBOOT = 0x00100001  # 1 byte

# Load default parameters (equivalent to hardware hard reset)
ADDR_CMD_LOAD_DEFAULT = 0x00100002  # 1 byte


# ============================================================================
# FIRMWARE AREA (0x00700000 - 0x00800000)
# ============================================================================

ADDR_FIRMWARE_START = 0x00700000
ADDR_FIRMWARE_END = 0x00800000


# ============================================================================
# UPGRADE FIRMWARE AREA (0x00900000 - 0x00900011)
# ============================================================================

ADDR_UPGRADE_FW_START = 0x00900000
ADDR_UPGRADE_FW_INFO = 0x00900000  # Firmware information
ADDR_UPGRADE_FW_FLASH_ERASE = 0x00900010  # Start firmware upgrade


# ============================================================================
# CONSTANTS
# ============================================================================

# Number of channels
NUM_CHANNELS = 4

# Source selection values
SOURCE_MUTED = -1  # Special value for muted channel
SOURCE_MIN = -1
SOURCE_MAX = 31

# Mute/unmute values
MUTE_OFF = 0
MUTE_ON = 1

# Standby states
STANDBY_DEACTIVATE = 0
STANDBY_ACTIVATE = 1

# Fault codes
FAULT_CODES = {
    0x00: "No Fault",
    0x01: "HWGoodT",
    0x02: "PGoodPOn",
    0x03: "CtrlVer",
    0x04: "RailsPOn",
    0x05: "RailsOverV",
    0x06: "RailsUnderV",
    0x07: "OutDC",
    0x08: "Fan Broken",
    0x09: "Fan Short",
    0x0A: "Fan Stuck",
    0x0B: "Software",
    0x0C: "MainBoardVer",
    0x0D: "PGoodMon",
    0x0E: "FuseBlown",
    0x0F: "PsuTemp",
    0x10: "HiFreq",
    0x11: "Model",
    0x12: "OverCurrPOn",
}

# Mute codes (bit positions in MUTE_CODE_FLAGS)
MUTE_CODES = {
    3: "Positive Rail out of range",
    4: "Negative Rails out of range",
    5: "Short Circuit",
    8: "Over Temperature",
    9: "High Frequency",
    14: "Mains Under Voltage",
    15: "Mains Over Voltage",
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_gain_address(channel: int) -> int:
    """Get user gain address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_USER_GAIN_CH1 + ((channel - 1) * 4)


def get_user_mute_address(channel: int) -> int:
    """Get user mute address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_USER_MUTE_CH1 + (channel - 1)


def get_source_id_address(channel: int) -> int:
    """Get source ID address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_SOURCE_ID_CH1 + ((channel - 1) * 4)


def get_priority_source_address(channel: int) -> int:
    """Get priority source address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_PRIORITY_SOURCE_CH1 + ((channel - 1) * 4)


def get_zone_gain_address(channel: int) -> int:
    """Get zone gain address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_ZONE_GAIN_CH1 + ((channel - 1) * 4)


def get_zone_mute_address(channel: int) -> int:
    """Get zone mute address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_ZONE_MUTE_CH1 + (channel - 1)


def get_temp_channel_address(channel: int) -> int:
    """Get temperature sensor address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_TEMP_CH1 + ((channel - 1) * 4)


def get_mute_code_flags_address(channel: int) -> int:
    """Get mute code flags address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_MUTE_CODE_FLAGS_CH1 + ((channel - 1) * 4)


def get_user_eq_channel_start(channel: int) -> int:
    """Get user EQ start address for given channel (1-4)."""
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    return ADDR_USER_EQ_CH1_START + ((channel - 1) * 0x60)  # 96 bytes per channel (4 bands * 24 bytes)


def get_user_eq_biquad_address(channel: int, band: int) -> int:
    """
    Get user EQ BiQuad address for given channel (1-4) and band (1-4).

    Args:
        channel: Channel number (1-4)
        band: EQ band number (1-4)

    Returns:
        Memory address of the BiQuad structure
    """
    if not 1 <= channel <= NUM_CHANNELS:
        raise ValueError(f"Channel must be 1-{NUM_CHANNELS}")
    if not 1 <= band <= NUM_EQ_BANDS:
        raise ValueError(f"Band must be 1-{NUM_EQ_BANDS}")

    channel_start = get_user_eq_channel_start(channel)
    return channel_start + ((band - 1) * EQ_BIQUAD_SIZE)
