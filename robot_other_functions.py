"""Robot functions other than its DFSM state functions.
"""


from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera


def get_ball_x() -> Union[int, None]:
    """Check the camera, then return the x coordinate of the pixel containing the centroid
    of the ball, in pixels.  x = 0 indicates a leftmost pixel.  If no ball is found, return None.
    """
    global my_camera
    global PICTURE_FILENAME
    # Check the camera
    my_camera.capture(PICTURE_FILENAME)
    # Find and return the centroid of the tennis ball, if one exists.  Else return None.
    # TODO