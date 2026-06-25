import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
import os
import csv

rng = np.random.default_rng(123)

rows = []
with open("testcsv.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        rows.append(row)
        print(row)

for i, row in enumerate(rows):
        if i > 0:
            row[1] = str(int(row[1]) + 1000)

print("")

with open("testcsv.csv", "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerows(rows)

with open("testcsv.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        rows.append(row)
        print(row)