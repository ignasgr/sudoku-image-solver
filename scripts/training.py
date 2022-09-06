import argparse

import pandas as pd
from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    InputLayer,
    MaxPooling2D,
)
from tensorflow.keras.utils import to_categorical

parser = argparse.ArgumentParser()
parser.add_argument("--name", "-n", help="Name of saved model.", required=True)
args = parser.parse_args()

# constants
N_CLASSES = 10
INPUT_SHAPE = (28, 28, 1)
BATCH_SIZE = 128
EPOCHS = 15

# reading in data
digits = pd.read_csv("data/training/TMNIST_processed.csv")

# splitting data into train and test
train = digits.sample(frac=0.8, random_state=0)
test = digits.drop(train.index)

# only the last 784 columns pertain to pixel values
x_train = train.iloc[:, 1:].to_numpy()
y_train = train.iloc[:, 0].to_numpy()
x_test = test.iloc[:, 1:].to_numpy()
y_test = test.iloc[:, 0].to_numpy()

# rescaling values
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

# making sure images have correct shape
x_train = x_train.reshape((x_train.shape[0], 28, 28, 1))
x_test = x_test.reshape((x_test.shape[0], 28, 28, 1))

# converting target variables to arrays
y_train = to_categorical(y_train, N_CLASSES)
y_test = to_categorical(y_test, N_CLASSES)

# building the model
model = Sequential(
    [
        InputLayer(input_shape=INPUT_SHAPE),
        Conv2D(filters=32, kernel_size=(3, 3), activation="relu"),
        MaxPooling2D(),
        Conv2D(filters=64, kernel_size=(3, 3), activation="relu"),
        MaxPooling2D(),
        Flatten(),
        Dropout(rate=0.5),
        Dense(units=N_CLASSES, activation="softmax"),
    ]
)

# fitting the model
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_split=0.3)

# evaluating the model
score = model.evaluate(x_test, y_test, verbose=0)
print("Test Accuracy:", score[1])

model.save("models/" + args.name)
