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

# Or use custom configuration (set ORB_PRESET = None):
# ORB_PRESET = None
# ORB_CUSTOM = {
#     'ring_counts': [24, 12, 6, 1],
#     'pin': 16,
#     'status_leds': 0,
#     'brightness': 20
# }

ORB_CUSTOM = None  # Only used if ORB_PRESET is None


# ============================================================================
# Helper function to create Orb instance
# ============================================================================

def create_orb():
    """Create an Orb instance using the configured preset or custom settings."""
    if ORB_PRESET is not None:
        print("USING PRESET: ", ORB_PRESET)
        return Orb(preset=ORB_PRESET)
    elif ORB_CUSTOM is not None:
        return Orb(**ORB_CUSTOM)
    else:
        raise ValueError("Either ORB_PRESET or ORB_CUSTOM must be configured")


# ============================================================================
# Example 1: Basic Ring and Axis Control
# ============================================================================

def example_1_basics():
    """Demonstrate basic ring and axis control."""
    print("\n=== Example 1: Basic Ring and Axis Control ===\n")

    orb = create_orb()

    print(f"Orb initialized:")
    print(f"  Rings: {orb.num_rings}")
    print(f"  Axes: {orb.outer_count}")
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
# Example 2: Line Drawing
# ============================================================================

def example_2_lines():
    """Demonstrate line drawing across the orb."""
    print("\n=== Example 2: Line Drawing ===\n")

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

    print("\nExample 2 complete!\n")


# ============================================================================
# Example 3: Built-in Animations
# ============================================================================

def example_3_builtin_animations():
    """Demonstrate built-in animation methods."""
    print("\n=== Example 3: Built-in Animations ===\n")

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

    print("\nExample 3 complete!\n")


# ============================================================================
# Example 4: Multiple Comets
# ============================================================================

def example_4_comets():
    """Demonstrate comet animations."""
    print("\n=== Example 4: Comet Animations ===\n")

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
    print("\nExample 4 complete!\n")


# ============================================================================
# Example 5: Flame Effect
# ============================================================================

def example_5_flame():
    """Demonstrate flame animation."""
    print("\n=== Example 5: Flame Animation ===\n")

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
    print("\nExample 5 complete!\n")


# ============================================================================
# Example 6: Rainbow Wave
# ============================================================================

def example_6_rainbow_wave():
    """Custom animation: rainbow wave rotating around rings."""
    print("\n=== Example 6: Rainbow Wave ===\n")

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
    print("\nExample 6 complete!\n")


# ============================================================================
# Example 7: Single LED Iteration
# ============================================================================

def example_7_single_led_iteration():
    """Iterate through each LED one at a time - basic hardware test."""
    print("\n=== Example 7: Single LED Iteration ===\n")

    orb = create_orb()

    print(f"Lighting each of {orb.numLEDs} LEDs individually...")
    print("(Ctrl-C to stop)\n")

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
    print("\nExample 7 complete!\n")


# ============================================================================
# Example 8: Segment Fill (Half Orb)
# ============================================================================

def example_8_segment_fill():
    """Split orb into halves and fill with different colors."""
    print("\n=== Example 8: Segment Fill (Half Orb) ===\n")

    orb = create_orb()

    def segment_by_axis(axis, include_center=False):
        """
        Split orb into two halves around the given axis.
        Returns (above_indices, below_indices).
        The axis line and its opposite are excluded.
        """
        if orb.outer_count <= 1:
            return ([], [])

        k = axis % orb.outer_count
        k_op = (k + orb.outer_count // 2) % orb.outer_count

        # Get all axis columns
        all_columns = {}
        for j in range(orb.outer_count):
            cols = orb.get_axis_indices(j, include_center=include_center)
            all_columns[j] = cols

        # Exclude the splitting axis and its opposite
        all_columns[k] = []
        all_columns[k_op] = []

        # Collect "above" (clockwise from axis)
        above = []
        seen = set()
        j = (k + 1) % orb.outer_count
        while j != k_op:
            for pix in all_columns.get(j, []):
                if pix not in seen:
                    above.append(pix)
                    seen.add(pix)
            j = (j + 1) % orb.outer_count

        # Collect "below" (counter-clockwise from axis)
        below = []
        seen2 = set()
        j = (k - 1) % orb.outer_count
        while j != k_op:
            for pix in all_columns.get(j, []):
                if pix not in seen2:
                    below.append(pix)
                    seen2.add(pix)
            j = (j - 1) % orb.outer_count

        return above, below

    print("Splitting orb into halves and filling with colors...\n")

    # Demo 1: Immediate fill
    print("Demo 1: Immediate fill at axis 0")
    above, below = segment_by_axis(0, include_center=False)

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
    above, below = segment_by_axis(6, include_center=False)

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

    print("\nExample 8 complete!\n")


# ============================================================================
# Main Menu
# ============================================================================

def main():
    """Run interactive example menu."""
    print("\n" + "="*60)
    print("GlowBit Orb Extension Library - Examples")
    print("="*60)

    examples = [
        ("Basic Ring and Axis Control", example_1_basics),
        ("Line Drawing", example_2_lines),
        ("Built-in Animations", example_3_builtin_animations),
        ("Multiple Comets", example_4_comets),
        ("Flame Effect", example_5_flame),
        ("Rainbow Wave", example_6_rainbow_wave),
        ("Single LED Iteration", example_7_single_led_iteration),
        ("Segment Fill (Half Orb)", example_8_segment_fill),
    ]

    while True:
        print("\nSelect an example to run:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print("  0. Exit")

        try:
            choice = input("\nEnter choice (0-8): ").strip()
            choice = int(choice)

            if choice == 0:
                print("\nGoodbye!")
                break
            elif 1 <= choice <= len(examples):
                examples[choice - 1][1]()
            else:
                print("Invalid choice. Please try again.")

        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    # Run all examples in sequence
    # Uncomment to run the interactive menu instead:
    # main()

    example_1_basics()
    example_2_lines()
    example_3_builtin_animations()
    example_4_comets()
    example_5_flame()
    example_6_rainbow_wave()
    example_7_single_led_iteration()
    example_8_segment_fill()

    print("\n" + "="*60)
    print("All examples complete!")
    print("="*60 + "\n")
