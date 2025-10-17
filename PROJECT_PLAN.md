# Powersoft Mezzo 602 AD - Home Assistant Integration Project

## Project Overview

Custom Home Assistant integration for the Powersoft Mezzo 602 AD amplifier using the PBus protocol over UDP (port 8002).

**Author:** Claude Code
**Date Started:** 2025-10-17
**Target Device:** Powersoft Mezzo 602 AD
**Protocol:** PBus over UDP
**Home Assistant Version:** 2024.x+

---

## Project Goals

- ✅ Implement complete PBus protocol support
- ✅ Auto-discovery of Mezzo amplifiers on the network
- ✅ Full control of power, volume, mute, and input selection
- ✅ Scene/preset support for quick configuration changes
- ✅ Real-time monitoring of amplifier status and health
- ✅ Native Home Assistant integration with proper entity platforms

---

## Architecture

### Component Structure

```
custom_components/powersoft_mezzo/
├── __init__.py                 # Integration setup and coordinator
├── manifest.json               # Integration metadata
├── config_flow.py              # Configuration UI flow
├── const.py                    # Constants and defaults
├── pbus_protocol.py           # ✅ PBus protocol implementation
├── mezzo_memory_map.py        # ✅ Memory address constants
├── udp_manager.py             # UDP communication layer
├── mezzo_client.py            # High-level amplifier API
├── discovery.py               # Network device discovery
├── coordinator.py             # Data update coordinator
├── switch.py                  # Power and mute switches
├── number.py                  # Volume/gain controls
├── select.py                  # Input source selection
├── sensor.py                  # Status sensors
└── button.py                  # Preset/scene buttons
```

### Key Features

1. **Protocol Layer** (✅ Completed)
   - Binary PBus packet building and parsing
   - CRC16-CCITT checksum calculation
   - STX/ETX/ESC character escaping
   - Support for Read and Write commands
   - Multicommand support for batching operations

2. **Memory Map** (✅ Completed)
   - Complete address space documentation
   - Helper functions for channel-based addressing
   - Constants for all control and status registers

3. **Communication Layer** (In Progress)
   - Async UDP socket management
   - Request/response matching via TAG
   - Connection timeout handling
   - Auto-reconnection logic

4. **Client API** (Pending)
   - High-level control methods
   - Device discovery
   - State polling
   - Error handling

5. **Home Assistant Integration** (Pending)
   - Config flow with auto-discovery
   - Multiple entity platforms
   - Centralized coordinator
   - Proper error handling and logging

---

## Todo List & Progress

### ✅ Phase 1: Protocol Foundation (Completed)

- [x] **Task 1.1:** Create project directory structure
  - Status: ✅ Completed
  - Files: `custom_components/powersoft_mezzo/`
  - Commit: Initial project structure

- [x] **Task 1.2:** Implement PBus protocol packet builder and parser
  - Status: ✅ Completed
  - File: `pbus_protocol.py`
  - Features:
    - `PBusPacket.build_request()` - Build request packets
    - `PBusPacket.parse_response()` - Parse response packets
    - `ReadCommand` and `WriteCommand` classes
    - Commit: Implemented PBus protocol layer

- [x] **Task 1.3:** Implement CRC16-CCITT calculator
  - Status: ✅ Completed
  - File: `pbus_protocol.py`
  - Features:
    - CRC16 lookup table
    - `calculate_crc16()` function
  - Commit: Added CRC16 implementation

- [x] **Task 1.4:** Implement character escaping engine
  - Status: ✅ Completed
  - File: `pbus_protocol.py`
  - Features:
    - `escape_data()` function
    - `unescape_data()` function
    - Proper STX/ETX/ESC handling
  - Commit: Added escaping engine

- [x] **Task 1.5:** Create memory map constants module
  - Status: ✅ Completed
  - File: `mezzo_memory_map.py`
  - Features:
    - All memory area addresses
    - Helper functions for channel addressing
    - Fault and mute code constants
  - Commit: Added memory map constants

### 🔄 Phase 2: Communication Layer (In Progress)

- [ ] **Task 2.1:** Create project plan and setup Git repository
  - Status: 🔄 In Progress
  - Files: `PROJECT_PLAN.md`, `.git/`
  - Next: Initialize Git, create GitHub repo, push initial commit

- [ ] **Task 2.2:** Implement UDP communication manager
  - Status: ⏳ Pending
  - File: `udp_manager.py`
  - Features:
    - Async UDP socket creation
    - Send/receive with timeout
    - TAG-based response matching
    - Auto-reconnect on failure
  - Next: Create udp_manager.py

- [ ] **Task 2.3:** Create high-level amplifier client
  - Status: ⏳ Pending
  - File: `mezzo_client.py`
  - Features:
    - Connection management
    - Control methods (power, volume, mute, source)
    - State reading methods
    - Batch operations
  - Next: After UDP manager

- [ ] **Task 2.4:** Implement discovery service
  - Status: ⏳ Pending
  - File: `discovery.py`
  - Features:
    - UDP broadcast discovery
    - Device info parsing
    - List discovered amplifiers
  - Next: After client API

### ⏳ Phase 3: Home Assistant Integration (Pending)

- [ ] **Task 3.1:** Create integration skeleton
  - Status: ⏳ Pending
  - Files: `manifest.json`, `__init__.py`, `const.py`
  - Features:
    - Integration metadata
    - Entry setup/unload
    - Platform forwarding
  - Next: After discovery service

- [ ] **Task 3.2:** Implement config flow with auto-discovery
  - Status: ⏳ Pending
  - File: `config_flow.py`
  - Features:
    - Auto-discovery flow
    - Manual IP entry
    - Options flow for settings
  - Next: After integration skeleton

- [ ] **Task 3.3:** Create data coordinator
  - Status: ⏳ Pending
  - File: `coordinator.py`
  - Features:
    - Centralized state polling
    - Batch read operations
    - Error handling
    - Configurable update interval
  - Next: After config flow

- [ ] **Task 3.4:** Implement switch platform (power/mute)
  - Status: ⏳ Pending
  - File: `switch.py`
  - Features:
    - Power switch (standby control)
    - 4 mute switches (per channel)
  - Next: After coordinator

- [ ] **Task 3.5:** Implement number platform (volume control)
  - Status: ⏳ Pending
  - File: `number.py`
  - Features:
    - 4 volume/gain entities (per channel)
    - Range: 0-100% (converted to linear gain)
  - Next: After switch platform

- [ ] **Task 3.6:** Implement select platform (input selection)
  - Status: ⏳ Pending
  - File: `select.py`
  - Features:
    - 4 input selection dropdowns (per channel)
    - Options: Source 1-31, Muted
  - Next: After number platform

- [ ] **Task 3.7:** Implement sensor platform (status monitoring)
  - Status: ⏳ Pending
  - File: `sensor.py`
  - Features:
    - Standby state sensor
    - Temperature sensors (transformer, heatsink, channels)
    - Fault code sensor
    - Mute code sensors per channel
  - Next: After select platform

- [ ] **Task 3.8:** Implement button platform (presets/scenes)
  - Status: ⏳ Pending
  - File: `button.py`
  - Features:
    - Preset/scene load buttons
    - Configurable preset list
  - Next: After sensor platform

### ⏳ Phase 4: Testing & Refinement (Pending)

- [ ] **Task 4.1:** Add comprehensive error handling and logging
  - Status: ⏳ Pending
  - Files: All modules
  - Features:
    - Proper exception handling
    - Debug logging
    - User-friendly error messages
  - Next: After all platforms implemented

- [ ] **Task 4.2:** Test integration with real device
  - Status: ⏳ Pending
  - Features:
    - Test all control functions
    - Verify state updates
    - Test error scenarios
    - Optimize polling intervals
  - Next: Final step

---

## Technical Specifications

### PBus Protocol Details

**Transport:** UDP on port 8002
**Endianness:** Little-endian for multi-byte values
**Frame Format:**

**Request:**
```
[STX] [TAG (4)] [PBus Commands...] [CRC16 (2)] [ETX]
```

**Response:**
```
[STX] [MZO (3)] [ProtocolID (2)] [TAG (4)] [PBus Replies...] [CRC16 (2)] [ETX]
```

**Special Bytes:**
- STX: 0x02 (Start of frame)
- ETX: 0x03 (End of frame)
- ESC: 0x1B (Escape character)

**Escaping:** Special bytes within payload are escaped by prepending ESC and adding 0x40

**CRC16:** CRC16-CCITT polynomial (x16+x12+x5+1)

### Key Memory Addresses

| Function | Address | Type | Access |
|----------|---------|------|--------|
| Standby Trigger | 0x0000a000 | uint32 | W |
| Standby State | 0x0000b638 | uint32 | R |
| User Gain CH1-4 | 0x00004000-0x0000400c | Float | R/W |
| User Mute CH1-4 | 0x00004024-0x00004027 | uint8 | R/W |
| Source ID CH1-4 | 0x00002200-0x0000220c | uint32 | R/W |
| Temperature Sensors | 0x0000b000-0x0000b100 | Float | R |
| Fault Code | 0x0000b656 | uint8 | R |

---

## Configuration Example

```yaml
# configuration.yaml (auto-configured via UI)
powersoft_mezzo:
  - host: 192.168.1.100
    name: "Living Room Amp"
    scan_interval: 5
    channels:
      1: "Front Left"
      2: "Front Right"
      3: "Rear Left"
      4: "Rear Right"
```

---

## Entities Created

After integration setup, the following entities will be created:

**Switches:**
- `switch.mezzo_power` - Main power (standby) control
- `switch.mezzo_mute_ch1` - Channel 1 mute
- `switch.mezzo_mute_ch2` - Channel 2 mute
- `switch.mezzo_mute_ch3` - Channel 3 mute
- `switch.mezzo_mute_ch4` - Channel 4 mute

**Numbers (Volume/Gain):**
- `number.mezzo_volume_ch1` - Channel 1 volume (0-100%)
- `number.mezzo_volume_ch2` - Channel 2 volume (0-100%)
- `number.mezzo_volume_ch3` - Channel 3 volume (0-100%)
- `number.mezzo_volume_ch4` - Channel 4 volume (0-100%)

**Selects (Input Selection):**
- `select.mezzo_input_ch1` - Channel 1 input source
- `select.mezzo_input_ch2` - Channel 2 input source
- `select.mezzo_input_ch3` - Channel 3 input source
- `select.mezzo_input_ch4` - Channel 4 input source

**Sensors (Status Monitoring):**
- `sensor.mezzo_standby_state` - Current power state
- `sensor.mezzo_temp_transformer` - Transformer temperature
- `sensor.mezzo_temp_heatsink` - Heatsink temperature
- `sensor.mezzo_temp_ch1` - Channel 1 temperature
- `sensor.mezzo_temp_ch2` - Channel 2 temperature
- `sensor.mezzo_temp_ch3` - Channel 3 temperature
- `sensor.mezzo_temp_ch4` - Channel 4 temperature
- `sensor.mezzo_fault_code` - Active fault code
- `sensor.mezzo_mute_flags_ch1` - Channel 1 active mute reasons
- `sensor.mezzo_mute_flags_ch2` - Channel 2 active mute reasons
- `sensor.mezzo_mute_flags_ch3` - Channel 3 active mute reasons
- `sensor.mezzo_mute_flags_ch4` - Channel 4 active mute reasons

**Buttons (Presets/Scenes):**
- `button.mezzo_preset_1` - Load preset 1
- `button.mezzo_preset_2` - Load preset 2
- `button.mezzo_preset_N` - Load preset N

---

## Progress Summary

**Completed:** 5 tasks (Protocol Foundation - Phase 1)
**In Progress:** 1 task (Git setup)
**Pending:** 13 tasks (Phases 2-4)
**Overall Progress:** ~26% complete

---

## Next Steps

1. ✅ Complete Git repository setup and initial commit
2. Implement UDP communication manager
3. Create amplifier client API
4. Begin Home Assistant integration skeleton

---

## Notes

- All float values for gain/volume are in linear scale (0.0 - 1.0 in protocol)
- Home Assistant UI will show 0-100% for user convenience
- Auto-discovery uses UDP broadcast on port 8002
- Default polling interval: 5 seconds (configurable)
- Supports multicommand for efficient batch operations
- NAK responses (SIZE32=0) indicate operation failure

---

## References

- Powersoft Mezzo Protocol Specification v1.2.3
- Home Assistant Integration Development Documentation
- UDP/IP Networking Standards
