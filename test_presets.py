"""
test_presets.py - Quick test to verify preset functionality

This script demonstrates the new preset feature for easy hardware configuration.
"""

# Make sure glowbit.py is in the parent directory
import sys
sys.path.insert(0, '..')

from orb_extension import Orb
from time import sleep


def test_pico_preset():
    """Test Pico Orb preset."""
    print("\n=== Testing Pico Orb Preset ===\n")
#     print(preset='pico')
    orb = Orb(preset='pico')

    print(f"Configuration loaded:")
    print(f"  Ring counts: {orb.ring_counts}")
    print(f"  Total LEDs: {orb.numLEDs}")
    print(f"  Outer ring count: {orb.outer_count}")
    print(f"  Number of rings: {orb.num_rings}")
    print(f"  Status LEDs: {orb.status_leds}")

    # Quick light test
    print("\nLighting each ring...")
    colors = ['red', 'green', 'blue', 'yellow']
    for i in range(orb.num_rings):
        orb.clear_ornament()
        orb.set_ring(i, colors[i % len(colors)], show=True)
        sleep(0.5)

    orb.clear_ornament(show=True)
    print("Pico preset test complete!\n")


def test_mini_preset():
    """Test Mini Orb preset."""
    print("\n=== Testing Mini Orb Preset ===\n")

    orb = Orb(preset='mini')

    print(f"Configuration loaded:")
    print(f"  Ring counts: {orb.ring_counts}")
    print(f"  Total LEDs: {orb.numLEDs}")
    print(f"  Outer ring count: {orb.outer_count}")
    print(f"  Number of rings: {orb.num_rings}")
    print(f"  Status LEDs: {orb.status_leds}")

    # Quick light test
    print("\nLighting each ring...")
    colors = ['cyan', 'purple', 'white']
    for i in range(orb.num_rings):
        orb.clear_ornament()
        orb.set_ring(i, colors[i % len(colors)], show=True)
        sleep(0.5)

    orb.clear_ornament(show=True)
    print("Mini preset test complete!\n")


def test_preset_with_override():
    """Test preset with parameter override."""
    print("\n=== Testing Preset with Override ===\n")

    # Use Pico preset but with higher brightness
    orb = Orb(preset='pico', brightness=100)

    print(f"Configuration loaded:")
    print(f"  Using 'pico' preset with brightness=100 override")
    print(f"  Ring counts: {orb.ring_counts}")

    # Quick blink test
    print("\nBlinking outer ring at high brightness...")
    for _ in range(3):
        orb.set_ring(0, 'white', show=True)
        sleep(0.3)
        orb.clear_ornament(show=True)
        sleep(0.3)

    print("Override test complete!\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Orb Extension Preset System Test")
    print("="*60)

    # Run tests - comment out the ones you don't need
    test_pico_preset()
    # test_mini_preset()
    # test_preset_with_override()

    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60 + "\n")
