"""
animations.py - Reusable animation classes for orb displays

This module provides animation classes that can be used with the Orb class.
Each animation is designed to be non-blocking and step-based for easy integration.
"""

import math
import random
from time import ticks_ms, ticks_diff


class CometAnimation:
    """
    Comet/shooting star animation for orb displays.

    A comet moves along a ring with a trailing tail.
    """

    def __init__(self, orb, ring_number, colour, clockwise=True,
                 tail_length=4, speed=0.07, start_pos=0, easing=True):
        """
        Initialize a comet animation.

        Args:
            orb: Orb instance
            ring_number: Ring index (0 = outermost)
            colour: Comet color (r,g,b) tuple or string
            clockwise: Movement direction
            tail_length: Number of LEDs in tail (including head)
            speed: Seconds per step
            start_pos: Starting position on ring
            easing: Use smooth brightness falloff for tail
        """
        self.orb = orb
        self.ring_number = int(ring_number)
        self.colour = self._parse_color(colour)
        self.clockwise = bool(clockwise)
        self.tail_length = int(max(1, tail_length))
        self.speed_s = float(speed)
        self.easing = bool(easing)

        self.head_pos = int(start_pos)
        self._last_step_ms = ticks_ms()

        # Get ring info
        self.ring_indices = orb.get_ring_indices(ring_number)
        self.ring_len = len(self.ring_indices)

    def _parse_color(self, colour):
        """Convert color to (r,g,b) tuple."""
        if isinstance(colour, (tuple, list)) and len(colour) == 3:
            return tuple(int(x) for x in colour)

        if isinstance(colour, str):
            color_map = {
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'purple': (128, 0, 128),
                'cyan': (0, 255, 255),
                'white': (255, 255, 255),
            }
            return color_map.get(colour.lower(), (128, 128, 128))

        return (128, 128, 128)  # Fallback

    def step(self):
        """
        Update comet position if enough time has elapsed.

        Returns:
            True if position was updated, False otherwise
        """
        if self.ring_len == 0:
            return False

        now_ms = ticks_ms()
        elapsed = ticks_diff(now_ms, self._last_step_ms)
        interval_ms = int(self.speed_s * 1000)

        if interval_ms <= 0:
            interval_ms = 1

        if elapsed >= interval_ms:
            steps = max(1, elapsed // interval_ms)
            for _ in range(steps):
                if self.clockwise:
                    self.head_pos = (self.head_pos + 1) % self.ring_len
                else:
                    self.head_pos = (self.head_pos - 1) % self.ring_len
            self._last_step_ms = now_ms
            return True

        return False

    def render(self, accum):
        """
        Render comet to accumulation buffer.

        Args:
            accum: Dict mapping pixel_index -> [r, g, b] for additive blending
        """
        if self.ring_len == 0:
            return

        head = self.head_pos % self.ring_len
        tail = min(self.tail_length, self.ring_len)

        for t in range(tail):
            # Compute tail position based on direction
            if self.clockwise:
                pos = (head - t) % self.ring_len
            else:
                pos = (head + t) % self.ring_len

            pix = self.ring_indices[pos]

            # Brightness falloff
            frac = 1.0 - (t / float(tail))
            if self.easing:
                frac = self._smoothstep(frac)

            r = int(self.colour[0] * frac)
            g = int(self.colour[1] * frac)
            b = int(self.colour[2] * frac)

            if pix not in accum:
                accum[pix] = [0, 0, 0]
            accum[pix][0] += r
            accum[pix][1] += g
            accum[pix][2] += b

    @staticmethod
    def _smoothstep(t):
        """Smoothstep easing function."""
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        return t * t * (3 - 2 * t)


class FlameAnimation:
    """
    Realistic flame flicker animation along an axis.

    Creates a flickering flame effect with gust simulation.
    """

    def __init__(self, orb, axis, base_color=(255, 160, 64),
                 angular_width=1, radial_limit=None,
                 flicker_strength=0.45, flicker_speed=1.0,
                 gust_mean=4.0, gust_mag_max=0.9, gust_smooth=0.6,
                 include_center=True):
        """
        Initialize flame animation.

        Args:
            orb: Orb instance
            axis: Central axis for flame
            base_color: Base flame color (r,g,b)
            angular_width: Number of neighbor axes on each side
            radial_limit: Max radial layers (None = all)
            flicker_strength: Brightness variation 0-1
            flicker_speed: Temporal speed multiplier
            gust_mean: Mean seconds between gusts
            gust_mag_max: Maximum gust magnitude 0-1
            gust_smooth: Gust transition smoothing time
            include_center: Include center LED
        """
        self.orb = orb
        self.axis = int(axis) % orb.outer_count
        self.base_color = tuple(int(x) for x in base_color)
        self.angular_width = max(0, int(angular_width))
        self.radial_limit = radial_limit
        self.flicker_strength = float(flicker_strength)
        self.flicker_speed = float(flicker_speed)
        self.gust_mean = float(gust_mean)
        self.gust_mag_max = float(gust_mag_max)
        self.gust_smooth = float(gust_smooth)
        self.include_center = include_center

        # Build pixel list with metadata
        self._build_pixel_list()

        # Dynamic state
        self._global_intensity = 1.0
        self._noise_phase = random.random() * 1000.0
        self._last_time = ticks_ms() / 1000.0
        self._bias = 0.0
        self._bias_target = 0.0
        self._next_gust_time = self._last_time + self._expovariate(self.gust_mean)
        self._last_written = {}

    def _build_pixel_list(self):
        """Build list of pixels and their metadata."""
        # Get central axis and neighbors
        col_indices = [self.axis]
        for d in range(1, self.angular_width + 1):
            col_indices.append((self.axis + d) % self.orb.outer_count)
            col_indices.append((self.axis - d) % self.orb.outer_count)

        self.pixel_list = []
        self.pixel_meta = {}

        for col_dist, col_idx in enumerate(col_indices):
            col = self.orb.get_axis_indices(col_idx, include_center=self.include_center)

            if self.radial_limit is not None:
                col = col[:self.radial_limit]

            for ridx, pix in enumerate(col):
                self.pixel_list.append(pix)
                self.pixel_meta[pix] = (col_idx, col_dist, ridx)

        # Compute max radial index
        self.max_ridx = 0
        for (_, _, ridx) in self.pixel_meta.values():
            self.max_ridx = max(self.max_ridx, ridx)

    def step(self, dt):
        """
        Update flame animation state.

        Args:
            dt: Elapsed time since last step (seconds)

        Returns:
            Dict mapping pixel_index -> (r, g, b)
        """
        # Update noise phase
        self._noise_phase += dt * (0.8 + self.flicker_speed * 1.6)
        noise = math.sin(self._noise_phase * 3.7) * 0.7 + math.sin(self._noise_phase * 13.1) * 0.3
        target_intensity = 1.0 + (noise * 0.5) * self.flicker_strength
        tau = max(0.001, 1.0 / max(0.1, self.flicker_speed))
        alpha = 1.0 - math.exp(-dt / tau)
        self._global_intensity += (target_intensity - self._global_intensity) * alpha

        # Check for gust
        now = ticks_ms() / 1000.0
        if now >= self._next_gust_time:
            self._bias_target = (random.random() * 2.0 - 1.0) * self.gust_mag_max
            self._next_gust_time = now + self._expovariate(max(0.001, self.gust_mean))

        # Smooth bias
        if self.gust_smooth > 0:
            b_alpha = 1.0 - math.exp(-dt / max(0.0001, self.gust_smooth))
            self._bias += (self._bias_target - self._bias) * b_alpha
        else:
            self._bias = self._bias_target

        # Compute pixel colors
        result = {}
        for pix in self.pixel_list:
            col_idx, col_dist, ridx = self.pixel_meta[pix]

            # Angular weight (closer to center axis = brighter)
            ang_w = 1.0 / (1.0 + col_dist * 0.6) if col_dist > 0 else 1.0
            ang_w = max(0.0, min(1.0, ang_w))

            # Radial weight (shape of flame)
            if self.max_ridx > 0:
                t = ridx / self.max_ridx
                rad_w = 0.5 + 0.6 * (1.0 - abs(t - 0.6))
            else:
                rad_w = 1.0
            rad_w = max(0.02, min(1.0, rad_w))

            # Bias contribution (wind effect)
            cw = (col_idx - self.axis) % self.orb.outer_count
            ccw = (self.axis - col_idx) % self.orb.outer_count
            if cw == ccw:
                col_sign = 0.0
            elif cw < ccw:
                col_sign = 1.0
            else:
                col_sign = -1.0

            bias_contrib = col_sign * self._bias * ang_w

            # Base brightness
            base_b = max(0.0, ang_w * rad_w + bias_contrib * 0.5)
            base_b = max(0.0, min(1.5, base_b))

            brightness = base_b * self._global_intensity

            # Per-pixel micro-variation
            micro = (math.sin(self._noise_phase * (7.1 + ridx * 0.9 + col_dist * 0.6) + pix) * 0.5 + 0.5) - 0.5
            brightness += micro * (0.18 * self.flicker_strength * (0.8 - (ridx / max(1, self.max_ridx))))
            brightness = max(0.0, min(2.0, brightness))

            # Scale color
            r = int(max(0, min(255, round(self.base_color[0] * brightness))))
            g = int(max(0, min(255, round(self.base_color[1] * brightness))))
            b = int(max(0, min(255, round(self.base_color[2] * brightness))))

            result[pix] = (r, g, b)

        return result

    @staticmethod
    def _expovariate(mean):
        """MicroPython-compatible exponential distribution."""
        u = random.random()
        if u <= 0.0:
            u = 1e-10
        return -mean * math.log(u)


def step_comets(orb, comets, clear=True):
    """
    Step and render multiple comet animations.

    Args:
        orb: Orb instance
        comets: List of CometAnimation instances
        clear: Clear ornament before rendering

    Returns:
        True if any comet moved
    """
    # Update positions
    any_moved = False
    for comet in comets:
        if comet.step():
            any_moved = True

    # Clear ornament
    if clear:
        orb.clear_ornament()

    # Accumulate colors
    accum = {}
    for comet in comets:
        comet.render(accum)

    # Write to orb
    for pix, rgb in accum.items():
        r = min(255, rgb[0])
        g = min(255, rgb[1])
        b = min(255, rgb[2])
        orb.pixelSet(pix, orb.rgbColour(r, g, b))

    return any_moved


def example_comets():
    """Example: Multiple comets on different rings."""
    from orb import Orb
    from time import sleep

    print("=== Comet Animation Example ===")

    orb = Orb(ring_counts=[24, 12, 6, 1], pin=16, brightness=20)

    # Create comets on different rings
    comets = [
        CometAnimation(orb, ring_number=0, colour='blue', clockwise=True,
                      tail_length=5, speed=0.06),
        CometAnimation(orb, ring_number=0, colour=(0, 255, 128), clockwise=False,
                      tail_length=4, speed=0.09, start_pos=12),
        CometAnimation(orb, ring_number=1, colour='red', clockwise=True,
                      tail_length=3, speed=0.12),
    ]

    try:
        print("Running comet animation (Ctrl-C to stop)...")
        while True:
            step_comets(orb, comets, clear=True)
            orb.pixelsShow()
            sleep(0.03)
    except KeyboardInterrupt:
        orb.clear_ornament(show=True)
        print("\nAnimation stopped.")


def example_flame():
    """Example: Flickering flame effect."""
    from orb import Orb
    from time import sleep, ticks_ms

    print("=== Flame Animation Example ===")

    orb = Orb(ring_counts=[24, 12, 6, 1], pin=16, brightness=20)

    flame = FlameAnimation(
        orb,
        axis=0,
        base_color=(255, 160, 64),
        angular_width=2,
        radial_limit=None,
        flicker_strength=0.5,
        flicker_speed=1.2
    )

    try:
        print("Running flame animation (Ctrl-C to stop)...")
        last_time = ticks_ms() / 1000.0

        while True:
            now = ticks_ms() / 1000.0
            dt = now - last_time

            # Get pixel colors from flame
            pixels = flame.step(dt)

            # Clear ornament
            orb.clear_ornament()

            # Set pixels
            for pix, (r, g, b) in pixels.items():
                orb.pixelSet(pix, orb.rgbColour(r, g, b))

            orb.pixelsShow()

            last_time = now
            sleep(0.08)

    except KeyboardInterrupt:
        orb.clear_ornament(show=True)
        print("\nAnimation stopped.")


if __name__ == "__main__":
    # Uncomment to run examples
    # example_comets()
    # example_flame()
    pass
