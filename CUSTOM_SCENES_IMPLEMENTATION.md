# Custom Scenes Implementation Plan

## Overview

This document describes the implementation of custom, user-editable scenes for the Powersoft Mezzo Home Assistant integration.

## Requirements

- Create custom scenes from HA UI
- Edit existing scenes
- Delete scenes
- Include full EQ settings (4 bands × 4 channels)
- Persist across HA restarts
- User-friendly service-based workflow

## Architecture

```
┌─────────────────────────────────────────────┐
│          Scene Storage (JSON file)          │
│     .storage/powersoft_mezzo_scenes.json    │
└─────────────────────────────────────────────┘
                    ↑↓
┌─────────────────────────────────────────────┐
│           SceneManager Class                │
│  - Load/save scenes from storage            │
│  - Validate scene data                      │
│  - Manage scene IDs                         │
└─────────────────────────────────────────────┘
                    ↑↓
┌──────────────────┬──────────────────────────┐
│   Services       │   Button Entities        │
│                  │                          │
│ • save_scene     │  Dynamically created     │
│ • update_scene   │  from stored scenes      │
│ • delete_scene   │                          │
│ • capture_state  │  Refresh on scene change │
└──────────────────┴──────────────────────────┘
```

## Services

### 1. `powersoft_mezzo.save_scene`
**Purpose**: Save current amplifier state as a new scene

**Parameters**:
- `name` (required): Scene name
- `scene_id` (optional): Specific ID to use (for overwriting)

**Action**: Reads current amp state (volumes, mutes, sources, EQ) and saves to storage

**Example**:
```yaml
service: powersoft_mezzo.save_scene
data:
  name: "Evening Listening"
```

### 2. `powersoft_mezzo.update_scene`
**Purpose**: Update existing scene with current amp state

**Parameters**:
- `scene_id` (required): Which scene to update

**Action**: Overwrites scene with current amplifier settings

**Example**:
```yaml
service: powersoft_mezzo.update_scene
data:
  scene_id: 5
```

### 3. `powersoft_mezzo.delete_scene`
**Purpose**: Delete a scene

**Parameters**:
- `scene_id` (required): Scene to delete

**Action**: Removes scene from storage, removes button entity

**Example**:
```yaml
service: powersoft_mezzo.delete_scene
data:
  scene_id: 5
```

### 4. `powersoft_mezzo.capture_eq` (helper)
**Purpose**: Read and display current EQ settings from amplifier

**Returns**: Current EQ configuration for all channels (logged)

**Use**: For debugging/viewing current EQ state

## Storage Format

**Location**: `.storage/powersoft_mezzo_scenes_{entry_id}.json`

**Format**:
```json
{
  "version": 1,
  "scenes": [
    {
      "id": 0,
      "name": "Evening Listening",
      "volumes": [0.6, 0.6, 0.5, 0.5],
      "mutes": [false, false, false, false],
      "sources": [1, 1, 2, 2],
      "standby": false,
      "eq": [
        [
          {"enabled": 1, "type": 11, "q": 0.707, "frequency": 80, "gain": 1.4, "slope": 1.0},
          {"enabled": 0, "type": 0, "q": 1.0, "frequency": 1000, "gain": 1.0, "slope": 1.0},
          {"enabled": 0, "type": 0, "q": 1.0, "frequency": 5000, "gain": 1.0, "slope": 1.0},
          {"enabled": 0, "type": 0, "q": 1.0, "frequency": 10000, "gain": 1.0, "slope": 1.0}
        ],
        [],
        [],
        []
      ],
      "created_at": "2025-10-17T18:30:00Z",
      "updated_at": "2025-10-17T18:30:00Z"
    }
  ]
}
```

## Implementation Phases

### Phase 1: Scene Storage & Manager
**Files**: `scene_manager.py`, `mezzo_client.py`

1. Create `SceneManager` class:
   - Load/save JSON from HA storage
   - CRUD operations for scenes
   - Scene ID auto-increment
   - Validation

2. Add EQ reading to `MezzoClient`:
   - `get_eq_band(channel, band)` - Read single EQ band
   - `get_all_eq()` - Read all EQ settings (bulk read)
   - `capture_current_state()` - Get complete amp state including EQ

### Phase 2: Service Registration
**Files**: `services.yaml`, `__init__.py`

3. Create `services.yaml` - Define service schemas with validation
4. Update `__init__.py`:
   - Initialize SceneManager
   - Register services
   - Connect service calls to SceneManager methods

### Phase 3: Dynamic Button Platform
**Files**: `button.py`

5. Update `button.py`:
   - Load scenes from SceneManager instead of const.py
   - Add async_add_entities support for dynamic entity creation
   - Listen for scene changes and update entities

### Phase 4: Testing & Polish

6. Test workflow:
   - Create scene via service
   - Verify button appears
   - Update scene
   - Delete scene
   - Verify persistence across restart
   - Test error handling

## User Workflow

### Creating a Scene

1. Set amplifier to desired state using HA controls
2. (Optional) Use Armonía/View Host to configure EQ
3. Go to Developer Tools > Services
4. Call `powersoft_mezzo.save_scene`:
   ```yaml
   service: powersoft_mezzo.save_scene
   data:
     name: "My Party Scene"
   ```
5. New button appears automatically

### Updating a Scene

1. Adjust amplifier settings to new desired state
2. Call `powersoft_mezzo.update_scene`:
   ```yaml
   service: powersoft_mezzo.update_scene
   data:
     scene_id: 5
   ```
3. Scene updated with new settings

### Deleting a Scene

1. Call `powersoft_mezzo.delete_scene`:
   ```yaml
   service: powersoft_mezzo.delete_scene
   data:
     scene_id: 5
   ```
2. Button removed automatically

## Future Enhancements

### Phase 5: EQ Control Entities
- Add `number` entities for each EQ parameter
- Add `select` entities for filter types
- Allow visual EQ editing from HA UI

### Phase 6: Scene Editor UI
- Config flow for scene editing
- Visual EQ curve display
- Drag-and-drop scene reordering

### Phase 7: Advanced Features
- Copy scene service
- Export/import scenes to/from YAML/JSON
- Scene scheduling
- Scene transitions (gradual volume changes)

## Technical Considerations

### EQ Reading Implementation

The amplifier stores EQ as BiQuad filters (24 bytes each):
```
+0x00: Enabled (uint32, 4 bytes)
+0x04: Type (uint32, 4 bytes)
+0x08: Q (float, 4 bytes)
+0x0C: Slope (float, 4 bytes)
+0x10: Frequency (uint32, 4 bytes)
+0x14: Gain (float, 4 bytes)
```

Reading all EQ requires:
- 4 channels × 4 bands = 16 read commands
- 16 × 24 bytes = 384 bytes total
- Can be done in single multicommand request

### Storage Location

Use HA's built-in storage API:
- `hass.helpers.storage.Store`
- Automatic backup/versioning
- JSON validation
- Atomic writes

### Button Entity Updates

When scenes change:
1. Use `async_dispatcher_send()` to notify button platform
2. Button platform calls `async_add_entities()` with new entities
3. Old entities automatically removed if not in new list

## Estimated Implementation Time

- Phase 1: 45 minutes
- Phase 2: 30 minutes
- Phase 3: 30 minutes
- Phase 4: 30-60 minutes

**Total**: 2-3 hours

## Notes

- Default scenes from `const.py` are merged with custom scenes
- Scene IDs 0-3 reserved for defaults (read-only)
- Custom scenes start at ID 100
- Scene buttons show creation/update timestamps as attributes
