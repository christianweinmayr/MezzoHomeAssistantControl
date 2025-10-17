# Powersoft Mezzo 602 AD - Home Assistant Integration

Custom Home Assistant integration for controlling the Powersoft Mezzo 602 AD amplifier via the PBus protocol over UDP (port 8002).

## Features

- ✅ **Auto-discovery** of Mezzo amplifiers on your network
- ✅ **Power Control** - Turn amplifier on/off (standby mode)
- ✅ **Volume Control** - Independent volume control for all 4 channels
- ✅ **Mute Control** - Mute/unmute individual channels
- ✅ **Input Selection** - Select audio source for each channel
- ✅ **Status Monitoring** - Temperature sensors, fault codes, and more
- ✅ **Scene Support** - Quick preset loading
- ✅ **Native Integration** - Proper Home Assistant entity platforms

## Status

🔄 **Work in Progress** - Phase 1 (Protocol Foundation) completed, Phase 2 (Communication Layer) in progress.

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed progress and roadmap.

## Current Progress

- ✅ PBus Protocol Implementation (complete)
- ✅ Memory Map Constants (complete)
- 🔄 UDP Communication Manager (in progress)
- ⏳ Amplifier Client API (pending)
- ⏳ Home Assistant Integration (pending)

## Requirements

- Home Assistant 2024.1+
- Powersoft Mezzo 602 AD amplifier
- Network connectivity (UDP port 8002)

## Installation

_Installation instructions will be added once the integration is complete._

### Manual Installation (Development)

1. Copy `custom_components/powersoft_mezzo` to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Powersoft Mezzo"
5. Follow the configuration wizard

## Configuration

Configuration is done through the Home Assistant UI with auto-discovery support.

### Manual Configuration (Optional)

```yaml
# configuration.yaml
powersoft_mezzo:
  host: 192.168.1.100
  name: "Living Room Amp"
  scan_interval: 5
  channels:
    1: "Front Left"
    2: "Front Right"
    3: "Rear Left"
    4: "Rear Right"
```

## Entities

The integration creates the following entities:

- **1x Power Switch** - Main amplifier power control
- **4x Volume Numbers** - Per-channel volume (0-100%)
- **4x Mute Switches** - Per-channel mute control
- **4x Input Selects** - Per-channel source selection
- **Multiple Sensors** - Temperatures, status, faults
- **Preset Buttons** - Quick scene loading

## Technical Details

### Protocol

- **Transport:** UDP on port 8002
- **Protocol:** Powersoft PBus (binary protocol)
- **Endianness:** Little-endian
- **CRC:** CRC16-CCITT
- **Escaping:** STX/ETX/ESC character escaping

### Architecture

```
pbus_protocol.py      → Core protocol implementation
mezzo_memory_map.py   → Memory address constants
udp_manager.py        → UDP communication layer
mezzo_client.py       → High-level amplifier API
coordinator.py        → Data update coordinator
[platform].py         → Home Assistant entity platforms
```

## Development

### Project Structure

```
MezzoHomeAssistantControl/
├── custom_components/
│   └── powersoft_mezzo/
│       ├── __init__.py
│       ├── pbus_protocol.py         ✅
│       ├── mezzo_memory_map.py      ✅
│       ├── udp_manager.py           🔄
│       └── ... (other modules)
├── PROJECT_PLAN.md                  ✅
├── README.md                        ✅
└── mezzo_protocol.md               ✅ (Protocol spec)
```

### Testing

_Testing instructions will be added once implementation is complete._

## Contributing

This is a personal project currently in development. Contributions, suggestions, and feedback are welcome once the initial implementation is complete.

## License

This project is provided as-is for personal use.

## Disclaimer

This is an unofficial integration not affiliated with or endorsed by Powersoft. Use at your own risk.

## Acknowledgments

- Powersoft for the Mezzo amplifier and PBus protocol documentation
- Home Assistant community for integration development resources
- Claude Code for implementation assistance

## Support

For issues and questions, please use the GitHub issue tracker once the repository is public.

---

**Status:** 🔄 Active Development | **Progress:** ~26% Complete | **Last Updated:** 2025-10-17
