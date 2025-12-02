# GlowBit Orb Extension Library

An extension to the [GlowBit library](https://github.com/CoreElectronics/CE-GlowBit-Python/tree/main) specifically designed for the Orb's spherical LED ornaments with concentric rings.

## Installation

Copy the `orb_extension` folder to your Pico alongside your main script and the `glowbit.py` library.

```
/
├── glowbit.py
├── orb_extension/
│   ├── __init__.py
│   ├── orb.py
│   └── animations.py
└── main.py
```

## Quick Start

### Basic Usage with Presets

```python
from orb_extension import Orb

# Use a preset configuration (easiest)
orb = Orb(preset='pico')   # For Pico Orb (24-LED, pin 16)
# or
orb = Orb(preset='mini')   # For Mini Orb (12-LED, pin 19)

# Light up the outer ring red
orb.set_ring(0, 'red', show=True)

# Light up an axis (radial line from outer to center)
orb.set_axis(0, (0, 255, 0), show=True)

# Draw a line across the orb (axis + opposite)
orb.set_line(6, 'blue', show=True)

# Clear the ornament
orb.clear_ornament(show=True)
```

### Custom Configuration

```python
from orb_extension import Orb

# Initialize orb with custom hardware configuration
orb = Orb(
    ring_counts=[24, 12, 6, 1],  # outer -> inner
    pin=16,
    status_leds=0,
    brightness=20
)

# Or override preset values
orb = Orb(preset='pico', brightness=50)  # Use Pico preset but brighter
```

### Available Presets

| Preset | Ring Counts | Pin | Status LEDs | Brightness | Description |
|--------|-------------|-----|-------------|------------|-------------|
| `'pico'` | [24, 12, 6, 1] | 16 | 0 | 20 | Standard Pico Orb |
| `'mini'` | [12, 6, 1] | 19 | 0 | 40 | Mini Orb |

### Animations

```python
from orb_extension import Orb
from orb_extension.animations import CometAnimation, step_comets
from time import sleep

orb = Orb(preset='pico')

# Create multiple comets
comets = [
    CometAnimation(orb, ring_number=0, colour='blue',
                   clockwise=True, tail_length=5, speed=0.06),
    CometAnimation(orb, ring_number=1, colour='red',
                   clockwise=False, tail_length=3, speed=0.12),
]

# Animation loop
while True:
    step_comets(orb, comets, clear=True)
    orb.pixelsShow()
    sleep(0.03)
```

## API Reference

### Orb Class

#### Constructor

```python
Orb(ring_counts, pin=16, status_leds=0, brightness=20, rateLimitFPS=30, sm=0)
```

**Parameters:**
- `ring_counts`: List of LED counts per ring, outer to inner (e.g., `[24, 12, 6, 1]`)
- `pin`: GPIO pin connected to LED data line
- `status_leds`: Number of status LEDs before ornament (default: 0)
- `brightness`: Initial brightness 0-255 or 0.0-1.0
- `rateLimitFPS`: Frame rate limit
- `sm`: State machine number

#### Methods

##### Indexing Methods

```python
get_axis_indices(axis, include_center=True)
```
Get pixel indices along an axis from outer to inner.

```python
get_line_indices(axis, length=None, include_opposite=True)
```
Get pixel indices for a line (axis + mirrored opposite).

```python
get_ring_indices(ring_number)
```
Get all pixel indices for a specific ring.

##### Setting Methods

```python
set_axis(axis, colour, length=None, show=False)
```
Set all pixels along an axis to a color.

```python
set_line(axis, colour, length=None, include_opposite=True, show=False)
```
Set all pixels along a line to a color.

```python
set_ring(ring_number, colour, show=False)
```
Set all pixels in a ring to a color.

```python
clear_ornament(show=False)
```
Clear all ornament LEDs (preserves status LEDs).

```python
fill_ornament(colour, show=False)
```
Fill all ornament LEDs with a color.

##### Built-in Animations

```python
spiral_in(colour, delay=0.1, start_axis=0)
```
Animation: spiral inward to center.

```python
spiral_out(colour, delay=0.1, start_axis=0)
```
Animation: spiral outward from center.

```python
rotate_axis(colour, speed=0.1, duration=None)
```
Animation: rotate a single axis around the orb.

### Animation Classes

#### CometAnimation

Creates a comet/shooting star that moves around a ring with a trailing tail.

```python
CometAnimation(orb, ring_number, colour, clockwise=True,
               tail_length=4, speed=0.07, start_pos=0, easing=True)
```

**Methods:**
- `step()`: Update position (call every frame)
- `render(accum)`: Render to accumulation buffer

#### FlameAnimation

Creates a realistic flickering flame effect along an axis.

```python
FlameAnimation(orb, axis, base_color=(255, 160, 64),
               angular_width=1, radial_limit=None,
               flicker_strength=0.45, flicker_speed=1.0,
               gust_mean=4.0, gust_mag_max=0.9, gust_smooth=0.6)
```

**Methods:**
- `step(dt)`: Update flame state, returns dict of pixel colors

#### Helper Functions

```python
step_comets(orb, comets, clear=True)
```
Step and render multiple comet animations in one call.

### Color Formats

The Orb class accepts colors in multiple formats:

- **RGB tuple**: `(255, 0, 0)` for red
- **Color names**: `'red'`, `'green'`, `'blue'`, `'yellow'`, `'purple'`, `'cyan'`, `'white'`, `'black'`
- **GlowBit objects**: `orb.red()`, `orb.rgbColour(255, 128, 0)`
