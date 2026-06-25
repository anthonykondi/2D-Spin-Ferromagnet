import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
import os

rng = np.random.default_rng(123)

with open("./images/.image_count.txt", "r") as file:
    content = file.read()
    print("before:", content)

count = 0
with open("./images/.image_count.txt", "r") as file:
    content = file.read()
    count = int(content)

count += 1
with open("./images/.image_count.txt", "w") as file:
    file.write(str(count))

with open("./images/.image_count.txt", "r") as file:
    content = file.read()
    print("after:", content)