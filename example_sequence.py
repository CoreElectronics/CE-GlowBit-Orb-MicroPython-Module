"""
example_usage.py - Complete examples showing how to use the orb extension library

These examples demonstrate various ways to use the Orb class and animation modules.
"""


from orb_extension import Orb
from orb_extension.animations import CometAnimation, FlameAnimation, step_comets
from time import sleep, ticks_ms


# ============================================================================
# Configuration - Adjust these for your hardware
# ============================================================================

# Choose your orb preset: 'pico' or 'mini'
ORB_PRESET = 'pico'  # Change to 'mini' for Mini Orb

# Preset configurations:
# - 'pico': 24-LED orb (24,12,6,1) on pin 16, brightness 20
# - 'mini': 12-LED orb (12,6,1) on pin 19, brightness 40

def create_orb():
    """Create an Orb instance using the configured preset"""
    return Orb(preset=ORB_PRESET)


# ============================================================================
# Single LED Iteration
# ============================================================================

def single_LED_cycle():
    """Cycle through each LED one at a time - basic hardware test."""
    print("\n=== Single LED Cycle ===\n")

    orb = create_orb()

    try:
        iteration = 0
        while iteration < 2:  # Run through twice
            for i in range(orb.numLEDs):
                # Clear all LEDs
                orb.pixelsFill(orb.black())

                # Light current LED
                orb.pixelSet(i, orb.red())
                orb.pixelsShow()

                print(f"  LED {i}/{orb.numLEDs-1}")
                sleep(0.2)

            iteration += 1
            print(f"\nCompleted iteration {iteration}\n")

    except KeyboardInterrupt:
        print("\n(Interrupted by user)")

    orb.clear_ornament(show=True)
    print("\nExample complete!\n")

# ============================================================================
# Basic Ring Control
# ============================================================================

def example_rings():
    """Demonstrate basic ring control."""
    print("\n=== Basic Ring Control ===\n")

    orb = create_orb()

    print(f"Orb initialized:")
    print(f"  Rings: {orb.num_rings}")
    print(f"  Total LEDs: {orb.numLEDs}\n")

    # Clear to start
    orb.clear_ornament(show=True)
    sleep(1)

    # Light each ring in sequence
    print("Lighting rings one at a time...")
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

    for ring_num in range(orb.num_rings):
        orb.clear_ornament()
        color = colors[ring_num % len(colors)]
        orb.set_ring(ring_num, color, show=True)
        print(f"  Ring {ring_num}: {len(orb.get_ring_indices(ring_num))} LEDs")
        sleep(1)

    sleep(0.5)
    orb.clear_ornament(show=True)
    sleep(0.5)

# ============================================================================
# Basic Line Control
# ============================================================================


def example_lines():
    """Demonstrate basic axes control."""
    print("\n=== Basic axes Control ===\n")
    
    orb = create_orb()

    print(f"Orb initialized:")
    print(f"  Axes: {orb.outer_count}")
    print(f"  Total LEDs: {orb.numLEDs}\n")

    # Clear to start
    orb.clear_ornament(show=True)
    sleep(1)
    
    # Light axes one at a time
    print("\nLighting axes one at a time...")
    for axis in range(min(12, orb.outer_count)):
        orb.clear_ornament()
        orb.set_axis(axis, 'cyan', show=True)
        print(f"  Axis {axis}: {len(orb.get_axis_indices(axis))} LEDs")
        sleep(0.3)

    sleep(0.5)
    orb.clear_ornament(show=True)

    print("\nExample 1 complete!\n")


# ============================================================================
#  Axes Drawing
# ============================================================================

def example_axes():
    """Demonstrate line drawing across the orb."""
    print("\n=== Axes Drawing ===\n")

    orb = create_orb()

    # Draw lines at different axes
    print("Drawing lines across the orb...")
    for i in range(4):
        axis = i * (orb.outer_count // 4)
        color = (
            (i * 80) % 256,
            (255 - i * 60) % 256,
            (i * 40) % 256
        )
        orb.set_line(axis, color, show=True)
        print(f"  Line at axis {axis}")
        sleep(0.5)

    sleep(2)

    # Draw lines with limited length
    orb.clear_ornament(show=True)
    sleep(0.5)

    print("\nDrawing partial-length lines...")
    for length in range(1, orb.num_rings + 1):
        orb.clear_ornament()
        for i in range(4):
            axis = i * (orb.outer_count // 4)
            orb.set_line(axis, 'yellow', length=length, show=False)
        orb.pixelsShow()
        print(f"  Length: {length} layers")
        sleep(0.5)

    sleep(1)
    orb.clear_ornament(show=True)

    print("\nExample complete!\n")


# ============================================================================
# Segment Fill (Half Orb)
# ============================================================================

def example_segment_fill():
    """Split orb into halves and fill with different colors."""
    print("\n=== Segment Fill (Half Orb) ===\n")

    orb = create_orb()

    print("Splitting orb into halves and filling with colors...\n")

    # Demo 1: Immediate fill
    print("Demo 1: Immediate fill at axis 0")
    above, below = orb.segment_by_axis(0, include_center=False)

    orb.clear_ornament()
    for pix in above:
        orb.pixelSet(pix, orb.rgbColour(0, 160, 255))  # Cyan
    for pix in below:
        orb.pixelSet(pix, orb.rgbColour(255, 80, 0))   # Orange
    orb.pixelsShow()

    print(f"  Above pixels: {len(above)}")
    print(f"  Below pixels: {len(below)}")
    sleep(2)

    # Demo 2: Animated fill
    print("\nDemo 2: Animated fill at axis 6")
    above, below = orb.segment_by_axis(6, include_center=False)

    orb.clear_ornament(show=True)
    sleep(0.5)

    print("  Filling above side...")
    for pix in above:
        orb.pixelSet(pix, orb.rgbColour(255, 50, 150))  # Pink
        orb.pixelsShow()
        sleep(0.02)

    print("  Filling below side...")
    for pix in below:
        orb.pixelSet(pix, orb.rgbColour(50, 255, 100))  # Green
        orb.pixelsShow()
        sleep(0.02)

    sleep(2)
    orb.clear_ornament(show=True)

    print("\nExample complete!\n")

# ============================================================================
# Built-in Animations
# ============================================================================

def example_builtin_animations():
    """Demonstrate built-in animation methods."""
    print("\n=== Built-in Animations ===\n")

    orb = create_orb()

    # Spiral in
    print("Spiral in animation...")
    orb.spiral_in((255, 0, 0), delay=0.2)
    sleep(1)

    # Spiral out
    print("Spiral out animation...")
    orb.clear_ornament(show=True)
    sleep(0.5)
    orb.spiral_out((0, 255, 0), delay=0.2)
    sleep(1)

    # Rotating axis
    print("Rotating axis for 5 seconds...")
    orb.clear_ornament(show=True)
    orb.rotate_axis((0, 0, 255), speed=0.05, duration=5)

    print("\nExample complete!\n")


# ============================================================================
# Multiple Comets
# ============================================================================

def example_comets():
    """Demonstrate comet animations."""
    print("\n=== Comet Animations ===\n")

    orb = create_orb()

    print("Creating comet animations...")

    # Create comets on different rings
    comets = [
        CometAnimation(orb, ring_number=0, colour=(0, 0, 255),
                      clockwise=True, tail_length=5, speed=0.06, start_pos=0),
        CometAnimation(orb, ring_number=0, colour=(0, 255, 128),
                      clockwise=False, tail_length=4, speed=0.09, start_pos=12),
        CometAnimation(orb, ring_number=1, colour='red',
                      clockwise=True, tail_length=3, speed=0.12, start_pos=0),
    ]

    print(f"Created {len(comets)} comets")
    print("Running for 10 seconds (Ctrl-C to stop early)...\n")

    try:
        start_time = ticks_ms()
        duration_ms = 10000

        while ticks_ms() - start_time < duration_ms:
            step_comets(orb, comets, clear=True)
            orb.pixelsShow()
            sleep(0.03)

    except KeyboardInterrupt:
        print("\n(Interrupted by user)")

    orb.clear_ornament(show=True)
    print("\nExample complete!\n")


# ============================================================================
# Flame Effect
# ============================================================================

def example_flame():
    """Demonstrate flame animation."""
    print("\n=== Flame Animation ===\n")

    orb = create_orb()

    print("Creating flame effect on axis 0...")

    flame = FlameAnimation(
        orb,
        axis=0,
        base_color=(255, 160, 64),  # Warm orange
        angular_width=2,  # Include 2 neighbors on each side
        radial_limit=None,  # Full length
        flicker_strength=0.5,
        flicker_speed=1.2
    )

    print("Running for 10 seconds (Ctrl-C to stop early)...\n")

    try:
        start_time = ticks_ms()
        duration_ms = 10000
        last_time = start_time / 1000.0

        while ticks_ms() - start_time < duration_ms:
            now = ticks_ms() / 1000.0
            dt = now - last_time

            # Get pixel colors from flame
            pixels = flame.step(dt)

            # Clear and render
            orb.clear_ornament()
            for pix, (r, g, b) in pixels.items():
                orb.pixelSet(pix, orb.rgbColour(r, g, b))
            orb.pixelsShow()

            last_time = now
            sleep(0.08)

    except KeyboardInterrupt:
        print("\n(Interrupted by user)")

    orb.clear_ornament(show=True)
    print("\nExample complete!\n")


# ============================================================================
# Rainbow Wave
# ============================================================================

def example_rainbow_wave():
    """Custom animation: rainbow wave rotating around rings."""
    print("\n=== Rainbow Wave ===\n")

    orb = create_orb()

    print("Running rainbow wave for 10 seconds...\n")

    try:
        offset = 0
        start_time = ticks_ms()
        duration_ms = 10000

        while ticks_ms() - start_time < duration_ms:
            orb.clear_ornament()

            # Draw each ring with offset colors
            for ring_num in range(orb.num_rings):
                indices = orb.get_ring_indices(ring_num)

                for i, pix in enumerate(indices):
                    # Rainbow color based on position and time
                    hue = (i * 255 // len(indices) + offset + ring_num * 30) % 255
                    color = orb.wheel(hue)
                    orb.pixelSet(pix, color)

            orb.pixelsShow()
            offset = (offset + 2) % 255
            sleep(0.03)

    except KeyboardInterrupt:
        print("\n(Interrupted by user)")

    orb.clear_ornament(show=True)
    print("\nExample complete!\n")


# ============================================================================
# Running examples
# ============================================================================


# Run all examples in sequence

# Basic functions
# single_LED_cycle()
# example_rings()
# example_lines()
# example_axes()
example_segment_fill()


# More complex functions/animations/examples
# example_builtin_animations()
# example_comets()
# example_rainbow_wave()
example_flame()

print("All examples complete!")

