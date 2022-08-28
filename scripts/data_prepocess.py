import numpy as np
import pandas as pd

N_RECORDS = 1495
N_FEATURES = 28 * 28
P = 0.20  # probability of noise pixel
BLACK_PIXEL = 255
WHITE_PIXEL = 0

# reading in data
digits = pd.read_csv("data/training/TMNIST_raw.csv").drop(columns="names")

# dropping zeros to be replaced with blank cells
digits = digits[digits["labels"] != 0]

# creating dataframe of blank cells, will be label 0
# 1 column for the label (0), rest for features
records_for_blanks = [[0] * N_RECORDS for _ in range(N_FEATURES + 1)]
data_dict = dict(zip(digits.columns.tolist(), records_for_blanks))
blank_cells = pd.DataFrame(data_dict, columns=digits.columns)

# mask that determines which pixels will be noise pixels
mask = np.random.binomial(1, P, size=(N_RECORDS, N_FEATURES)).astype(bool)
cell_values = np.where(mask, BLACK_PIXEL, WHITE_PIXEL)
cell_labels = np.zeros((N_RECORDS, 1))
noisy_cells = pd.DataFrame(
    np.concatenate((cell_labels, cell_values), axis=1), columns=digits.columns
)

# combining original data set with dummy dataset
result = pd.concat([digits, blank_cells, noisy_cells], ignore_index=True)

# writing file
result.to_csv("data/training/TMNIST_processed.csv", index=False)
