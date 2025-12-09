"""
orb.py - GlowBit extension library for spherical LED ornaments

This module extends the glowbit.stick class with orb-specific functionality,
including ring mapping, axis-based addressing, and common animation helpers.

Usage:
    from orb import Orb

    # Initialize with preset configuration
    orb = Orb(preset='pico')  # or preset='mini'

    # Or initialize with custom configuration
    orb = Orb(
        ring_counts=[24, 12, 6, 1],  # outer -> inner
        pin=16,
        status_leds=0,
        brightness=20
    )

    # Use orb-specific methods
    orb.set_axis(axis=0, colour=(255, 0, 0))
    orb.clear_ornament()
    orb.pixelsShow()
"""

import glowbit
from time import sleep

# Hardware presets
ORB_PRESETS = {
    'pico': {
        'ring_counts': [24, 12, 6, 1],
        'pin': 16,
        'status_leds': 0,
        'brightness': 20
    },
    'mini': {
        'ring_counts': [12, 6, 1],
        'pin': 19,
        'status_leds': 0,
        'brightness': 40
    }
}


class Orb(glowbit.stick):
    """
    Extension of glowbit.stick with orb-specific functionality.

    An orb is a spherical arrangement of concentric LED rings where:
    - The outer ring defines "axes" (radial lines toward center)
    - Inner rings have progressively fewer LEDs
    - The center is typically a single LED
    """

    def __init__(self, ring_counts=None, pin=None, status_leds=None, brightness=None,
                 rateLimitFPS=30, sm=0, preset=None):
        """
        Initialize an Orb.

        Args:
            preset: Optional preset configuration ('pico' or 'mini').
                    If provided, overrides default values for ring_counts, pin, status_leds, and brightness.
                    Individual parameters can still override preset values.
            ring_counts: List of LED counts per ring, outer to inner (e.g., [24, 12, 6, 1])
            pin: GPIO pin connected to LED data line
            status_leds: Number of status LEDs before ornament (default: 0)
            brightness: Initial brightness 0-255 or 0.0-1.0
            rateLimitFPS: Frame rate limit
            sm: State machine number (Pico only)

        Examples:
            # Using preset
            orb = Orb(preset='pico')
            orb = Orb(preset='mini')

            # Using preset with custom brightness
            orb = Orb(preset='pico', brightness=50)

            # Custom configuration
            orb = Orb(ring_counts=[24, 12, 6, 1], pin=16)
        """
        # Apply preset if specified
        if preset is not None:
            if preset not in ORB_PRESETS:
                raise ValueError(f"Unknown preset '{preset}'. Available presets: {list(ORB_PRESETS.keys())}")

            preset_config = ORB_PRESETS[preset]
            # Use preset values as defaults, but allow parameter overrides
            if ring_counts is None:
                ring_counts = preset_config['ring_counts']
            if pin is None:
                pin = preset_config['pin']
            if status_leds is None:
                status_leds = preset_config['status_leds']
            if brightness is None:
                brightness = preset_config['brightness']

        # Set defaults for any remaining None values
        if ring_counts is None:
            raise ValueError("ring_counts must be specified either via preset or directly")
        if pin is None:
            pin = 16
        if status_leds is None:
            status_leds = 0
        if brightness is None:
            brightness = 20

        self.ring_counts = list(ring_counts)
        self.status_leds = status_leds
        total_leds = status_leds + sum(ring_counts)

        # Initialize parent stick class
        super().__init__(numLEDs=total_leds, pin=pin, brightness=brightness,
                        rateLimitFPS=rateLimitFPS, sm=sm)

        # Build ring map
        self.ring_map = self._build_ring_map()
        self.outer_count = self.ring_counts[0] if self.ring_counts else 0
        self.num_rings = len(self.ring_counts)

        # Precompute axis columns for fast lookup
        self._axis_cache = {}
        self._build_axis_cache()

    def _build_ring_map(self):
        """Build ring map structure: [{'start': idx, 'length': n}, ...]"""
        rings = []
        start = self.status_leds
        for count in self.ring_counts:
            rings.append({'start': start, 'length': count})
            start += count
        return rings

    def _build_axis_cache(self):
        """Precompute pixel indices for each axis."""
        if self.outer_count <= 0:
            return

        for axis in range(self.outer_count):
            self._axis_cache[axis] = self._compute_axis_indices(axis)

    def _compute_axis_indices(self, axis, include_center=True):
        """
        Compute pixel indices along an axis from outer to inner.

        Args:
            axis: Axis index (0 to outer_count-1)
            include_center: Include center LED if present

        Returns:
            List of absolute pixel indices (outer -> inner order)
        """
        if self.outer_count <= 0:
            return []

        k = int(axis) % self.outer_count
        indices = []

        for ring_id, ring in enumerate(self.ring_map):
            count = ring['length']
            start = ring['start']

            if count == 1:
                # Center pixel - matches all axes
                if include_center:
                    indices.append(start)
                continue

            # Check if this axis has an LED on this ring
            numerator = k * count
            if numerator % self.outer_count == 0:
                local_idx = (numerator // self.outer_count) % count
                indices.append(start + local_idx)

        return indices

    def get_axis_indices(self, axis, include_center=True):
        """
        Get precomputed pixel indices for an axis.

        Args:
            axis: Axis index (0 to outer_count-1)
            include_center: Include center LED if present

        Returns:
            List of absolute pixel indices (outer -> inner)
        """
        axis = int(axis) % self.outer_count

        if not include_center:
            # Filter out center from cached result
            cached = self._axis_cache.get(axis, [])
            if cached and self.ring_counts[-1] == 1:
                return cached[:-1]  # Remove last element (center)
            return cached

        return self._axis_cache.get(axis, [])

    def get_line_indices(self, axis, length=None, include_opposite=True):
        """
        Get pixel indices for a line across the orb.

        A line consists of:
        - Forward axis (outer -> inner)
        - Optionally, opposite axis mirrored (inner -> outer)

        Args:
            axis: Starting axis index
            length: Maximum number of layers (None = all)
            include_opposite: Include mirrored opposite axis

        Returns:
            List of absolute pixel indices
        """
        forward = self.get_axis_indices(axis)

        if length is not None:
            forward = forward[:int(length)]

        if not include_opposite or self.outer_count % 2 != 0:
            return forward

        # Compute opposite axis
        opposite_axis = (axis + self.outer_count // 2) % self.outer_count
        opposite = self.get_axis_indices(opposite_axis)

        # Reverse to create inner->outer order for second half
        opposite_rev = list(reversed(opposite))

        # Remove duplicate center pixel if present
        if forward and opposite_rev and forward[-1] == opposite_rev[0]:
            opposite_rev = opposite_rev[1:]

        if length is not None:
            remaining = int(length) - len(forward)
            if remaining > 0:
                opposite_rev = opposite_rev[:remaining]
            else:
                opposite_rev = []

        return forward + opposite_rev

    def get_ring_indices(self, ring_number):
        """
        Get all pixel indices for a specific ring.

        Args:
            ring_number: Ring index (0 = outermost)

        Returns:
            List of absolute pixel indices
        """
        if ring_number < 0 or ring_number >= self.num_rings:
            return []

        ring = self.ring_map[ring_number]
        return list(range(ring['start'], ring['start'] + ring['length']))

    def set_axis(self, axis, colour, length=None, show=False):
        """
        Set all pixels along an axis to a color.

        Args:
            axis: Axis index
            colour: Color as (r,g,b) tuple, string, or glowbit color
            length: Maximum layers to light (None = all)
            show: Call pixelsShow() after setting

        Returns:
            List of pixel indices that were set
        """
        indices = self.get_axis_indices(axis)

        if length is not None:
            indices = indices[:int(length)]

        col = self._color_to_obj(colour)

        for idx in indices:
            self.pixelSet(idx, col)

        if show:
            self.pixelsShow()

        return indices

    def set_line(self, axis, colour, length=None, include_opposite=True, show=False):
        """
        Set all pixels along a line (axis + opposite) to a color.

        Args:
            axis: Starting axis index
            colour: Color as (r,g,b) tuple, string, or glowbit color
            length: Maximum layers total (None = all)
            include_opposite: Include mirrored opposite axis
            show: Call pixelsShow() after setting

        Returns:
            List of pixel indices that were set
        """
        indices = self.get_line_indices(axis, length, include_opposite)
        col = self._color_to_obj(colour)

        for idx in indices:
            self.pixelSet(idx, col)

        if show:
            self.pixelsShow()

        return indices

    def set_ring(self, ring_number, colour, show=False):
        """
        Set all pixels in a ring to a color.

        Args:
            ring_number: Ring index (0 = outermost)
            colour: Color as (r,g,b) tuple, string, or glowbit color
            show: Call pixelsShow() after setting

        Returns:
            List of pixel indices that were set
        """
        indices = self.get_ring_indices(ring_number)
        col = self._color_to_obj(colour)

        for idx in indices:
            self.pixelSet(idx, col)

        if show:
            self.pixelsShow()

        return indices

    def clear_ornament(self, show=False):
        """
        Clear all ornament LEDs (preserve status LEDs).

        Args:
            show: Call pixelsShow() after clearing
        """
        if not self.ring_map:
            return

        ornament_start = self.ring_map[0]['start']
        ornament_total = sum([r['length'] for r in self.ring_map])

        for i in range(ornament_start, ornament_start + ornament_total):
            self.pixelSet(i, self.black())

        if show:
            self.pixelsShow()

    def fill_ornament(self, colour, show=False):
        """
        Fill all ornament LEDs with a color (preserve status LEDs).

        Args:
            colour: Color as (r,g,b) tuple, string, or glowbit color
            show: Call pixelsShow() after filling
        """
        if not self.ring_map:
            return

        col = self._color_to_obj(colour)
        ornament_start = self.ring_map[0]['start']
        ornament_total = sum([r['length'] for r in self.ring_map])

        for i in range(ornament_start, ornament_start + ornament_total):
            self.pixelSet(i, col)

        if show:
            self.pixelsShow()

    def _color_to_obj(self, colour):
        """
        Convert various color formats to glowbit color object.

        Args:
            colour: (r,g,b) tuple, color name string, or glowbit color

        Returns:
            Glowbit color object suitable for pixelSet()
        """
        # Handle tuple/list RGB
        if isinstance(colour, (tuple, list)) and len(colour) == 3:
            return self.rgbColour(int(colour[0]), int(colour[1]), int(colour[2]))

        # Handle string color names
        if isinstance(colour, str):
            name = colour.strip().lower()
            color_map = {
                'red': self.red(),
                'green': self.green(),
                'blue': self.blue(),
                'yellow': self.yellow(),
                'purple': self.purple(),
                'cyan': self.cyan(),
                'white': self.white(),
                'black': self.black(),
            }
            if name in color_map:
                return color_map[name]

        # Assume it's already a glowbit color object
        return colour

    def spiral_out(self, colour, delay=0.1, start_axis=0):
        """
        Animation: spiral outward from center.

        Args:
            colour: Color to use
            delay: Delay between steps (seconds)
            start_axis: Starting axis index
        """
        # Light up rings from inner to outer
        for ring_num in range(self.num_rings - 1, -1, -1):
            self.set_ring(ring_num, colour, show=True)
            sleep(delay)

    def spiral_in(self, colour, delay=0.1, start_axis=0):
        """
        Animation: spiral inward to center.

        Args:
            colour: Color to use
            delay: Delay between steps (seconds)
            start_axis: Starting axis index
        """
        # Light up rings from outer to inner
        for ring_num in range(self.num_rings):
            self.set_ring(ring_num, colour, show=True)
            sleep(delay)

    def rotate_axis(self, colour, speed=0.1, duration=None):
        """
        Animation: rotate a single axis around the orb.

        Args:
            colour: Color to use
            speed: Delay between steps (seconds)
            duration: Total duration (None = infinite)
        """
        import time
        start_time = time.time()

        try:
            axis = 0
            while True:
                if duration is not None and (time.time() - start_time) >= duration:
                    break

                self.clear_ornament()
                self.set_axis(axis, colour)
                self.pixelsShow()

                axis = (axis + 1) % self.outer_count
                sleep(speed)

        except KeyboardInterrupt:
            pass
        finally:
            self.clear_ornament(show=True)

    def segment_by_axis(self, axis, include_center=False):
        """
        Split orb into two halves around the given axis.
        Returns (above_indices, below_indices).
        The axis line and its opposite are excluded.
        """
        if self.outer_count <= 1:
            return ([], [])

        k = axis % self.outer_count
        k_op = (k + self.outer_count // 2) % self.outer_count

        # Get all axis columns
        all_columns = {}
        for j in range(self.outer_count):
            cols = self.get_axis_indices(j, include_center=include_center)
            all_columns[j] = cols

        # Exclude the splitting axis and its opposite
        all_columns[k] = []
        all_columns[k_op] = []

        # Collect "above" (clockwise from axis)
        above = []
        seen = set()
        j = (k + 1) % self.outer_count
        while j != k_op:
            for pix in all_columns.get(j, []):
                if pix not in seen:
                    above.append(pix)
                    seen.add(pix)
            j = (j + 1) % self.outer_count

        # Collect "below" (counter-clockwise from axis)
        below = []
        seen2 = set()
        j = (k - 1) % self.outer_count
        while j != k_op:
            for pix in all_columns.get(j, []):
                if pix not in seen2:
                    below.append(pix)
                    seen2.add(pix)
            j = (j - 1) % self.outer_count

        return below, above


def example_basic():
    """Basic example showing orb functionality."""
    print("=== Orb Extension Basic Example ===")

    # Create orb instance
    orb = Orb(
        ring_counts=[24, 12, 6, 1],
        pin=16,
        status_leds=0,
        brightness=20
    )

    print(f"Orb initialized: {orb.num_rings} rings, {orb.outer_count} axes")

    # Clear to start
    orb.clear_ornament(show=True)
    sleep(0.5)

    # Light up each ring in sequence
    print("Lighting rings...")
    colors = ['red', 'green', 'blue', 'yellow']
    for ring_num in range(orb.num_rings):
        orb.set_ring(ring_num, colors[ring_num % len(colors)], show=True)
        sleep(0.5)

    sleep(1)
    orb.clear_ornament(show=True)
    sleep(0.5)

    # Light up axes in sequence
    print("Lighting axes...")
    for axis in range(min(8, orb.outer_count)):
        orb.clear_ornament()
        orb.set_axis(axis, (255, 255, 0))  # Yellow
        orb.pixelsShow()
        sleep(0.2)

    sleep(1)
    orb.clear_ornament(show=True)
    sleep(0.5)

    # Draw lines
    print("Drawing lines...")
    for axis in range(0, orb.outer_count, 3):
        orb.set_line(axis, (0, 255, 255), show=True)  # Cyan
        sleep(0.3)

    sleep(1)

    # Cleanup
    orb.clear_ornament(show=True)
    print("Example complete!")


def example_animations():
    """Example showing built-in animations."""
    print("=== Orb Extension Animation Example ===")

    orb = Orb(
        ring_counts=[24, 12, 6, 1],
        pin=16,
        status_leds=0,
        brightness=20
    )

    # Spiral animations
    print("Spiral in...")
    orb.spiral_in((255, 0, 0), delay=0.2)
    sleep(1)

    print("Spiral out...")
    orb.clear_ornament(show=True)
    sleep(0.5)
    orb.spiral_out((0, 255, 0), delay=0.2)
    sleep(1)

    # Rotating axis
    print("Rotating axis for 5 seconds...")
    orb.clear_ornament(show=True)
    orb.rotate_axis((0, 0, 255), speed=0.05, duration=5)

    print("Animations complete!")


if __name__ == "__main__":
    # Uncomment to run examples
    # example_basic()
    # example_animations()
    pass

