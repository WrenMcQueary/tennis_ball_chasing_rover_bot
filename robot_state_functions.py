"""Functions for the robot to perform in each state of its DFSM.
"""


from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera

from robot_other_functions import get_ball_x


def search_func() -> str:   # TODO
    """Rotate 360 degrees looking for the ball.
    If ball not found, roam for a bit, then return "Ball not found"
    If ball found, return "Ball found" as soon as it's found.
    If search time exceeded maximum, then return "Search time exceeded maximum"
    """
    global MAXIMUM_SEARCH_TIME
    pass


def aim_func() -> str:  # TODO
    """Use a feedback system to center the ball LR in the camera.
    If can't center ball, return "Ball not centered"
    If successfully center ball, return "Ball centered"
    """
    global BALL_CENTERED_ERROR_TOLERANCE
    pass


def charge_func() -> str:   # TODO
    """Set motors to full, then check if ball is centered.
    If ball is centered, then return "Ball centered"
    If ball is not centered, then return "Ball lost or not centered"
    If motors stalling, then return "Motors stalling"
    """
    global BALL_CENTERED_ERROR_TOLERANCE
    pass


def wait_func() -> str:
    """Give the moving ball time to come to rest.
    Then, if ball is in camera (not necessarily centered), return "Ball found".
    If ball not in camera, return "Ball lost"
    """
    global WAIT_TIME
    time.sleep(WAIT_TIME)
    if get_ball_x() is None:
        return "Ball lost"
    else:
        return "Ball found"


def request_help_func() -> None:
    """Make a friendly barking sound, to indicate to a human that the rover is blocked from reaching the ball, or can't
    find it.  Remain in this state forever.
    """
    global SPEAKER_PIN
    global HELP_FREQ_HZ
    pwm = GPIO.PWM(SPEAKER_PIN, HELP_FREQ_HZ)
    pwm.start(50)   # Duty cycle of 50%
    while True:
        time.sleep(60)