"""
snowflake_example.py - Patterns suited for the Snowflake artwork
"""

# Preflashed Demo for the Snowflake Kit - swaps between 'frames' of coloured rings

from orb_extension import Orb
from orb_extension.animations import CometAnimation, FlameAnimation, step_comets
from time import sleep, ticks_ms

# Initialise Pico Orb - configures brightness to our tested values, pin number etc
orb = Orb(preset='pico')


# Colours defined as RGB tuples = (R, G, B)
DARK_BLUE  = orb.rgbColour(0, 0, 150)
LIGHT_BLUE = orb.rgbColour(30, 200, 255)
WHITE      = orb.rgbColour(200, 200, 200) # Slightly less intense white


# Action Functions

def action_A():
    
    # The outer ring is 0, next in is 1...
    orb.set_ring(0, DARK_BLUE)
    orb.set_ring(1, LIGHT_BLUE)
    orb.set_ring(2, DARK_BLUE)
    orb.set_ring(3, WHITE)
    orb.pixelsShow() # Update pixels

def action_B():

    orb.set_ring(0, WHITE)
    orb.set_ring(1, DARK_BLUE)
    orb.set_ring(2, LIGHT_BLUE)
    orb.set_ring(3, DARK_BLUE)
    orb.pixelsShow() # Update pixels


while True:

    action_A()
    sleep(0.8)
    
    action_B()
    sleep(0.8)
