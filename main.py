"""Script for a robot that chases a ball and knocks it in a semirandom direction to play with a dog."""


from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera
from gpiozero import Robot

from graph import DFSM, Node, Transition
from robot_state_functions import search_func, aim_func, charge_func, wait_func, request_help_func


# TODO: Implement good-practice logging
# TODO: Consider splitting some of the ### zones into separate files.
# TODO: Update PDF scans
# TODO: Update set_motors to allow for nuanced control, not just bang-bang.
# TODO: Can I switch "rover_picture.jpg" to .bmp or other to increase performance by skipping image compression?


#
# CONSTANTS
#
MAXIMUM_SEARCH_TIME = 30  # seconds
BALL_CENTERED_ERROR_TOLERANCE = 30  # pixels
WAIT_TIME = 10  # seconds
HELP_FREQ_HZ = 1000    # Hz

IN1_PIN = 17
IN2_PIN = 27
IN3_PIN = 23
IN4_PIN = 24
SPEAKER_PIN = 18

PICTURE_FILENAME = "rover_picture.jpg"


#
# EXECUTION
#
# Set up pins
GPIO.setmode(GPIO.BCM)
rover = Robot(left=(8,7), right=(10,9))
GPIO.setup(SPEAKER_PIN, GPIO.OUT)    # Goes to speaker

# Set up the camera
my_camera = PiCamera()

# Build the finite-state machine for the rover.
node_search = Node("SEARCH", {Transition("Ball not found", "SEARCH"), Transition("Ball found", "AIM"), Transition("Search time exceeded maximum", "REQUEST HELP")}, search_func)
node_aim = Node("AIM", {Transition("Ball not centered", "AIM"), Transition("Ball centered", "CHARGE"), Transition("Ball lost", "SEARCH")}, search_func)
node_charge = Node("CHARGE", {Transition("Ball centered", "CHARGE"), Transition("Ball lost or not centered", "WAIT"), Transition("Motors stalling", "REQUEST HELP")}, charge_func)
node_wait = Node("WAIT", {Transition("Ball found", "AIM"), Transition("Ball lost", "SEARCH")}, wait_func)
node_request_help = Node("REQUEST HELP", set(), request_help_func)
rover_DFSM = DFSM([node_search, node_aim, node_charge, node_wait, node_request_help], active_node=node_search)

# Start running the finite-state machine!
rover_DFSM.run_dfsm()
