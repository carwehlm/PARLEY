import numpy as np

class UMC(object):
	def __init__(self, N, map_commands_file, map_updates_file):
		## Read in controller (map commands and updates)
		map_commands=np.loadtxt(map_commands_file)
		map_updates=np.loadtxt(map_updates_file)

		## NxNx2 matrix with each element containing a command and update request
		## For command: 0=North, 1=East, 2=South, 3=West
		## For update request: 0=no update, 1='GPS', 2=human intervention 
		self.map=np.zeros((N,N,2))
		self.map[:,:,0]=map_commands
		self.map[:,:,1]=map_updates