# GlassCutting Pro - Chrome Extension

Lisec GFB-60/30RE glass cutting machine control extension. Browser-based G-code editor, cutting parameters, simulation and machine monitoring.

## ⚡ Quick Install (2 minutes)

### Step 1: Open Chrome Extensions

```
1. Open Google Chrome
2. Go to: chrome://extensions/
```

### Step 2: Enable Developer Mode

```
- Toggle "Developer mode" switch (top right corner)
- It turns blue when enabled
```

### Step 3: Load Extension

```
1. Click "Load unpacked" button
2. Navigate to: AI/GlassCuttingProgram/web/
3. Select the folder and click "Select Folder"
```

### Step 4: Use Extension

```
- Click the puzzle icon (Extensions) in Chrome toolbar
- Pin "GlassCutting Pro" to toolbar
- Click the icon to open
```

---

## Features

### 📝 G-Code Editor

- Full-featured text editor
- Line numbers
- Load/Save files
- Sample G-code included
- Character and line counter

### ⚙️ Cutting Parameters

- Glass properties (width, height, thickness, type)
- Cutting settings (speed, pressure, angle)
- Axis settings (X/Y/Z max speed)
- E-Cam for laminated glass
- Preset save/load

### 🎯 Simulation

- Real-time 2D visualization
- Cutting path animation
- Position tracking
- Speed control (1x-10x)
- Pause/Resume/Reset

### 🖥️ Machine Status

- 5-axis servo monitoring
- I/O LED indicators
- Alarm list
- Connection status

---

## Usage

### Load G-Code

1. Click extension icon
2. Go to G-Code tab
3. Click "📂 Load" button
4. Select your .nc, .gcode, or .txt file

### Set Parameters

1. Go to Parameters tab
2. Configure glass and cutting settings
3. Click "✓ Apply"

### Run Simulation

1. Go to Simulation tab
2. Click "▶ Start"
3. Adjust speed with slider

### Connect to Machine

1. Go to Machine tab
2. Click "🔌 Connect"
3. Monitor servo positions

---

## File Structure

```
web/
├── manifest.json         # Extension manifest (v3)
├── app.html              # Main UI
├── app.css               # Styles
├── app.js                # Application logic
├── app.background.js     # Service worker
├── test.html             # Test page
└── icons/
    ├── icon16.png
    ├── icon48.png
    ├── icon128.png
    └── icon256.png
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Click icon | Open extension |
| Ctrl+Click | Open in new tab |

---

## Supported G-Codes

| Code | Description |
|------|-------------|
| G0 | Rapid positioning |
| G1 | Linear cutting |
| G21 | Metric units |
| G90 | Absolute positioning |
| G91 | Relative positioning |
| M30 | Program end |

---

## Troubleshooting

### Extension not showing

- Make sure Developer mode is enabled
- Reload from chrome://extensions/
- Restart Chrome

### Can't load files

- Grant permissions when prompted
- Use supported file extensions

### Simulation not working

- Check G-code format
- Try sample G-code first

---

## Version

**2.0.0** - Chrome Extension (April 2026)

---

**CNC Revizyon Team**
