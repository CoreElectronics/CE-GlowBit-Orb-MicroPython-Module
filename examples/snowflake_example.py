"""
bauble_example.py - Patterns suited for the Bauble artwork
"""

from orb_extension import Orb
from orb_extension.animations import CometAnimation, FlameAnimation, step_comets
from time import sleep, ticks_ms


orb = Orb(preset='pico')

# TODO: Pack function segment_by_axis into lib



top_colour = orb.rgbColour(0, 160, 255) # Cyan
bottom_colour = orb.rgbColour(255, 80, 0) # Orange


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

    return below, above

print("Splitting orb into halves and filling with colors...\n")

# Demo code starts here

print("Demo 1: Immediate fill at axis 0")

orb.clear_ornament()
above, below = segment_by_axis(0, include_center=False)


def top_colour_action(above_pixels, colour):
    for pix in above_pixels:
        orb.pixelSet(pix, colour)

def bottom_colour_action(below_pixels, colour):
    for pix in below_pixels:
        orb.pixelSet(pix, colour)

# REMIX:
'''
Fade top on and off, fade bottom on and off?
Fade them both on and off at the same time?
Could do something with the pixel values (like the animation below)
'''

while True:
    top_colour_action(above, top_colour)
    bottom_colour_action(below, bottom_colour)
    
    orb.pixelsShow() # Always refresh the colour of the display, sometimes LEDs can lose colour

    sleep(10)
    


## TODO: END EXAMPLE HERE

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







