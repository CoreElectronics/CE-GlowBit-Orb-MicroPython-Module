"""
bauble_example.py - Patterns suited for the Bauble artwork

"""

# Preflashed Demo - Colour wipe and blank

from orb_extension import Orb
from time import sleep

# Initialise Pico Orb - configures brightness to our tested values, pin number etc
orb = Orb(preset='pico')


# Colours defined as RGB tuples = (R, G, B)
top_colour = orb.rgbColour(255, 0, 0) # Red
bottom_colour = orb.rgbColour(0, 255, 0) # Green

blank_colour = orb.rgbColour(0, 0, 0) # All 0's to turn LEDs off

# Pre-defining the above and below pixels, the helper function does A LOT
above, below = orb.segment_by_axis(0, include_center=False)

# Action Functions

def action_A():
    # This function sweeps our defined colours on
    
    # Sweep through the pixels on the 'top' of the orb
    for pix in above:
        orb.pixelSet(pix, top_colour) # Setting them to the first colour
        orb.pixelsShow()
        sleep(0.02)

    # Reverse the order of pixels for the below half
    reverse_below = below[::-1]
    # Sweep through them in the reverse order
    for pix in reverse_below:
        orb.pixelSet(pix, bottom_colour) # Setting them to the second colour
        orb.pixelsShow()
        sleep(0.02)


# The same sweeping action but turning the LEDs off
def action_B():
    
    for pix in above:
        orb.pixelSet(pix, blank_colour)
        orb.pixelsShow()
        sleep(0.02)

    reverse_below = below[::-1]
    for pix in reverse_below:
        orb.pixelSet(pix, blank_colour)
        orb.pixelsShow()
        sleep(0.02)

# Ensure all LEDs are clear to begin with
orb.clear_ornament(show=True)

# Start our infinite loop
while True:
    action_A()
    sleep(0.5)
    
    action_B()
    sleep(0.5)
    