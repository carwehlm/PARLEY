#!/usr/bin/env python3
import numpy as np
import rospy
import os
# import roslib; roslib.load_manifest('gazebo')
import time

from std_srvs.srv import Empty
from std_msgs.msg import String
from std_msgs.msg import Float64MultiArray
from std_msgs.msg import Int8
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from gazebo_msgs.srv import GetModelState
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
import geometry_msgs.msg
from tf.transformations import euler_from_quaternion, quaternion_from_euler

from math import pi

## Custom classes
from gazebo_utils import GazeboUtils as GU
from umc import UMC
from make_map import commands

import sys
import os

class Robot(object):
    def __init__(self):
        self.loop_rate = rospy.Rate(1)

        ## Initialise agent's pose beliefs
        x_start=1
        y_start=0

        self.x_belief=x_start
        self.y_belief=y_start

        ## 0=North, 1=East, 2=South, 3=West
        self.theta=0

        ## Intialise running costs
        self.total_cost=0.0
        self.u_cost=5.0

        ## Define cell to reach
        self.x_goal=3
        self.y_goal=5

        ## Define agent's velocities
        self.vel_linear=0.2 # m/s
        self.vel_angular=0.1 # rads/s
        self.vel=Twist()

        ## Fault wheel
        self.wheel_manlfunction=0.99

        ## Call custom classes
        ##   Setup Gazebo tools
        self.gu=GU()
        ##   Setup UMC values
        umc={}
        f=open('src/umc_turtlebot/src/decisions.txt','r+')
        f_lines=f.readlines()
        frequencies=np.loadtxt('src/umc_turtlebot/src/umc_controller.txt')
        self.umc=np.zeros([7,7,4])
        for line_ind in np.arange(len(f_lines)):
            text=f_lines[line_ind][9:]
            ind_x=int(text[0])
            ind_y=int(text[2])
            ind_theta=int(text[4])
            self.umc[ind_x,ind_y,ind_theta]=frequencies[line_ind]

        ##   Positions in metres (each cell is 3mx3m)
        self.cell_size=3

        self.N=7
        self.commands=commands(self.N, self.cell_size, self.x_goal, self.y_goal)

        ## Publishers
        self.vel_pub=rospy.Publisher("/cmd_vel", Twist,queue_size=1)
        rospy.sleep(2)
        self.stop()
        mid_diff=self.cell_size/2.0
        # start_pos=np.array([self.cell_size*XY[rand_ind][0]+mid_diff,self.cell_size*XY[rand_ind][1]+mid_diff])
        self.gu.smsClient('turtlebot3_waffle_pi', [self.cell_size*x_start+mid_diff,self.cell_size*y_start+mid_diff,0],np.pi/2)
        self.update_count=0
        self.travel()

    def resetRobot(self):
        x_start=1
        y_start=0
        self.x_belief=x_start
        self.y_belief=y_start
        self.theta=0
        rospy.sleep(2)
        self.stop()
        mid_diff=self.cell_size/2.0
        # start_pos=np.array([self.cell_size*XY[rand_ind][0]+mid_diff,self.cell_size*XY[rand_ind][1]+mid_diff])
        self.gu.smsClient('turtlebot3_waffle_pi', [self.cell_size*x_start+mid_diff,self.cell_size*y_start+mid_diff,0],np.pi/2)

    def stop(self):
        self.vel.linear.x=0
        self.vel.angular.z=0
        self.vel_pub.publish(self.vel)

    def checkOut(self):
        pose=self.gu.gms_client('turtlebot3_waffle_pi','')
        x_cell, y_cell=self.getCellPos(pose.pose.position.x, pose.pose.position.y)
        if x_cell<0 or x_cell>self.N-1 or y_cell<0 or y_cell>self.N-1:
            return True
        else:
            return False

    def travel(self):
        reached=0
        out=False
        self.gu.collision=False
        while not (reached or self.gu.collision or out):
            while not (self.reachedGoal() or self.gu.collision or out):
                ## Check if updating
                if self.update_count>=self.umc[self.x_belief,self.y_belief,self.theta]:
                    ## position updated
                    print("Requesting update!\n")
                    self.U1()
                    self.update_count=0
                else:
                    self.update_count+=1
                v=self.x_belief+self.y_belief*self.N
                command=self.commands.commands[v]
                self.move(command)
                self.total_cost+=1

                if command==0:
                    self.y_belief=self.y_belief+1
                elif command==1:
                    self.x_belief=self.x_belief+1
                elif command==2:
                    self.y_belief=self.y_belief-1
                elif command==3:
                    self.x_belief=self.x_belief-1
                self.theta=command

                out=self.checkOut()
            ## Once the robot believes it has reached the goal location should it check to confirm?
            self.U1()
            if self.reachedGoal():
                self.stop()
                reached=1
                print("Success!")
        if self.gu.collision:
            print("Turtlebot has crashed!\n")
            self.resetRobot()
            self.travel()
        elif out:
            print("Turtlebot has left mission area!\n")
            self.resetRobot()
            self.travel()
        else:
            print("Energy used: "+str(self.total_cost)+'\n')

    def reachedGoal(self):
        if (self.x_belief==self.x_goal and self.y_belief==self.y_goal):
            return True
        else:
            return False

    def move(self, command):
        ##   Rotate if required
        if not self.theta==command:
            change=1-self.theta
            rotate=int(np.abs((command+change)%4))
            self.rotate(rotate)
        ## Move in direction
        self.forward()
    
    def forward(self):
        time_to_drive=self.cell_size/self.vel_linear
        vr=self.vel_linear
        vl=self.wheel_manlfunction*vr
        self.vel.linear.x=(vr+vl)/2

        ## Now include rotational drift due to wheel defect
        wheel_dist=0.287
        angular=(vr-vl)/wheel_dist
        self.vel.angular.z=angular

        self.vel_pub.publish(self.vel)
        rospy.sleep(time_to_drive)

        self.vel.linear.x=0
        self.vel_pub.publish(self.vel)
        rospy.sleep(1)

    def rotate(self, rotate):
        angles=[np.pi/2.0,0,-np.pi/2.0,np.pi]
        time_to_rotate=np.abs(angles[rotate]/self.vel_angular)
        wheel_dist=0.287
        vr=(self.vel_angular*np.sign(angles[rotate]))*wheel_dist/2.0
        vl=-1.0*self.wheel_manlfunction*vr

        angular=(vr-vl)/wheel_dist
        self.vel.angular.z=angular

        ## Now include linear drift due to wheel defect
        self.vel.linear.x=(vr+vl)/2
        self.vel_pub.publish(self.vel)
        rospy.sleep(time_to_rotate)
        self.vel.angular.z=0
        self.vel_pub.publish(self.vel)

    ## Convert continuous postion to cell position
    def getCellPos(self, x, y):
        x_cell=int(x/self.cell_size)
        y_cell=int(y/self.cell_size)
        return [x_cell, y_cell]

    ## Update direction with new continuous angle
    def updateTheta(self,angle):
        if angle>np.pi/4 and angle<3*np.pi/4:
            self.theta=0
        elif angle<np.pi/4 and angle>-np.pi/4:
            self.theta=1
        elif angle<-np.pi/4 and angle>-3*np.pi/4:
            self.theta=2
        else:
            self.theta=3

    ## Uses GPS to update belief
    ## Question: How best to fix position? Agent move to centre of current cell? Stay where it is?
    def U1(self):
        pose=self.gu.gms_client('turtlebot3_waffle_pi','')
        x=pose.pose.position.x
        y=pose.pose.position.y
        pos=self.getCellPos(x,y)
        self.x_belief=pos[0]
        self.y_belief=pos[1]

        self.updateTheta(2*np.arcsin(pose.pose.orientation.z))

        self.total_cost=self.total_cost+self.u_cost

    def start(self):
        while not rospy.is_shutdown():
            self.loop_rate.sleep()

if __name__=='__main__':
    rospy.init_node("robot", anonymous=True)
    ## Need to make this input argument
    _intensity=1.0
    robot=Robot()
    robot.start()