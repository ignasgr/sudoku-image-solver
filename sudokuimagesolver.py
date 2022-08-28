import argparse

import cv2
import numpy as np
from tensorflow.keras.models import load_model

import imageproc.contours
import imageproc.transforms
import imageproc.utils
import models.solver

parser = argparse.ArgumentParser()
parser.add_argument("--image", "-i", required=True, help="Name of image.")
parser.add_argument("--model", "-m", required=True, help="Name of OCR model")
args = parser.parse_args()

# reading in image
image = cv2.imread("data/puzzles/" + args.image)
if image is None:
    print("Could not find image:", args.image)
    exit()

# resizing image, maintaining aspect ratio
image = imageproc.transforms.resize(image, width=700)

# preprocessing image
_, _, thresh = imageproc.utils.grey_blur_threshold(
    image, (5, 5), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 2
)

# outside edge of sudoku grid will likely be quadrilateral contour
quad_contours, quad_corners = imageproc.contours.find_quadrilaterals(
    thresh, cv2.RETR_EXTERNAL, 0.01
)

# sudoku grid will most likely be largest contour by area, sort to find sooner
temp = list(zip(quad_contours, quad_corners))
sorted_temp = sorted(temp, key=lambda q: cv2.contourArea(q[0]), reverse=True)
quad_contours, quad_corners = list(zip(*sorted_temp))
del temp, sorted_temp

# will populate
sudoku_grid = None
candidates = []

# going to loop through all contours to see if any look like sudoku grid
for c in quad_corners:

    # getting top-down-view of potential grid
    roi_origin = imageproc.transforms.top_down_view(image.copy(), c.reshape((4, 2)))

    # preprocessing image
    _, _, roi_thresh = imageproc.utils.grey_blur_threshold(
        roi_origin, (3, 3), cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 57, 5
    )

    # contouring top-down view to find cells
    cell_contours, _ = imageproc.contours.find_quadrilaterals(
        roi_thresh, mode=cv2.RETR_LIST, error=0.02, bounds=(0.0035, 0.02)
    )

    # collecting sudoku candidate attributes
    candidates.append((roi_origin, roi_thresh, len(cell_contours), cell_contours))

    # if 81 contours are found, we assume we found the board
    if len(cell_contours) == 81:
        sudoku_grid = roi_origin.copy()
        break

# in case no grid is found
if sudoku_grid is None:
    # choosing the tuple with the most cells
    steps = max(candidates, key=lambda c: c[2])

    # plotting the various processing steps
    cv2.imshow("Region of Interest", steps[0])
    cv2.imshow("Region of Interest - Thresholded", steps[1])
    cv2.imshow(
        "Region of Interest - Contours",
        cv2.drawContours(steps[0], steps[3], -1, (0, 255, 0), 2),
    )
    cv2.waitKey()

    print("Sudoku grid not found")
    exit()


# have to know cell order to transcribe to matrix for solving
sorted_cells = imageproc.utils.sort_cells(cell_contours)

# cell centours for image annotation, boxes for cropping
cell_centers = [imageproc.contours.get_center(c) for c in sorted_cells]
cell_bboxes = [cv2.boundingRect(c) for c in sorted_cells]

# getting a list of cells and then cleaning up noise
_, cells = imageproc.utils.extract_cells(roi_thresh, cell_bboxes)
cells = [imageproc.contours.fill_contours(c, cv2.RETR_LIST, (0.0, 0.05)) for c in cells]

# loading the model
model = load_model("models/" + args.model)

# predicting cell contents with the model
digits = np.array(cells).reshape(len(cells), 28, 28, 1) / 255.0
pred_digits = model.predict(digits).argmax(axis=1)

# instantiating solver and solving
puzzle = pred_digits.reshape((9, 9))
solver = models.solver.SudokuSolver(puzzle)
solver.solve()

# displaying solution if one exists
if solver.problem.status != 1:
    print("No solution found")
    annotated = imageproc.utils.write_text(
        roi_origin, puzzle, solver.solution, cell_centers, mode="starting_values"
    )
    cv2.imshow("Thresholded", roi_thresh)
    cv2.imshow("Predicted Digits", annotated)
    cv2.waitKey()
    exit()
else:
    solved_grid = imageproc.utils.write_text(
        sudoku_grid, puzzle, solver.solution, cell_centers, mode="solution"
    )
    cv2.imshow("Original Image", image)
    cv2.imshow("Solved Puzzle", solved_grid)
    cv2.waitKey()
    exit()
