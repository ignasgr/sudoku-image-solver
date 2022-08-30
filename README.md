# Sudoku Image Solver
This project is about solving a sudoku puzzle contained in an image. The puzzle is identifed using image processing techniques, starting values are transcribed using a CNN, and solved with linear programming.
<br/>
<p align="middle">
  <img src="docs/readme_images/image12.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image12_solution.jpg" width="45%" hspace=10>
</p>

<br/>

# Current Project Status
The Sudoku Image Solver is viable under generally favorable conditions. The puzzle in the image should be flat, with the picture taken from a reasonable angle and without shadows.

## Example 1: Warped Puzzle
<br/>
<p align="middle">
  <img src="docs/readme_images/image1.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image1_contoured.jpg" width="45%" hspace=10 vspace=100>
</p>

## Example 2: Extreme Angle
<br/>
<p align="middle">
  <img src="docs/readme_images/image15.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image15_contoured.jpg" width="45%" hspace=10>
</p>

<br/>
<br/>

# To Run
The repository contains several images of sudoku puzzles and a digit recognition model to get started. Both are required parameters when running the script: 

`python sudokuimagesolver.py --image <name-of-image> --model digitnet`

The script looks for the image in `data/puzzles/` and the model in `models/` so any new images or models should be added to their respective directories. 