import numpy as np
import sys 

class commands(object):
  def __init__(self, N, cell_size, goal_x, goal_y):
    print('making maps')
    self.world=np.zeros((N,N,2))
    self.world[:,:,1]=-1

    self.cell_size=cell_size

    vertices=N*N
    count=0
    for y in np.arange(N):
        for x in np.arange(N):
            self.world[x,y,0]=count
            count+=1

    self.obstacles_pos=np.loadtxt('obstacles.txt')
    self.obstacles_vertices=[]
    for o in self.obstacles_pos:
      o_cell_pos=self.getCellPos(o[0],o[1])
      self.obstacles_vertices.append(self.getVertex(o_cell_pos[0],o_cell_pos[1], N))

    # print(self.obstacles_vertices)

    ## Dictionary for adjacency matrix
    self.adjacency_dict={}
    for v in np.arange(vertices):
      if not self.checkObstacles(v):
        val={}
        if v+N<vertices and not self.checkObstacles(v+N):
            val[v+N]=1
        if v-N>0 and not self.checkObstacles(v-N):
            val[v-N]=1          
        if v%N+1<N and not self.checkObstacles(v+1):
            val[v+1]=1
        if v%N-1>-1 and not self.checkObstacles(v-1):
            val[v-1]=1
        self.adjacency_dict[v]=val

    target=self.getVertex(goal_x, goal_y, N)
    self.commands=self.dijkstra(N,target, self.adjacency_dict)
    self.commands[self.getVertex(goal_x,goal_y, N)]=5
    self.command_map=np.zeros([N,N])-1

    for v in self.commands.keys():
      self.command_map[int(v/N)][v%N]=self.commands[v]
    # print(self.command_map)
    # print(np.flip(self.command_map,0))

  def checkObstacles(self, vertex):
    if vertex in self.obstacles_vertices:
      return True
    else:
      return False

  def minDistance(self, dist_dict, searched_dict, vertices):
        # Initialize minimum distance for next node
        min=1e7
        # Search not nearest vertex not in the
        # shortest path tree
        # min_index=-1
        for v in vertices:
            if dist_dict[v]<min and searched_dict[v]==False:
                min=dist_dict[v]
                min_index=v
        return min_index

  def dijkstra(self, N, end, adjacency_dict):
    vertices=adjacency_dict.keys()

    dist_dict={}
    searched_dict={}
    for v in vertices:
      dist_dict[v]=1e7
      searched_dict[v]=False

    dist_dict[end]=0

    # dist=[1e7]*vertices
    # dist[end]=0
    # searched=[False]*len(adjacency_mat)

    # searched

    # directions=np.zeros(vertices)-1

    directions={}

    for cout in vertices:
        # Pick the minimum distance vertex from
        # the set of vertices not yet processed.
        # u is always equal to src in first iteration
        # print(cout, self.checkObstacles(cout))

        # u=self.minDistance(dist, searched, vertices)
        u=self.minDistance(dist_dict, searched_dict, vertices)
        # print(u)
        # Put the minimum distance vertex in the
        # shortest path tree
        searched_dict[u]=True

        # Update dist value of the adjacent vertices
        # of the picked vertex only if the current
        # distance is greater than new distance and
        # the vertex in not in the shortest path tree
        for v in vertices:
          if (v in adjacency_dict[u] and searched_dict[v]==False and dist_dict[v]>(dist_dict[u]+adjacency_dict[u][v])):
            dist_dict[v]=dist_dict[u]+adjacency_dict[u][v]
            if v==u-N:
              directions[v]=0
            elif v==u-1:
              directions[v]=1
            elif v==u+N:
              directions[v]=2
            elif v==u+1:
              directions[v]=3
    return directions

  def getNeighbours(self, x, y):
    # v=self.getVertex(x,y)
    N=len(self.command_map)
    neighbours=''
    for xx in (x-1,x,x+1):
      for yy in (y-1,y,y+1):
        if xx<0 or xx>N-1 or yy<0 or yy>N-1:
          neighbours+='-1'
        elif self.command_map[yy,xx]>-1:
          neighbours+='1'
        else:
          neighbours+='0'
    return neighbours

  ## Convert continuous (x,y) postion to cell position
  def getCellPos(self, x, y):
      x_cell=int(x/self.cell_size)
      y_cell=int(y/self.cell_size)
      return [x_cell, y_cell]  

  ## Get vertex from discrete (x,y) cell position
  def getVertex(self, x, y, N):
    return (x+y*N)


# test=commands(5,4,4)
# print(test.commands)