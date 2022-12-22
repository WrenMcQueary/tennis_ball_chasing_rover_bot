"""Functions for the robot to perform in each state of its DFSM.
"""


from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera
from datetime import datetime

from robot_other_functions import get_ball_x
from main import rover


def search_func() -> str:
    """Rotate >360 degrees looking for the ball.
    If ball not found, roam for a bit, then return "Ball not found"
    If ball found, return "Ball found" as soon as it's found.
    If search time exceeded maximum, then return "Search time exceeded maximum"
    """
    global MAXIMUM_SEARCH_TIME
    turn_interval_seconds = 0.25

    for ii in range(int(MAXIMUM_SEARCH_TIME / turn_interval_seconds)):
        if get_ball_x() is not None:
            return "Ball found"
        rover.left()
        time.sleep(turn_interval_seconds)
        rover.stop()
    return "Search time exceeded maximum"


def aim_func() -> str:
    """Use a feedback system to center the ball LR in the camera's view.
    If can't center the ball, return "Ball not centered"
    If successfully center the ball, return "Ball centered"
    """
    global BALL_CENTERED_ERROR_TOLERANCE
    global MAXIMUM_AIM_TIME
    global PICTURE_WIDTH

    turn_interval_seconds = 0.25

    # TODO: Empirically tune PID gains (could use the Ziegler-Nichols method from CS 685)
    kp = 1
    ki = 0
    kd = 0

    goal = PICTURE_WIDTH / 2

    err_old = 0
    err_i = 0
    for ii in range(int(MAXIMUM_AIM_TIME / turn_interval_seconds)):
        err = goal - get_ball_x()

        if abs(err) <= BALL_CENTERED_ERROR_TOLERANCE:
            return "Ball centered"

        err_p = err * kp
        err_i += err * ki
        #err_d = (err - err_old) * kd
        #u = kp*err_p - kd*err_d - ki*err_i
        u = kp * err_p - ki * err_i     # We shouldn't have a differential component because we stop rotating between frames

        if u == 0:
            rover.stop()
        elif u > 0:
            rover.left(u)
        elif u > 0:
            rover.right(-u)

        # TODO: If our input to rover.left() or rover.right() was greater than 1, log that we saturated that function.
        time.sleep(turn_interval_seconds)
        rover.stop()
        err_old = err

    return "Ball not centered"


def charge_func() -> str:
    """Set motors to full, then check if ball is centered.
    If motors stalling, then return "Motors stalling"
    If ball is centered, then return "Ball centered"
    If ball is not centered, then return "Ball lost or not centered"
    """
    global BALL_CENTERED_ERROR_TOLERANCE
    global PICTURE_WIDTH

    rover.forward()

    ball_x = get_ball_x()

    # TODO: If motors stalling, then return "Motors stalling"

    if abs(ball_x - PICTURE_WIDTH/2) > BALL_CENTERED_ERROR_TOLERANCE:
        return "Ball lost or not centered"
    else:
        return "Ball centered"


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
