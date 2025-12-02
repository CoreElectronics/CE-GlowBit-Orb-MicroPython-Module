"""
GlowBit Orb Extension Library

This package extends the glowbit library with orb-specific functionality
for spherical LED ornaments with concentric rings.

Usage:
    from orb_extension import Orb

    # Use preset configuration
    orb = Orb(preset='pico')

    # Or custom configuration
    orb = Orb(ring_counts=[24, 12, 6, 1], pin=16)

    orb.set_axis(0, (255, 0, 0), show=True)
"""

from .orb import Orb, ORB_PRESETS

__version__ = "1.0.0"
__all__ = ['Orb', 'ORB_PRESETS']
