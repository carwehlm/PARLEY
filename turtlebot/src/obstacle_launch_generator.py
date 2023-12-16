import numpy as np

##obstacles=np.loadtxt('obstacles.txt')
# obstacles=np.loadtxt('obstacles_2x2.txt')
# obstacles=np.loadtxt('obstacles_3x3.txt')
obstacles=np.load('obstacles_3x3.npz')['arr_0']
print(obstacles)

box_string='box_3x3'

output='<launch>\n\n    <!-- Box spawn -->\n    <!-- Template -->\n    <!-- <node name="spawn_obstacle_0" pkg="gazebo_ros" type="spawn_model" respawn="false" output="screen" args="-sdf -file $(find umc_turtlebot)/models/'+box_string+'/model.sdf -model box_0 -x 0.0 -y 0.0 -z 0.0"/> -->\n\n'
#for obstacle in obstacles:
count=0
for obstacle in obstacles:
	output+='    <node name="spawn_obstacle_'+str(count)+'" pkg="gazebo_ros" type="spawn_model" respawn="false" output="screen" args="-sdf -file $(find umc_turtlebot)/models/'+box_string+'/model.sdf -model box_'+str(count)+' -x '+str(obstacle[0])+' -y '+str(obstacle[1])+' -z 0.0"/>\n\n'
	count+=1

output+='</launch>'
outfile=open('../launch/spawn_obstacles.launch','w')
outfile.write(output)