from random import random, choice, seed
import numpy as np
import matplotlib.pyplot as plt

seed(30)

cycles = 10000

# Vertices of equilateral triangle side lenght=1
A = [0, 0]
B = [1, 0]
C = [.5, .5*np.sqrt(3)]
vertices = [A, B, C]

# Initial position
x_0 = [0.2, 0.5]
coords = [x_0]

for i in range(cycles):
    # Trow a d3
    d3 = choice(vertices)
    x_f = [(x_0[0]+d3[0])/2, (x_0[1]+d3[1])/2]
    coords.append(x_f)
    x_0 = x_f

# Get the transposed matrix to plot coordinates
vertices.append(A)
v, w = np.array(vertices).T
x, y = np.array(coords).T

fig, ax = plt.subplots()

ax.scatter(x, y, s=0.2)
ax.plot(v, w, c='red')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set(xlabel='x', ylabel='y', title='Random trajectory given a d3 roll')
# ax.grid()

# fig.savefig("test.png")
plt.show()
