import numpy as np
import pulp as pulp


class SudokuSolver:
    rows = range(1, 10)
    cols = range(1, 10)
    vals = range(1, 10)

    def __init__(self, puzzle):
        self.problem = pulp.LpProblem("Sudoku", pulp.LpMinimize)
        self.variables = pulp.LpVariable.dicts(
            name="var", indices=(self.rows, self.cols, self.vals), cat="Binary"
        )
        self.puzzle = puzzle
        self.solution = None

        # constraint that each cell contains only one digit
        for r in self.rows:
            for c in self.cols:
                self.problem += (
                    pulp.lpSum([self.variables[r][c][v] for v in self.vals]) == 1
                )

        for v in self.vals:
            # constraint the each row contains unique instances of values 1-9
            for r in self.rows:
                self.problem += (
                    pulp.lpSum([self.variables[r][c][v] for c in self.cols]) == 1
                )

            # constraint the each column contains unique instances of values 1-9
            for c in self.cols:
                self.problem += (
                    pulp.lpSum([self.variables[r][c][v] for r in self.rows]) == 1
                )

        # constraint that each 3x3 section contains unique instances of values 1-9
        for r_shift in [0, 3, 6]:
            for c_shift in [0, 3, 6]:
                for v in self.vals:
                    self.problem += (
                        pulp.lpSum(
                            [
                                self.variables[r + r_shift][c + c_shift][v]
                                for r in range(1, 4)
                                for c in range(1, 4)
                            ]
                        )
                        == 1
                    )

        # constraint that we cannot change the starting values
        for r in self.rows:
            for c in self.cols:
                if self.puzzle[r - 1, c - 1] != 0:
                    self.problem += self.variables[r][c][self.puzzle[r - 1, c - 1]] == 1

    def solve(self):
        # solving
        self.problem.solve(pulp.PULP_CBC_CMD(msg=0))

        # solution attribute is 9x9 matrix representing sudoku grid
        self.solution = np.zeros((9, 9), dtype="int")

        # populating solution matrix
        for r in self.rows:
            for c in self.cols:
                for v in self.vals:
                    vars_val = pulp.value(self.variables[r][c][v])
                    if vars_val == 1:
                        self.solution[r - 1, c - 1] = v
