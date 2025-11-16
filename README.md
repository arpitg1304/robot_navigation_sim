# Reactive Navigation Simulator - Modern UI Edition

A modern Python-based robot navigation simulator with a **beautiful, polished UI** and **pluggable algorithm system**. Write and test your own navigation algorithms!

## ✨ Modern UI Features

- 🎨 **Dark mode theme** with professional color palette
- 📱 **Dropdown menu** for easy algorithm selection
- ✨ **Visual effects**: glowing target, gradient paths, shadows
- 🎯 **Smooth animations** running at 60 FPS
- 💎 **Polished interface** with rounded corners and hover effects

## Features

- 🎮 **Interactive GUI** with real-time visualization
- 🔌 **Pluggable algorithm system** - easily write and test custom navigation algorithms
- 🎯 **5 built-in algorithms**:
  - Reactive Navigation (random & target-centric)
  - Simple Target Seeking
  - Wall Following (right-hand rule)
  - Potential Field Navigation
- 📊 **Visual feedback** with color-coded sonar, path tracking, and live stats
- 🗺️ **Custom environments** with obstacles and targets
- 💾 **Path recording** and analysis

## Quick Start

### Installation

```bash
# Install dependencies
pip install pygame numpy

# Run the simulator
python -m src.main
```

### Controls

- **Start/Stop**: Click button or press `SPACE`
- **Algorithm Dropdown**: Select from all available algorithms
- **Manual Control**: Use arrow keys
- **Sonar/Tracking**: Toggle buttons to control features
- **Reset**: Reset robot to starting position
- **Quit**: Click button or press `ESC`

## Screenshots
![Navigation Simulator](screenshots/navigation_sim.png "Navigation Simulatort")

![Map Editor](screenshots/map_editor.png "Map editor")



**Dark Mode UI:**
- Clean, modern interface
- Algorithm dropdown for easy selection
- Live status indicators
- Glowing target with pulse animation
- Color-coded sonar (green = clear, red = blocked)

## Writing Custom Algorithms

See **[ALGORITHM_GUIDE.md](ALGORITHM_GUIDE.md)** for comprehensive documentation!

### Quick Example

```python
from src.algorithms.base import NavigationAlgorithm
import math

class MyAlgorithm(NavigationAlgorithm):
    def get_name(self):
        return "My Custom Algorithm"

    def compute_direction(self, robot_x, robot_y, robot_radius,
                         robot_heading, environment, sonar):
        # Move toward target
        dx = environment.target.x - robot_x
        dy = environment.target.y - robot_y
        angle = math.degrees(math.atan2(dy, dx))
        return round(angle / 45) * 45 % 360
```

Add to `src/main.py` and it appears in the dropdown!

## Project Structure

```
reactive-nav-sim-modern/
├── src/
│   ├── algorithms/          # Built-in algorithms
│   │   ├── base.py         # Base class
│   │   ├── reactive.py     # Reactive navigation
│   │   ├── simple_target.py
│   │   ├── wall_follower.py
│   │   └── potential_field.py
│   ├── ui_components.py     # Modern UI components
│   ├── modern_renderer.py   # Modern renderer with effects
│   ├── main.py              # Entry point
│   ├── robot.py             # Robot class
│   ├── environment.py       # Environment & obstacles
│   ├── sonar.py             # Sonar sensor
│   └── config.py            # Configuration & colors
├── user_algorithms/         # Your custom algorithms go here!
│   └── template.py          # Template for new algorithms
├── ALGORITHM_GUIDE.md       # Complete guide for algorithms
├── MODERN_UI_GUIDE.md       # UI customization guide
├── QUICK_START.md           # Quick reference
└── README.md                # This file
```

## Documentation

- **[ALGORITHM_GUIDE.md](ALGORITHM_GUIDE.md)** - Complete guide for writing custom algorithms
- **[MODERN_UI_GUIDE.md](MODERN_UI_GUIDE.md)** - UI features and customization
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide

## Modern UI Highlights

### Dark Theme
Professional dark mode with carefully chosen colors for readability and aesthetics.

### Algorithm Dropdown
No more cycling! Click the dropdown to see all algorithms and select directly.

### Visual Effects
- **Pulsing target** with animated glow
- **Gradient path trace** that fades over time  
- **Shadows** on robot and obstacles for depth
- **Color-coded sonar** (green=clear, red=blocked)
- **Smooth animations** at 60 FPS

### Status Indicators
Live status with colored dots:
- 🟢 Running
- 🔵 Sonar enabled
- 🟣 Tracking enabled

### Stat Cards
Modern cards showing:
- Current position (x, y)
- Robot heading (degrees)

## Customization

Edit `src/config.py` to change colors:

```python
# Change robot color to red
COLOR_ROBOT = (255, 0, 0)

# Adjust UI background
COLOR_UI_BG = (30, 30, 35)
```

See [MODERN_UI_GUIDE.md](MODERN_UI_GUIDE.md) for full customization options.

## Contributing

Contributions welcome! If you create an interesting algorithm:

1. Add it to `src/algorithms/`
2. Update documentation
3. Submit a pull request

## License

MIT License - feel free to use and modify!

## Credits

Modernized with:
- Dark mode UI with professional design
- Dropdown algorithm selector
- Visual effects and animations
- Plugin architecture for custom algorithms
- Comprehensive documentation

Happy navigating! 🤖✨
