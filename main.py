"""Script for a robot that chases a ball and knocks it in a semirandom direction to play with a dog."""

#
# IMPORTS
#
from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera


#
# TODOs
#
# TODO: Implement good-practice logging
# TODO: Consider splitting some of the ### zones into separate files.
# TODO: Update PDF scans
# TODO: Update set_motors to allow for nuanced control, not just bang-bang.
# TODO: Can I switch "rover_picture.jpg" to .bmp or other to increase performance by skipping image compression?


#
# USER-SET PARAMETERS
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
# CLASSES
#
class Transition:
    """Transition edge between 2 nodes."""

    def __init__(self, symbol: str, node_destination_name: str) -> None:
        """:param symbol: the name of the symbol that causes this transition.
        :param node_destination_name: the name of the destination node
        """
        self.symbol = symbol
        self.node_destination_name = node_destination_name


class Node:
    """Node with a name and a list of transitions."""

    def __init__(self, name: str, transitions: Set[Transition], func: Callable) -> None:
        """:param name: the name of the node
        :param transitions: all Transition objects pointing *away* from the node
        :param func: the helper function that should be called while this node is active.  func must return a transition symbol (ie string).
        """
        self.name = name
        self.transitions = transitions
        self.func = func


class DFSM:
    """Deterministic finite state machine."""

    def __init__(self, nodes: List[Node], active_node: Node) -> None:
        """:param nodes: all nodes in the finite state machine
        :param active_node: the node currently being executed upon
        """
        self.nodes = nodes
        self.active_node = active_node

    def traverse_symbol(self, symbol: str) -> None:
        """Based on the DFSM's active node and the argument symbol, change the active node to whatever the symbol points
        to.
        :param symbol: the symbol of a single transition
        """
        # Transition to the new node.
        for transition in self.active_node.transitions:
            if transition.symbol == symbol:
                self.active_node = transition.node_destination_name
                return None
        # If we reach this part of the code, then the node was not found.  Raise an error.
        raise RuntimeError("no node to transition to from node " + self.active_node.name + " on transition symbol " + symbol)

    def run_dfsm(self) -> None:
        """Begin running the DFSM.  Repeatedly call the function of the active state, then transition based on the
        symbol returned.
        """
        while True:
            # Call the function of the active state and save the transition symbol it returns
            print("Running " + str(self.active_node.func) + "...")
            transition_symbol = self.active_node.func()
            print(transition_symbol)
            # State-transition based on the symbol returned
            self.traverse_symbol(transition_symbol)


#
# DFSM STATE FUNCTIONS
#
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
    if get_ball_position() is None:
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


#
# HELPER FUNCTIONS OTHER THAN DFSM STATE FUNCTIONS
#
def get_ball_position() -> Union[int, None]:
    """Check the camera, then return the x coordinate of the pixel containing the centroid
    of the ball, in pixels.  x = 0 indicates a leftmost pixel.  If no ball is found, return None.
    """
    global my_camera
    global PICTURE_FILENAME
    # Check the camera
    my_camera.capture(PICTURE_FILENAME)
    # Find and return the centroid of the tennis ball, if one exists.  Else return None.
    # TODO


#
# MAIN SCRIPT
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

# Start running the finite-state machine!
rover_DFSM.run_dfsm()
