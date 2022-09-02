# Sudoku Image Solver
This project is about solving a sudoku puzzle contained in an image. The puzzle is identifed using fairly simple image processing techniques and heuristic rules, starting values are transcribed using a CNN, and solved with linear programming.
<br/>
<p align="middle">
  <img src="docs/readme_images/image12.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image12_solution.jpg" width="45%" hspace=10>
</p>
<br/>

# Current Project Status
The Sudoku Image Solver is viable under generally favorable conditions. The puzzle in the image should be flat, with the picture taken from a reasonable angle. The project may see some updates in the future.
<br/>
<br/>

<!-- ## Example 1: Warped Puzzle
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
<br/> -->

# To Run
The repository contains several images of sudoku puzzles and a digit recognition model to get started. Both are required parameters when running the script: 

`python sudokuimagesolver.py --image <name-of-image> --model digitnet`

The script looks for the image in `data/puzzles/` and the model in `models/` so any new images or models should be added to their respective directories.
<br/>
<br/>

# Methodology

## Identifying the Puzzle

A sudoku puzzle can be thought of as a case of nested quadrilaterals, with 81 square cells contained within a greater square that is the puzzle's outside edge. Contouring can be used to identify such shapes, and heuristic rules can help deduce which shapes belong to puzzle. 

The first phase of contouring intends to find the outer edge of the puzzle. Below, an approximation error of 5% is used for demonstration purposes. The script uses an error of 1% to reduce the number of puzzle edge candidates.

<p align="middle">
  <img src="docs/readme_images/image12.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image12_contoured1.jpg" width="45%" hspace=10>
</p>

Each candidate then undergoes a perspective transform, providing a top-down view of the contoured object. After the perspective transform is complete, the image is contoured again with the intent of finding 81 quadrilateral contours. 

<p align="middle">
  <img src="docs/readme_images/image12_pretransform.jpg" width="32%" hspace=5>
  <img src="docs/readme_images/image12_posttransform.jpg" width="32%" hspace=5>
  <img src="docs/readme_images/image12_contoured2.jpg" width="32%" hspace=5>
</p>

While the above example is fairly straight forward given the image was originally taken from a top-down view, the below example demonstrates the scripts ability to handle cases where the image is taken at an angle.

<p align="middle">
  <img src="docs/readme_images/image4_pretransform.jpg" width="45%" hspace=10>
  <img src="docs/readme_images/image4_posttransform.jpg" width="45%" hspace=10>
</p>


## Digit Recognition

## Solving the Puzzle