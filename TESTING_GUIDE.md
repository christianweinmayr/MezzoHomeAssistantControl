# Testing Guide - Powersoft Mezzo Home Assistant Integration

## Prerequisites

1. **Home Assistant** 2024.1+ installed and running
2. **Powersoft Mezzo 602 AD** amplifier on your network
3. Network connectivity between Home Assistant and the amplifier
4. UDP port 8002 accessible (no firewall blocking)

## Installation

### Method 1: Manual Installation (Development)

1. Copy the integration to your Home Assistant custom_components directory:
   ```bash
   cd /path/to/homeassistant/config
   mkdir -p custom_components
   cp -r /path/to/MezzoHomeAssistantControl/custom_components/powersoft_mezzo custom_components/
   ```

2. Restart Home Assistant:
   ```bash
   ha core restart
   ```
   Or use the UI: Settings → System → Restart

3. Clear browser cache to ensure UI updates are loaded

### Method 2: Direct Clone (Alternative)

```bash
cd /path/to/homeassistant/config/custom_components
git clone https://github.com/christianweinmayr/MezzoHomeAssistantControl.git temp
mv temp/custom_components/powersoft_mezzo .
rm -rf temp
```

## Configuration

### Option 1: Auto-Discovery (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Powersoft Mezzo"**
4. Select **"Auto-discover amplifiers"**
5. Wait for discovery to complete (5 seconds)
6. Select your amplifier from the list
7. Optionally provide a custom name
8. Click **Submit**

### Option 2: Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Powersoft Mezzo"**
4. Select **"Manual configuration"**
5. Enter the amplifier's IP address
6. Enter port (default: 8002)
7. Provide a name
8. Click **Submit**

## Verification

### 1. Check Integration Status

- Go to **Settings** → **Devices & Services**
- You should see **"Powersoft Mezzo"** with status **"Configured"**
- Click on the integration to see the device card

### 2. Verify Entities

The integration should create the following entities:

**Switches (5 total):**
- `switch.mezzo_power` - Main power control
- `switch.mezzo_mute_channel_1` - Channel 1 mute
- `switch.mezzo_mute_channel_2` - Channel 2 mute
- `switch.mezzo_mute_channel_3` - Channel 3 mute
- `switch.mezzo_mute_channel_4` - Channel 4 mute

**Numbers (4 total):**
- `number.mezzo_volume_channel_1` - Channel 1 volume (0-100%)
- `number.mezzo_volume_channel_2` - Channel 2 volume (0-100%)
- `number.mezzo_volume_channel_3` - Channel 3 volume (0-100%)
- `number.mezzo_volume_channel_4` - Channel 4 volume (0-100%)

**Selects (4 total):**
- `select.mezzo_input_source_channel_1` - Channel 1 input
- `select.mezzo_input_source_channel_2` - Channel 2 input
- `select.mezzo_input_source_channel_3` - Channel 3 input
- `select.mezzo_input_source_channel_4` - Channel 4 input

**Sensors (3 total):**
- `sensor.mezzo_transformer_temperature` - Transformer temp (°C)
- `sensor.mezzo_heatsink_temperature` - Heatsink temp (°C)
- `sensor.mezzo_fault_code` - Current fault status

**Buttons (4 total):**
- `button.mezzo_preset_1` - Load preset 1
- `button.mezzo_preset_2` - Load preset 2
- `button.mezzo_preset_3` - Load preset 3
- `button.mezzo_preset_4` - Load preset 4

### 3. Test Basic Functions

#### Power Control
```yaml
# Turn on (exit standby)
service: switch.turn_on
target:
  entity_id: switch.mezzo_power

# Turn off (enter standby)
service: switch.turn_off
target:
  entity_id: switch.mezzo_power
```

#### Volume Control
```yaml
# Set channel 1 volume to 50%
service: number.set_value
target:
  entity_id: number.mezzo_volume_channel_1
data:
  value: 50
```

#### Mute Control
```yaml
# Mute channel 1
service: switch.turn_on
target:
  entity_id: switch.mezzo_mute_channel_1

# Unmute channel 1
service: switch.turn_off
target:
  entity_id: switch.mezzo_mute_channel_1
```

#### Input Selection
```yaml
# Select source 1 for channel 1
service: select.select_option
target:
  entity_id: select.mezzo_input_source_channel_1
data:
  option: "Source 1"
```

#### Load Preset
```yaml
# Load preset 1
service: button.press
target:
  entity_id: button.mezzo_preset_1
```

## Testing Protocol Communication

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.powersoft_mezzo: debug
```

Restart Home Assistant and check logs:

```bash
tail -f /config/home-assistant.log | grep powersoft_mezzo
```

### Expected Log Messages

**Successful Connection:**
```
INFO ... Connecting to 192.168.1.100:8002
INFO ... Successfully connected to 192.168.1.100:8002
INFO ... Updated amplifier state: {'standby': False, 'volumes': {1: 0.5, ...}, ...}
```

**Discovery:**
```
INFO ... Starting amplifier discovery...
INFO ... Broadcasting discovery packet on port 8002
INFO ... Discovered amplifier at 192.168.1.100
INFO ... Discovery complete: found 1 amplifier(s)
```

## Troubleshooting

### Issue: No Devices Found During Discovery

**Possible Causes:**
- Amplifier is off or in deep standby
- Firewall blocking UDP port 8002
- Amplifier on different subnet/VLAN
- Network switch blocking broadcast

**Solutions:**
1. Ensure amplifier is powered on
2. Try manual configuration with IP address
3. Check firewall rules:
   ```bash
   sudo ufw allow 8002/udp  # Linux
   ```
4. Verify network connectivity:
   ```bash
   ping <amplifier-ip>
   ```

### Issue: Connection Timeout

**Error:** `Failed to connect: Timeout communicating with amplifier`

**Solutions:**
1. Verify IP address is correct
2. Check amplifier is on same network
3. Increase timeout in integration options (Settings → Devices & Services → Powersoft Mezzo → Configure)
4. Check network latency:
   ```bash
   ping -c 10 <amplifier-ip>
   ```

### Issue: Entities Not Updating

**Possible Causes:**
- Coordinator update interval too long
- Amplifier in standby/sleep mode
- Network issues

**Solutions:**
1. Reduce scan interval in options (default: 5 seconds)
2. Check amplifier is responding:
   ```bash
   # From Home Assistant container/host
   nc -u <amplifier-ip> 8002
   ```
3. Manually refresh: Developer Tools → States → select entity → "Refresh"

### Issue: Values Not Changing

**Symptom:** Switches/numbers don't respond to changes

**Debug Steps:**
1. Check logs for error messages
2. Verify write permissions (not all areas may be writable)
3. Test with lower-level protocol:
   ```python
   # In Home Assistant Python environment
   from custom_components.powersoft_mezzo.mezzo_client import MezzoClient

   client = MezzoClient("192.168.1.100")
   await client.connect()
   await client.set_standby(False)  # Should power on
   ```

## Advanced Testing

### Network Packet Capture

Capture UDP traffic to verify protocol communication:

```bash
# On Home Assistant host
sudo tcpdump -i any -n udp port 8002 -X

# Look for:
# - STX byte (0x02) at start
# - ETX byte (0x03) at end
# - Magic number "MZO" in responses
```

### Direct Protocol Testing

Use Python to test protocol directly:

```python
import asyncio
from custom_components.powersoft_mezzo.mezzo_client import MezzoClient, discover_amplifiers

async def test():
    # Discovery
    devices = await discover_amplifiers(timeout=5.0)
    print(f"Found devices: {devices}")

    # Connect to first device
    if devices:
        host = list(devices.keys())[0]
        async with MezzoClient(host) as client:
            # Test power
            await client.set_standby(False)
            standby = await client.get_standby_state()
            print(f"Standby: {standby}")

            # Test volume
            await client.set_volume(1, 0.5)  # 50%
            volume = await client.get_volume(1)
            print(f"Volume CH1: {volume}")

            # Test all state
            state = await client.get_all_state()
            print(f"State: {state}")

asyncio.run(test())
```

## Performance Optimization

### Optimal Settings

For best performance:

```yaml
# In integration options
timeout: 2.0          # 2 seconds (increase if network is slow)
scan_interval: 5      # 5 seconds (decrease for faster updates, increase to reduce network traffic)
```

### Network Considerations

- **LAN:** scan_interval can be as low as 1-2 seconds
- **VLAN/Complex network:** increase to 10+ seconds
- **WiFi:** may need 5-10 seconds for stability

## Automation Examples

### Morning Amplifier Startup

```yaml
automation:
  - alias: "Morning Amplifier On"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.mezzo_power
      - delay:
          seconds: 2
      - service: number.set_value
        target:
          entity_id:
            - number.mezzo_volume_channel_1
            - number.mezzo_volume_channel_2
        data:
          value: 30
```

### Temperature Alert

```yaml
automation:
  - alias: "Amplifier Overheat Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.mezzo_transformer_temperature
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "Amplifier temperature high: {{ states('sensor.mezzo_transformer_temperature') }}°C"
```

## Next Steps

1. ✅ Verify all entities are created
2. ✅ Test basic controls (power, volume, mute)
3. ✅ Monitor temperature sensors
4. ✅ Test input source switching
5. ✅ Try preset loading
6. ✅ Check logs for errors
7. Create automations
8. Report any issues to GitHub

## Success Criteria

- [ ] Integration shows as "Configured"
- [ ] All 20 entities are created
- [ ] Power control works (on/off)
- [ ] Volume adjustment works
- [ ] Mute functions properly
- [ ] Input switching responds
- [ ] Temperature readings are accurate
- [ ] No errors in logs
- [ ] Updates occur within scan_interval
- [ ] Preset loading functions

## Reporting Issues

If you encounter problems:

1. Enable debug logging
2. Capture relevant log entries
3. Note exact error messages
4. Document steps to reproduce
5. Create issue at: https://github.com/christianweinmayr/MezzoHomeAssistantControl/issues

Include:
- Home Assistant version
- Integration version
- Amplifier firmware version
- Network setup
- Relevant logs

---

**Happy Testing!** 🎉
