import numpy as np
from scipy import optimize

f = lambda x: x * np.log(x) - 3.6e13

root = optimize.newton(f, 50)
print(root)
