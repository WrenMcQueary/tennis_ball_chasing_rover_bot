"""Robot functions other than its DFSM state functions.
"""


from typing import Set, List, Callable, Union
import time
import RPi.GPIO as GPIO
from picamera import PiCamera
from skimage import io, color, feature, transform
import numpy as np


# Set up the camera
my_camera = PiCamera()
PICTURE_FILENAME = "rover_picture.jpg"


def get_ball_x() -> Union[int, None]:
    """Check the camera, then return the x coordinate of the pixel containing the centroid
    of the ball, in pixels.  x = 0 indicates a leftmost pixel.  If no ball is found, return None.
    """
    global my_camera
    global PICTURE_FILENAME
    # Check the camera
    my_camera.capture(PICTURE_FILENAME)
    image = transform.rotate(io.imread(PICTURE_FILENAME), 180)

    # Use a mask to make hte entire image black except for the ball
    image_grayscale = 255 * color.rgb2gray(image)
    tennis_ball_greener_than_red_mask = image[:, :, 1] > 1 * image[:, :, 0]
    tennis_ball_greener_than_blue_mask = image[:, :, 1] > 1.5 * image[:, :, 2]
    tennis_ball_bright_mask = image_grayscale > 20
    tennis_ball_combined_mask = np.logical_and(np.logical_and(tennis_ball_greener_than_red_mask,
                                                              tennis_ball_greener_than_blue_mask),
                                               tennis_ball_bright_mask)
    tennis_ball_combined_mask_inverted = np.logical_not(tennis_ball_combined_mask)
    image[tennis_ball_combined_mask] = [255, 255, 255]
    image[tennis_ball_combined_mask_inverted] = [0, 0, 0]
    image_ready_for_blob_detection = color.rgb2gray(image)

    # Find the largest blob for the frame and return its x-coordinate.  If no blobs found, return None.
    blobs = feature.blob_log(image_ready_for_blob_detection, max_sigma=30, min_sigma=3, num_sigma=10, threshold=0.1)[0]     # TODO: Tune these arguments
    if len(blobs) == 0:
        return None
    return blobs[0][1]
