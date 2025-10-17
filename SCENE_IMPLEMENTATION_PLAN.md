# Scene/Preset Implementation Plan - PBus Protocol Only

## Project Status: COMPLETE - Stage 1 Implemented ✅
**Created:** October 17, 2025
**Updated:** October 17, 2025 - EQ support added
**Issue:** Current preset implementation using `ADDR_PRESET_TYPE_SPK` addresses doesn't work
**Goal:** Implement scene/preset switching WITHOUT View Host or extra software using ONLY PBus protocol

**CRITICAL UPDATE:** Scenes now include full 4-band parametric EQ settings per channel!

---

## Problem Statement

### Current Situation
- Integration successfully controls: power, volume, mute, input selection, temperature monitoring
- **NOT working:** Scene/preset loading via button platform
- Current implementation uses deprecated addresses: `0x000062d4` - `0x000062e0` (Preset Type)
- User reports: "old endpoint doesn't work anymore"

### View Host Issue
- New approach mentioned: `/scene/active/<IdConfig>/<SceneId>`
- This appears to be HTTP-based REST API (View Host web interface)
- **Requirement:** Must avoid View Host dependency - PBus protocol only

### Key Questions
1. Are there alternative PBus memory addresses for scene control?
2. Can scenes be implemented as software snapshots (HA native)?
3. What does View Host actually send via PBus when loading a scene?
4. Are scenes device-wide or per-channel configurations?

---

## Protocol Analysis

### Examined Memory Areas

#### 1. **Preset Type Addresses (DEPRECATED - NOT WORKING)**
```
0x000062d4 - Preset Type Speaker 1 (int32, 4 bytes, R/W)
0x000062d8 - Preset Type Speaker 2 (int32, 4 bytes, R/W)
0x000062dc - Preset Type Speaker 3 (int32, 4 bytes, R/W)
0x000062e0 - Preset Type Speaker 4 (int32, 4 bytes, R/W)
```
**Status:** User reports these don't work anymore

#### 2. **Command Area (Triggers/Actions)**
```
0x00100000 - 0x00100001  Blink command
0x00100001 - 0x00100002  System Reboot command
0x00100002 - 0x00100003  Load Default Parameters (Hard Reset)
```
**Analysis:** No scene/preset load command found in command area

#### 3. **AutoSetup Area (Speaker Calibration)**
```
0x0000c000 - 0x0000ef04  AutoSetup area (speaker calibration)
0x0000ef00 - AutoSetup Start trigger
```
**Analysis:** This is for automatic speaker calibration, not user scenes

#### 4. **User Control Area (Current State)**
```
0x00004000-0x0000400c  User Gain (volumes) - 4 channels
0x00004024-0x00004027  User Mute - 4 channels
0x00002200-0x0000220c  Source ID - 4 channels
0x0000a000             Standby trigger
```
**Analysis:** These are the state registers we currently control successfully

#### 5. **Zone Block Area**
```
0x0000f000 - 0x0000f340  Amplifier zones information
```
**Status:** Need to investigate if zones relate to scenes

---

## Implementation Approaches

### **Approach 1: Software-Based Scenes (HA Native)**
**Complexity:** Low
**Pros:** ✅
**Cons:** ❌

#### Description
Implement scenes entirely in Home Assistant without relying on amplifier's scene memory.

#### How It Works
1. **Scene Storage:** Store scene configurations in HA integration config/options
2. **Scene Structure:** Each scene contains:
   ```python
   {
     "scene_id": 1,
     "name": "Cinema Mode",
     "config": {
       "volumes": [0.6, 0.6, 0.5, 0.5],      # Ch1-4
       "mutes": [False, False, False, True],  # Ch1-4
       "sources": [1, 1, 2, -1],              # Ch1-4
       "standby": False
     }
   }
   ```
3. **Scene Loading:** When button pressed:
   - Read scene config from storage
   - Build multicommand with all writes
   - Send single PBus packet with all changes
   - Coordinator refreshes state

#### Implementation Steps
1. Create scene storage in integration options
2. Add scene configuration UI in options flow
3. Modify button platform to read scene config and apply via multicommand
4. Add scene management service for automation

#### Pros
- ✅ Full control over scene definitions
- ✅ No dependency on amplifier firmware
- ✅ Easy to backup/restore scenes
- ✅ Can include custom parameters (delays, fade times in future)
- ✅ Works with any Mezzo model
- ✅ User can create unlimited scenes via HA UI

#### Cons
- ❌ Doesn't use amplifier's built-in scene capability
- ❌ Requires configuration via HA (can't use ArmoníaPlus scenes)
- ❌ Scene data not portable to other control systems
- ❌ More complex configuration UI needed

#### Code Changes Required
- `config_flow.py`: Add scene configuration in options flow
- `button.py`: Rewrite to apply stored scene configs
- `mezzo_client.py`: Add `apply_scene(scene_config)` method
- `const.py`: Add scene storage keys
- `strings.json`: Add scene configuration UI strings

---

### **Approach 2: Reverse Engineer View Host**
**Complexity:** Medium
**Pros:** ✅
**Cons:** ❌

#### Description
Capture network traffic when View Host loads a scene, analyze PBus packets to discover the "real" scene control method.

#### How It Works
1. **Setup packet capture:** tcpdump/Wireshark on port 8002
2. **Trigger scene load:** Use View Host to load different scenes
3. **Analyze PBus packets:** Look for:
   - Write commands to unknown addresses
   - Sequence of writes that constitute a scene
   - Special opcodes or command patterns
4. **Reverse engineer:** Determine if scenes are:
   - Single write to special address
   - Batch writes to multiple addresses
   - Trigger + preset ID combination

#### Implementation Steps
1. Install View Host on test system
2. Configure amplifier and create test scenes
3. Run packet capture: `tcpdump -i any -n udp port 8002 -X -w capture.pcap`
4. Load scenes 1-4 in View Host
5. Analyze captured PBus frames:
   - Identify STX (0x02), ETX (0x03) boundaries
   - Extract OPCODE, ADDR32, SIZE32, DATA
   - Look for patterns specific to scene loading
6. Document findings and implement in `mezzo_client.py`

#### Pros
- ✅ Discovers official scene control mechanism
- ✅ Works with ArmoníaPlus-configured scenes
- ✅ Uses amplifier's native scene capability
- ✅ Likely more reliable long-term
- ✅ Scenes portable across control systems

#### Cons
- ❌ Requires View Host installation for testing
- ❌ May discover it's just batch writes (same as Approach 1)
- ❌ Time-consuming analysis
- ❌ May not find anything new

#### Required Tools
- Wireshark or tcpdump
- View Host software
- Powersoft ArmoníaPlus (for scene configuration)
- Test amplifier on network

---

### **Approach 3: Explore Undocumented Memory Areas**
**Complexity:** High
**Pros:** ✅
**Cons:** ❌

#### Description
Systematically probe memory areas mentioned in protocol spec but not fully documented.

#### Target Areas to Investigate

**Zone Block Area:**
```
0x0000f000 - 0x0000f340  Amplifier zones information
```
- May contain zone-based scene configurations
- Could have scene recall addresses per zone

**OEM Spare Area:**
```
0x00013000 - 0x00013100  Empty Spare Area dedicated to OEM
```
- Might contain OEM-specific scene storage

**Command Area Extension:**
```
0x00100003+  Potential undocumented commands after Load Default
```
- May have scene load/recall commands

**Preset-Related Unknown Area:**
- Search for addresses near `0x000062d4` that might be updated mechanisms

#### Testing Methodology
1. **Read Operations:** Try reading from target addresses
2. **Pattern Analysis:** Look for data structures that resemble scene configs
3. **Write Testing:** (CAUTION) Try writing preset IDs to discovered addresses
4. **Response Analysis:** Check if writes trigger state changes

#### Implementation Steps
1. Create test script with safe read operations
2. Systematically read Zone Block area
3. Document any readable data structures
4. Attempt writes to promising addresses with preset IDs (0-3)
5. Monitor amplifier state changes

#### Pros
- ✅ May discover official scene mechanism
- ✅ Could find simpler single-write solution
- ✅ Deepens protocol knowledge

#### Cons
- ❌ May find nothing useful
- ❌ Risk of triggering unwanted amplifier behavior
- ❌ Time-consuming trial-and-error
- ❌ No guarantee of success

---

### **Approach 4: Hybrid - Scene Snapshots with PBus Storage**
**Complexity:** High
**Pros:** ✅
**Cons:** ❌

#### Description
Store scene configurations in amplifier's user-writable memory areas, then recall by reading and applying.

#### Concept
1. **Scene Storage:** Use OEM Spare Area (0x00013000) to store scene configs
2. **Scene Format:** Binary structure with volumes, mutes, sources per scene
3. **Scene Loading:** Read scene data from spare area, then apply via multicommand

#### Memory Layout Example
```
OEM Spare Area: 0x00013000 - 0x00013100 (256 bytes available)

Scene 0: 0x00013000 - 0x0001301F (32 bytes)
  +0x00: Magic number "SCEN" (4 bytes)
  +0x04: Scene ID (1 byte)
  +0x05: Reserved (1 byte)
  +0x06: Volumes[4] (16 bytes, float32 each)
  +0x16: Mutes[4] (4 bytes, uint8 each)
  +0x1A: Sources[4] (16 bytes, int32 each)

Scene 1: 0x00013020 - 0x0001303F (32 bytes)
Scene 2: 0x00013040 - 0x0001305F (32 bytes)
Scene 3: 0x00013060 - 0x0001307F (32 bytes)
```

#### How Scene Loading Works
```python
async def load_scene_hybrid(self, scene_id: int):
    # 1. Read scene data from OEM spare area
    addr = 0x00013000 + (scene_id * 32)
    cmd = ReadCommand(addr, 32)
    response = await self._udp.send_request([cmd])

    # 2. Parse scene data
    data = response[0].data
    volumes = [struct.unpack('<f', data[6+i*4:10+i*4])[0] for i in range(4)]
    mutes = [data[22+i] for i in range(4)]
    sources = [struct.unpack('<i', data[26+i*4:30+i*4])[0] for i in range(4)]

    # 3. Apply via multicommand
    commands = []
    for ch in range(1, 5):
        commands.append(WriteCommand(get_user_gain_address(ch), float_to_bytes(volumes[ch-1])))
        commands.append(WriteCommand(get_user_mute_address(ch), uint8_to_bytes(mutes[ch-1])))
        commands.append(WriteCommand(get_source_id_address(ch), int32_to_bytes(sources[ch-1])))

    await self._udp.send_request(commands)
```

#### Pros
- ✅ Scenes stored in amplifier (persist across HA restarts)
- ✅ Still independent of View Host
- ✅ Scenes survive network disconnections
- ✅ Could be compatible with other systems

#### Cons
- ❌ OEM Spare Area might not persist across reboots
- ❌ No guarantee spare area is writable
- ❌ Complex implementation
- ❌ Needs initial scene configuration step
- ❌ 256 bytes may limit scene complexity

---

## Recommended Approach: **Approach 1 + Approach 2**

### Phase 1: Immediate Solution (Approach 1)
Implement software-based scenes to unblock user NOW.

**Timeline:** 1-2 hours
**Risk:** Low
**Value:** Immediate functionality

### Phase 2: Optimal Solution (Approach 2)
Reverse engineer View Host to discover official mechanism.

**Timeline:** 2-4 hours (requires View Host setup)
**Risk:** Medium (may not discover anything new)
**Value:** High (authentic scene control)

### Why This Combination?
1. **User gets working scenes immediately** via Approach 1
2. **We discover true mechanism** via Approach 2
3. **If Approach 2 finds nothing**, Approach 1 is already done
4. **If Approach 2 succeeds**, we can migrate to official method
5. **Both approaches use same underlying PBus multicommand**, so code reuse is high

---

## Implementation Plan

### Stage 1: Software-Based Scenes (Immediate)

#### Task 1.1: Update Data Structures
**File:** `const.py`

```python
# Scene configuration keys
CONF_SCENES = "scenes"
DEFAULT_SCENES = [
    {
        "id": 0,
        "name": "Scene 1",
        "volumes": [0.5, 0.5, 0.5, 0.5],
        "mutes": [False, False, False, False],
        "sources": [0, 0, 0, 0],
        "standby": False
    },
    {
        "id": 1,
        "name": "Scene 2",
        "volumes": [0.7, 0.7, 0.3, 0.0],
        "mutes": [False, False, False, True],
        "sources": [1, 1, 2, 0],
        "standby": False
    },
    # ... scenes 3, 4
]
```

#### Task 1.2: Update Client API
**File:** `mezzo_client.py`

```python
async def apply_scene(self, scene_config: dict) -> None:
    """Apply a complete scene configuration via multicommand.

    Args:
        scene_config: Dictionary with keys: volumes, mutes, sources, standby
    """
    commands = []

    # Build all write commands
    for ch in range(1, 5):
        # Volume
        volume = scene_config["volumes"][ch - 1]
        addr = get_user_gain_address(ch)
        commands.append(WriteCommand(addr, float_to_bytes(volume)))

        # Mute
        muted = scene_config["mutes"][ch - 1]
        addr = get_user_mute_address(ch)
        commands.append(WriteCommand(addr, uint8_to_bytes(1 if muted else 0)))

        # Source
        source = scene_config["sources"][ch - 1]
        addr = get_source_id_address(ch)
        commands.append(WriteCommand(addr, int32_to_bytes(source)))

    # Power state
    if "standby" in scene_config:
        value = STANDBY_ACTIVATE if scene_config["standby"] else STANDBY_DEACTIVATE
        commands.append(WriteCommand(ADDR_STANDBY_TRIGGER, uint32_to_bytes(value)))

    # Send all changes in single multicommand
    try:
        await self._udp.send_request(commands)
        _LOGGER.info("Applied scene successfully")
    except Exception as err:
        _LOGGER.error("Failed to apply scene: %s", err)
        raise
```

#### Task 1.3: Update Button Platform
**File:** `button.py`

```python
class MezzoSceneButton(CoordinatorEntity, ButtonEntity):
    """Representation of a scene button."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:palette"

    def __init__(
        self,
        coordinator,
        client: MezzoClient,
        entry: ConfigEntry,
        scene_config: dict,
    ):
        """Initialize the scene button."""
        super().__init__(coordinator)
        self._client = client
        self._scene_config = scene_config
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Powersoft",
            "model": "Mezzo 602 AD",
        }
        self._attr_unique_id = f"{entry.entry_id}_scene_{scene_config['id']}"
        self._attr_name = scene_config["name"]

    async def async_press(self) -> None:
        """Handle the button press - apply the scene."""
        try:
            _LOGGER.info("Applying scene: %s", self._scene_config["name"])
            await self._client.apply_scene(self._scene_config)
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to apply scene %s: %s", self._scene_config["name"], err)
            raise


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mezzo button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]

    entities = []

    # Get scene configurations from entry options or use defaults
    scenes = entry.options.get(CONF_SCENES, DEFAULT_SCENES)

    # Add scene buttons
    for scene in scenes:
        entities.append(
            MezzoSceneButton(
                coordinator,
                client,
                entry,
                scene,
            )
        )

    async_add_entities(entities)
```

#### Task 1.4: Add Scene Configuration UI (Optional)
**File:** `config_flow.py`

Add options flow step for scene configuration:
```python
async def async_step_configure_scenes(self, user_input=None):
    """Configure scene settings."""
    if user_input is not None:
        # Parse and save scene configurations
        return self.async_create_entry(title="", data=user_input)

    # Show scene configuration form
    return self.async_show_form(
        step_id="configure_scenes",
        data_schema=vol.Schema({
            # Scene configuration fields
        })
    )
```

#### Task 1.5: Update Documentation
- Update TESTING_GUIDE.md with scene configuration instructions
- Update README.md with scene feature description
- Add SCENE_IMPLEMENTATION_PLAN.md to docs

---

### Stage 2: Reverse Engineering (Research Phase)

#### Task 2.1: Setup Test Environment
1. Install View Host on test system
2. Configure test amplifier with ArmoníaPlus
3. Create 4 distinct test scenes with obvious settings:
   - Scene 1: All volumes 25%, all unmuted, source 0
   - Scene 2: All volumes 50%, all unmuted, source 1
   - Scene 3: All volumes 75%, all unmuted, source 2
   - Scene 4: Ch1/2 100%, Ch3/4 muted, sources varied

#### Task 2.2: Capture PBus Traffic
```bash
# On Home Assistant host or network gateway
sudo tcpdump -i any -n 'udp port 8002' -X -w mezzo_scene_capture.pcap

# Then in View Host:
# - Load Scene 1
# - Wait 5 seconds
# - Load Scene 2
# - Wait 5 seconds
# - Load Scene 3
# - Wait 5 seconds
# - Load Scene 4
# - Stop capture
```

#### Task 2.3: Analyze Captured Packets
1. Open in Wireshark with filter: `udp.port == 8002`
2. For each scene load event:
   - Identify request frames (TAG + commands)
   - Identify response frames (MZO + replies)
   - Extract write operations: ADDR32 + DATA
3. Look for patterns:
   - Single write to trigger address with scene ID
   - Batch writes to multiple addresses (volumes, mutes, sources)
   - Unknown addresses not in our memory map
4. Document findings in this file

#### Task 2.4: Implement Discovered Method
If new mechanism found, update:
- `mezzo_memory_map.py`: Add new addresses
- `mezzo_client.py`: Add `load_scene_official(scene_id)` method
- `button.py`: Add option to use official vs software scenes

---

## Testing Plan

### Test Scenario 1: Software Scene Loading
1. Configure 4 scenes with distinct settings
2. Apply Scene 1 via button press
3. Verify all parameters changed correctly
4. Wait for coordinator refresh
5. Check entity states match scene config
6. Repeat for Scenes 2-4

### Test Scenario 2: Multicommand Performance
1. Apply scene with all 12 parameters changing
2. Measure total time from button press to completion
3. Verify single PBus packet sent (not 12 separate)
4. Check for any NAK responses

### Test Scenario 3: Error Handling
1. Apply scene while amplifier disconnected
2. Verify error logged and exception raised
3. Apply scene with invalid volume value (>1.0)
4. Verify validation catches error

### Test Scenario 4: State Persistence
1. Apply Scene 2
2. Restart Home Assistant
3. Verify current state still reflects Scene 2
4. Apply Scene 3 after restart
5. Verify successful application

---

## Success Criteria

### Stage 1 Success (Software Scenes)
- [ ] Scene button entities appear in HA
- [ ] Pressing scene button changes all parameters
- [ ] State updates reflect scene config within scan_interval
- [ ] No errors in logs
- [ ] Multicommand sent (not individual writes)
- [ ] User can create/modify scenes via config

### Stage 2 Success (Reverse Engineering)
- [ ] Captured View Host scene loading traffic
- [ ] Analyzed PBus packets successfully
- [ ] Documented View Host scene mechanism
- [ ] Either: Found new address/command OR confirmed it's batch writes
- [ ] If new mechanism found: Implemented and tested

---

## Rollout Plan

### Commit 1: Software Scene Foundation
- Update `const.py` with scene data structures
- Update `mezzo_client.py` with `apply_scene()` method
- Add unit tests for scene application

### Commit 2: Button Platform Rewrite
- Rewrite `button.py` to use scene configs
- Update `strings.json` for scene buttons
- Test scene loading

### Commit 3: Documentation
- Update TESTING_GUIDE.md
- Update README.md
- Add SCENE_IMPLEMENTATION_PLAN.md

### Commit 4: Scene Configuration UI (Optional)
- Add scene config to options flow
- Add scene management services
- Update translations

### Commit 5: Official Scene Method (If Discovered)
- Add new addresses to memory map
- Implement official scene loading
- Add toggle between methods
- Update documentation

---

## Timeline Estimate

| Stage | Task | Time | Status |
|-------|------|------|--------|
| 1.1 | Update data structures | 15 min | ⏳ Pending |
| 1.2 | Update client API | 30 min | ⏳ Pending |
| 1.3 | Update button platform | 30 min | ⏳ Pending |
| 1.4 | Scene configuration UI | 45 min | ⏳ Optional |
| 1.5 | Update documentation | 20 min | ⏳ Pending |
| **Stage 1 Total** | | **2h 20min** | |
| 2.1 | Setup test environment | 1 hour | ⏳ Pending |
| 2.2 | Capture traffic | 30 min | ⏳ Pending |
| 2.3 | Analyze packets | 1-2 hours | ⏳ Pending |
| 2.4 | Implement findings | 1-2 hours | ⏳ Pending |
| **Stage 2 Total** | | **3.5-5.5 hours** | |

**Minimum Viable Solution:** Stage 1 (2.5 hours)
**Complete Solution:** Stage 1 + Stage 2 (6-8 hours)

---

## Risk Assessment

### Risks - Stage 1 (Software Scenes)
- **Low:** Scene application may take multiple scan intervals to fully reflect
  - *Mitigation:* Force coordinator refresh after scene application
- **Low:** User confusion about scene vs amplifier preset terminology
  - *Mitigation:* Clear documentation and entity naming

### Risks - Stage 2 (Reverse Engineering)
- **Medium:** View Host may not use PBus for scene loading (uses HTTP to device)
  - *Mitigation:* Stage 1 already provides working solution
- **Medium:** Captured traffic may be encrypted or obfuscated
  - *Mitigation:* PBus protocol spec shows no encryption
- **Low:** Scene mechanism may be complex multi-step process
  - *Mitigation:* Document complexity, may stick with Stage 1

---

## Questions for User (If Needed)

1. Do you have View Host available for testing?
2. Do you have scenes configured in ArmoníaPlus currently?
3. What should the 4 default scenes be? (volumes, mutes, sources)
4. Would you prefer scene names editable in HA UI or fixed?
5. Should scenes control power state (standby) or just audio params?

---

## Next Steps

**Immediate Action:**
1. Get user approval for Stage 1 implementation
2. Implement software-based scenes (Tasks 1.1-1.3)
3. Test with real amplifier
4. Commit and push to GitHub

**Follow-Up:**
1. User tests scene functionality
2. If View Host available, proceed to Stage 2
3. Document any findings from reverse engineering
4. Implement official method if discovered

---

**Status:** ✅ **Plan Complete - Ready for Implementation**
**Recommended:** Begin Stage 1 immediately to unblock user

---

*Generated: October 17, 2025*
*Claude Code Implementation*
