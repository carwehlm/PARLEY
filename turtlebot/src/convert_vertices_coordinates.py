import numpy as np
import sys

cell_size=float(sys.argv[1])

obst_v=np.loadtxt('obstacles_3x3_vertices.txt')

obst=(obst_v*cell_size)+0.5*cell_size

np.savez('obstacles_3x3.npz',obst)