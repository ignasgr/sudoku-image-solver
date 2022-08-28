from typing import Tuple

import cv2
import numpy as np

import imageproc.contours


def _sort_points(points: np.ndarray, row_size: int) -> np.ndarray:
    """
    Sorts points as if they were organized on a grid: left to right,
    top to bottom.

    Parameters
    -----------
        points (np.ndarray): an array of two-coordinate points to sort
        row_size (int): the number of points per row (dictates move to next row)

    Returns
    -------
        sorted_points (np.ndarray): sorted version of original array
    """

    # number of points
    n_points = len(points)

    # initializing array to store result
    sorted_points = np.empty_like(points, dtype="float32")

    # sorting top-to-bottom first
    points = sorted(points, key=lambda p: p[1])

    # sorting each row left-to-right
    for start_idx in range(0, n_points, row_size):
        row = points[start_idx : start_idx + row_size]
        row = sorted(row, key=lambda p: p[0])
        sorted_points[start_idx : start_idx + row_size] = row

    return sorted_points


def grey_blur_threshold(
    image: np.ndarray,
    ksize: Tuple[int, int],
    adaptiveMethod: int,
    thresholdType: int,
    blockSize: int,
    C: int,
) -> np.ndarray:
    """
    Wrapper function for performing common pre-processing steps of greying,
    bluring, and thresholding an image

    Parameters
    ----------
        image (np.ndarray): image to process
        ksize (int, int): parameter for cv2.GaussianBlur
        adaptiveMethod (int): parameter for cv2.adaptiveThreshold
        thresholdType (int): parameters for cv2.adaptiveThreshold
        blockSize (int): parameters for cv2.adaptiveThreshold
        C (int): parameters for cv2.adaptiveThreshold

    Returns
    -------
        greyed (np.ndarray): greyed version of image
        blurred (np.ndarray): greyed, and blurred version of image
        thresh (np.ndarray): thresholded image after grey, and blur
    """

    greyed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(greyed, ksize, 0, 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, adaptiveMethod, thresholdType, blockSize, C
    )

    return greyed, blurred, thresh


def sort_cells(contours: list) -> list:
    """
    Sorts the cell contours of a sudoku grid such that they are sorted
    left-to-right, top-to-bottom

    Parameters
    ----------
        contours (list): contours to sort

    Returns
    -------
        sorted_contours (list): a sorted version the original contours
    """

    # number of cells in a standard sudoku row
    ROW_SIZE = 9

    # sorting contours, by using their centers
    centers = [imageproc.contours.get_center(c) for c in contours]
    sorted_centers = [tuple(p) for p in _sort_points(centers, row_size=ROW_SIZE)]

    # tuples representing contour centers are unique
    # producing list of sorted contour labels (labels are indices)
    pre_sort_idx = [centers.index(p) for p in sorted_centers]

    # using sorted indices to get contours in sorted order
    sorted_contours = [contours[idx] for idx in pre_sort_idx]

    return sorted_contours


def extract_cells(image: np.ndarray, bboxes: list) -> Tuple[list, list]:
    """
    Creates a 28x28 image out of each cell in the sudoku grid

    Parameters
    ----------
        image (np.array): image of sudoku grid
        bounds (list): boxes of cells, define the cropping area

    Returns
    -------
        mtx_indices (list): column of row, column index tuples for use in matrix
        digits (list): openCV images of digits
    """

    # instatiating lists to hold digit locations  and cropped image of the digit
    mtx_indices = []
    digit_images = []

    # the mount by which to expand or contact cell boundaries by
    # helps if cells have white boundaries
    OFFSET = 3

    for idx, b in enumerate(bboxes):
        # cropping a cell and resizing
        cell = image[
            b[1] + OFFSET : b[1] + b[3] - OFFSET, b[0] + OFFSET : b[0] + b[2] - OFFSET
        ]
        cell = cv2.resize(cell, (28, 28), interpolation=cv2.INTER_AREA)

        # converting index value to index for 2d array
        row_idx, col_idx = idx // 9, idx % 9

        # storing results
        mtx_indices.append((row_idx, col_idx))
        digit_images.append(cell)

    return mtx_indices, digit_images


def write_text(image, puzzle, solution, centers, mode="solution"):
    """
    Writes the solved values onto the sudoku image.

    Parameters
    ----------
        image (np.array): openCV image
        puzzle (np.array): matrix representing the original puzzle
        solution (np.array): matrix of the solved puzzle
        centers (tuple): coordinates representing centers of sudoku cells
        mode (str): indicator for what to write to image

    Returns
    -------
        image (np.ndarray): original image with text annotations
    """

    # flattening will make iteration straight forward
    puzzle = puzzle.flatten()
    solution = solution.flatten()
    tuples = zip(puzzle, solution, centers)

    # adjusting write options based on mode
    if mode == "solution":
        digits_to_write = [(t[1], t[2]) for t in tuples if t[0] != t[1]]
        thickness = 3
        offset = 10
        font_scale = 1
    elif mode == "starting_values":
        digits_to_write = [(t[0], t[2]) for t in tuples if t[0] != 0]
        thickness = 2
        offset = -8
        font_scale = 0.7
    else:
        raise ValueError("Mode must be either 'solution' or 'starting_values'")

    # writing text on to image
    for val, c in digits_to_write:
        cv2.putText(
            img=image,
            text=str(val),
            org=(c[0] - offset, c[1] + offset),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=font_scale,
            thickness=thickness,
            color=(255, 0, 0),
        )

    return image
