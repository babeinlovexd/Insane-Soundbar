# Implement Internal Profiles and Clipboard Backup

Replace the failing `FilePicker` with a robust internal profile system and clipboard-based export/import.

## Proposed Changes

### main.py

- Add `favorite_profiles` dictionary.
- Load `iss_profiles` from `SharedPreferences` at startup.
- Add UI to the DSP tab:
    - Dropdown to select a profile.
    - Button to "Save Current Settings" to a profile.
    - Button to "Restore Selected Profile".
    - Buttons to Export/Import settings via Clipboard (JSON text).
- Remove all `FilePicker` references.

#### [main.py](file:///C:/Users/chris/OneDrive/Dokumente/Insane-Soundbar/Insane Control Center/Android/src/main.py)

```python
async def save_profile(_e):
    # Collect current slider values
    # Save to favorite_profiles
    # Update storage
```

## Verification Plan

### Automated Tests
- Run `analyze_file` again to confirm the reduction in warnings.

### Manual Verification
- Visual inspection of the code to ensure logic remains unchanged.
