import cv2
import numpy as np

import imageproc.utils


def resize(
    image: np.ndarray, width: int | None = None, height: int | None = None
) -> np.ndarray:
    """
    Resizes an image to desired height or width while maintining aspect ratio.

    Parameters
    ----------
        image (np.ndarray): image to resize
        width (int): desired width of image
        height (int): desired height of image

    Returns
    -------
        resized(np.ndarray): resized image
    """

    # getting image height, widgth, and aspect ratio
    h, w = image.shape[:2]
    aspect = h / w

    # interpolation method based on shrinkage or expansion
    if width < w or height < h:
        interpol = cv2.INTER_AREA
    else:
        interpol = cv2.INTER_CUBIC

    # calculating new dimensions
    if width is not None:
        dim = (width, int(aspect * width))
    elif height is not None:
        dim = (int(1 / aspect * height), height)
    else:
        raise ValueError("No width or height provided.")

    # resizing
    resized = cv2.resize(src=image, dsize=dim, interpolation=interpol)

    return resized


def top_down_view(
    image: np.ndarray,
    points: np.ndarray,
    margin: int = 10,
    sidelen: int = 500,
) -> np.ndarray:
    """
    Corrects the perspective of an image into a top-down view as defined by four
        corners.

    Parameters
    ----------
        image (np.array): original image to perform perspective transform on
        points (np.array): the four points on the image that get moved to new locations
        margin (int): the distance between the edge of the image and area of interest
            defined by the points
        sidelen (int): the distance between between two adjacent points after correction

    Returns
    -------
        transf_image (np.array): image that has been perspective-corrected
    """

    # defining the locations of the post-transformed corners
    new_points = np.array(
        [
            [margin, margin],
            [margin + sidelen, margin],
            [margin, margin + sidelen],
            [margin + sidelen, margin + sidelen],
        ],
        dtype="float32",
    )

    # sorting corners so transformation happens in the correct order
    points = imageproc.utils._sort_points(points, row_size=2)

    # transforming the image into a square, top-down view
    dim = sidelen + 2 * margin
    transf_mat = cv2.getPerspectiveTransform(points, new_points)
    transf_image = cv2.warpPerspective(image, transf_mat, (dim, dim))

    return transf_image
