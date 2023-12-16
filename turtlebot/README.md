# UMC controller on a Turtlebot
The Turtlebot is tasked with navigating between two points in the environment. The world is 21mx21m, which is discretised into 3mx3m cells where some cells have an obstacle present. The shortest path is calculated with Dijkstra's algorithm. The Turtlebot is considered to have failed its mission if it crashes into an obstacle or drives out of the environmnet. The Turtlebot knows its initial cell location and the commands provided by Dijkstra's algorithm, but does not use any sensors. The Turtlebot may request an update of its true position which comes at a cost. The left wheel however is fault and is only operating at 99% power, resulting in a consistent drift in both rotating and moving straight.

To setup the simulation first download this package and build in your workspace. Then export the models provided in the package:

`export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/path/to/umc_turtlebot/models`

You will need to setup the Turtlebot3 waffle (https://emanual.robotis.com/docs/en/platform/turtlebot3/simulation/) and modify it by adding a bump sensor which publishes to the topic **/tb3_gazebo/bumper**. 

To start the simulation:

`roslaunch umc_turtlebot main.launch`

This will bring up the Gazebo simulator with the Turtlebot3 and environment. To acquire probability transistions run:

`rosrun umc_turtlebot sample_traces.py`

Once you have synthesised the UMC controller you need to put the list of possible decisions into the text file **decisions.txt**, and the corresponding frequencies in the text file **umc_controller.txt**. To run the Turtlebot3 with the UMC controller:

`rosrun umc_turtlebot main.py`
