"""
bauble_example.py - Patterns suited for the Bauble artwork

"""

# Preflashed Demo - Colour wipe and blank

from orb_extension import Orb
from time import sleep


orb = Orb(preset='pico')

top_colour = orb.rgbColour(0, 160, 255) # Cyan
bottom_colour = orb.rgbColour(255, 80, 0) # Orange

# Pre-defining the above and below pixels
above, below = orb.segment_by_axis(0, include_center=False)

# Action Functions
def action_A(colour1, colour2):
    
    # Sweep through the pixels on the 'top' of the orb
    for pix in above:
        orb.pixelSet(pix, colour1) # Setting them to the first colour
        orb.pixelsShow()
        sleep(0.02)

    # Reverse the order of pixels for the below half
    reverse_below = below[::-1]
    # Sweep through them in the reverse order
    for pix in reverse_below:
        orb.pixelSet(pix, colour2) # Setting them to the second colour
        orb.pixelsShow()
        sleep(0.02)


# Do the same for the second action
def action_B(colour1, colour2):
    
    for pix in above:
        orb.pixelSet(pix, colour1)
        orb.pixelsShow()
        sleep(0.02)

    reverse_below = below[::-1]
    for pix in reverse_below:
        orb.pixelSet(pix, colour2)
        orb.pixelsShow()
        sleep(0.02)


orb.clear_ornament(show=True)

blank_colour = orb.rgbColour(0, 0, 0)

while True:
    action_A(top_colour, bottom_colour)
    sleep(0.5)
    action_A(blank_colour, blank_colour)
    sleep(0.5)
    
