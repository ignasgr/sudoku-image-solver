from typing import Tuple

import cv2
import numpy as np


def _is_quadrilateral(
    contour: np.ndarray, error: float
) -> Tuple[bool, np.ndarray, np.ndarray]:
    """
    Determines whether a contour is a quadrilateral subject to its closeness to
    its contour approximation.

    Parameters
    ----------
        contour (np.ndarray): an array of two-coordinate points
        error (float): allowable percentage error between contour and
            approximation

    Returns
    -------
        is_quad (bool): boolean indicator for whether contour is a quadrilateral
        contour (np.ndarray): the original contour
        approx_shape (np.ndarray): points that approximate the shape of the
            contour
    """

    # finding the characterstics of the contour
    perimeter = cv2.arcLength(curve=contour, closed=True)
    approx_shape = cv2.approxPolyDP(
        curve=contour, epsilon=error * perimeter, closed=True
    )

    # four points indicate quadrilateral
    if len(approx_shape) == 4:
        is_quad = True
    else:
        is_quad = False

    return is_quad, contour, approx_shape


def find_quadrilaterals(
    image: np.ndarray,
    mode: int,
    error: float,
    bounds: Tuple[float, float] | None = None,
) -> Tuple[list, list]:
    """
    Idenfities all quadrilateral contours in an image

    Parameters
    ----------
        image (np.ndarray): thresholded image
        mode (int): retrieval mode for contours
        error (float): allowable percentage error for contour approzimation
        bounds (int, int): upper and lower bound search restrictions for contour
            area relative to image area

    Returns
    -------
        quad_contours (list): quadrilateral contours found in image
        quad_corners (list): corners of contour approximation
    """

    # contouring image
    contours, _ = cv2.findContours(image, mode=mode, method=cv2.CHAIN_APPROX_SIMPLE)

    # initialize to store results
    quad_contours = []
    quad_corners = []

    for c in contours:
        quad, _, corners = _is_quadrilateral(c, error)

        # area of contour is irrelevant
        if bounds is None:
            area_cond = True
        # area of contour matters
        else:
            image_area = image.shape[0] * image.shape[1]
            ratio = cv2.contourArea(c) / image_area
            area_cond = bounds[0] < ratio < bounds[1]

        # conditionally adding to result
        if quad and area_cond:
            quad_contours.append(c)
            quad_corners.append(corners)

    return quad_contours, quad_corners


def fill_contours(
    image: np.ndarray, mode: int, bounds: Tuple[float, float]
) -> np.ndarray:
    """
    Fills contours whose area relavant to the image falls within bounds

    Parameters
    ----------
        image (np.ndarray): black and white image in which to fill contours
        bounds (float, float): upper and lower bound search restrictions for contour
            area relative to image area

    Returns
    -------
        filled (np.ndarray): image with contours filled
    """

    # image area will be needed for targeting contours of certain size
    image_area = image.shape[0] * image.shape[1]

    # finding the contours and filling them based on condition
    contours, _ = cv2.findContours(image, mode=mode, method=cv2.CHAIN_APPROX_SIMPLE)
    contours = [
        c for c in contours if bounds[0] < cv2.contourArea(c) / image_area < bounds[1]
    ]
    filled = cv2.drawContours(image, contours, -1, (0, 0, 0), -1)

    return filled


def get_center(contour: np.ndarray) -> Tuple[int, int]:
    """
    Finds the center of a contour

    Parameters
    ----------
        contour (np.ndarray): contour for which to find center of

    Returns
    -------
        center_x (int): x-coordinate of center
        center_y (int): y-coordinate of center
    """

    m = cv2.moments(contour)

    center_x = int(m["m10"] / m["m00"])
    center_y = int(m["m01"] / m["m00"])

    return center_x, center_y
