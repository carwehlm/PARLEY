import heapq
import math
from make_map import commands
import numpy as np

startX = 1
startY = 1
# targetX = 5
# targetY = 7
targetX=2
targetY=3

# mapSize=10
mapSize=5

updates = [1]  # cost of updates

def preamble():
    with open('model.pm', 'w') as f:
        f.write('dtmc\n')
        f.write('const int N=' + str(mapSize - 1) + ';\n')
        f.write('const int startX = ' + str(startX) + ';\n')
        f.write('const int startY = ' + str(startY) + ';\n')
        f.write('const int targetX = ' + str(targetX) + ';\n')
        f.write('const int targetY = ' + str(targetY) + ';\n')

def getVertex(N, x, y):
    return (x+y*N)

def agent(commands):
    with open('model.pm', 'a') as f:
        f.write('module Agent \n')
        f.write('  step : [0..1] init 0;\n')
        f.write('  x : [0..N] init startX;\n')
        f.write('  y : [0..N] init startY;\n')
        f.write('  direction : [0..3] init 0;\n')   ## Starting true direction (0=North, 1=East, 2=South, 3=West)
        f.write('  ax : [0..N] init startX;\n')
        f.write('  ay : [0..N] init startY;\n')
        f.write('  adirection : [0..3] init 0;\n')  ## Starting belief direction (0=North, 1=East, 2=South, 3=West)
        # f.write('  command : [0..3] init 0;\n')
        f.write('  collision : [0..1] init 0;\n')   ## Track if the agent collides with an obstacle
        f.write('  reached : [0..1] init 0;\n')     ## Track if agent has succesfully reached goal
        f.write('  out : [0..1] init 0;\n') ## If the agent leaves area and fails
        f.write('\n')

        for i in range(0, len(updates)):
            # precise update:
            f.write(
                '  [update' + str(i) + '] t=0 & step=0 & mustUpdate' + str(i) + ' -> (ax\'=x)&(ay\'=y)&(step\'=1);\n')
        f.write('  [skipUpdate] t=0 & step=0')
        for i in range(0, len(updates)):
            f.write(' & !mustUpdate' + str(i))
        f.write(' -> (step\'=1);\n')

        probs={}
        probs[0]=open('probs_north.txt','r').readlines()
        probs[1]=open('probs_east.txt','r').readlines()
        probs[2]=open('probs_south.txt','r').readlines()
        probs[3]=open('probs_west.txt','r').readlines()

        # ['north', 'east', 'west', 'south']
        dir_map=['north', 'east', 'south', 'west']
        AD=[0,1,2,3]
        D=[0,1,2,3]
        C=[0,1,2,3]

        for x in np.arange(mapSize):
            for y in np.arange(mapSize):
        # for x in np.arange(1):
        #     for y in np.arange(1):
                ## Get command for cell
                # v=getVertex(mapSize, x, y)

                ## The command the agent believes it should take
                c=int(commands.transpose()[x,y])

                ## if c==-1 then cell is obstacle; if c==5 then c is goal location
                if c>-1 and c<5:
                    suffix=str(x)+'-'+str(y)+'.npz'
                    ## New approach; each datapoint has record of collision and going outside
                    output=np.load('output/output_'+suffix)
                    data=output['arr_0']
                    # with np.printoptions(threshold=np.inf):
                    #     print(data)

                    for ax in np.arange(mapSize):
                        for ay in np.arange(mapSize):
                            ## Go through each combo (N->N, N->E,..., W->W)
                            for ad in AD:
                                for d in D:
                                    adjusted_c=(c-ad+d)%4
                                    
                                    ## Set state requirements
                                    # start='['+str(dir_map[c])+'_'+str(dir_map[ad])+'_'+str(dir_map[d])+'] (t=0) & (step=1) & (ax='+str(x)+') & (ay='+str(y)+') & (adirection='+str(ad)+') & (direction='+str(d)+') & (out=0) -> \n'
                                    start='['+str(dir_map[adjusted_c])+'] (t=0) & (step=1) & (ax='+str(ax)+') & (ay='+str(ay)+') & (adirection='+str(ad)\
                                          +') & '+'(x='+str(x)+') & (y='+str(y)+') & (direction='+str(d)+') & (out=0) & (collision=0)-> \n'
                                    f.write(start)
                                    data_total=np.sum(data[d,adjusted_c,:])
                                    for i in np.arange(72):
                                        line=probs[adjusted_c][i]
                                        p=data[d,adjusted_c,i]/data_total
                                        if p>0:
                                            f.write(str(p)+':'+line)
                                    ## Add out of area probs
                                    p=data[d][adjusted_c][72]/data_total
                                    f.write(str(p)+':(out\'=1);\n')
                elif c==5:
                    goal_x=x
                    goal_y=y

        check_correct='[check_goal] (t=0) & (ax='+str(goal_x)+') & (ay='+str(goal_y)+') & (reached=0) -> 1:(reached\'=1)&(step\'=1);\n'
        f.write(check_correct)
        check_incorrect='[check_goal] (t=0) & (ax='+str(goal_x)+') & (ay='+str(goal_y)+') & (x!='+str(goal_x)+') & (y!='+str(goal_y)+') & (reached=0) -> 1:(ax\'=x)&(ay\'=y)&(adirection\'=direction);\n'
        f.write(check_incorrect)

        f.write('endmodule \n\n')

def controller():
    with open('model.pm', 'a') as f:
        # write the decision variables
        for i in range(0, mapSize):
            for j in range(0, mapSize):
                f.write('const int decision_{0}_{1}; \n'.format(str(i), str(j)))
        f.write('module Controller \n')
        for i in range(0, len(updates)):
            f.write('  mustUpdate{0} : bool init false; \n'.format(str(i)))
        for i in range(0, mapSize):
            for j in range(0, mapSize):
                for k in range(-1, len(updates)):
                    f.write('  [decide] t = 1 & ')
                    f.write('ax = {0} & ay = {1} & decision_{0}_{1} = {2} -> '.format(str(i), str(j), str(k+1)))
                    for u in range(0, len(updates)):
                        f.write('(mustUpdate' + str(u))
                        if u==k :
                            f.write('\'=true)')
                        else :
                            f.write('\'=false)')
                        if u < len(updates) - 1:
                            f.write(' & ')
                        else:
                            f.write(';\n')
        f.write('endmodule \n\n')


def turn():
    with open('model.pm', 'a') as f:
        f.write('module Turn \n')
        f.write('  t : [0..1] init 0;\n')
        f.write('  [east] true -> (t\'=1);\n')
        f.write('  [west] true -> (t\'=1);\n')
        f.write('  [north] true -> (t\'=1);\n')
        f.write('  [south] true -> (t\'=1);\n')

        f.write('  [decide] true -> (t\'=0);\n')
        f.write('endmodule \n\n')


def rewards():
    with open('model.pm', 'a') as f:
        ## Reward for time
        f.write('rewards \"time\"\n')
        f.write('  [east] true : 1; \n')
        f.write('  [west] true : 1; \n')
        f.write('  [north] true : 1; \n')
        f.write('  [south] true : 1; \n')
        f.write('endrewards \n')

        ## Reward for energy
        f.write('rewards \"energy\"\n')
        f.write('  [check_goal] true : 5; \n')
        for u in range(0, len(updates)):
            f.write('  [update' + str(u) + '] true : ' + str(updates[u]) + ';\n')
        f.write('endrewards \n')

def main():
    commands_inst=commands(mapSize, 1.0, targetX, targetY).command_map.copy()
    # open("model.pm", "w").close()
    preamble()
    agent(commands_inst)
    controller()
    turn()
    rewards()

if __name__ == "__main__":
    main()