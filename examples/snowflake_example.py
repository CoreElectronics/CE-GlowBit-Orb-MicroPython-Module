"""
snowflake_example.py - Patterns suited for the Snowflake artwork
"""

from orb_extension import Orb
from orb_extension.animations import CometAnimation, FlameAnimation, step_comets
from time import sleep, ticks_ms


orb = Orb(preset='pico')


# Define colors
DARK_BLUE  = orb.rgbColour(0, 0, 150)
LIGHT_BLUE = orb.rgbColour(30, 200, 255)
WHITE      = orb.rgbColour(255, 255, 255)


# Animation/Action Functions
# Ring numbers: 0=outer, 1=2nd, 2=3rd, 3=center
def action_A(colour1, colour2):
    
    orb.set_ring(0, colour1)
    orb.set_ring(2, colour2)

def action_B(colour1, colour2):
    
    orb.set_ring(1, colour1)
    orb.set_ring(3, colour2)

flag = True
while True:

    # Set up a condition to toggle between colour configurations
    if flag == True:
        action_A(DARK_BLUE, WHITE)
        action_B(LIGHT_BLUE, DARK_BLUE)
    else:
        action_A(LIGHT_BLUE, DARK_BLUE)
        action_B(DARK_BLUE, WHITE)
    
    flag = not flag # Toggle the flag

    orb.pixelsShow() # Update pixels

    sleep(2)

