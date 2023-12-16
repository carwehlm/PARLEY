#!/usr/bin/env python3
import numpy as np
import rospy
import os
import sys
# import roslib; roslib.load_manifest('gazebo')
import time
import shutil

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

        ## Define agent's velocities
        self.vel_linear=0.15 # m/s
        self.vel_angular=0.15 # rads/s
        self.vel=Twist()

        ## Call custom classes
        ##   Setup Gazebo tools
        self.gu=GU()

        self.cell_size=3

        # self.N=10
        self.N=7

        self.theta=0

        ## Publishers
        self.vel_pub=rospy.Publisher("/cmd_vel", Twist,queue_size=1)
        rospy.sleep(2)
        self.stop()
        self.gu.smsClient('turtlebot3_waffle_pi', [0.5,0.5,0],np.pi/2)

        ## End positions don't matter, just here to get map
        # self.commands_map=commands(self.N, self.cell_size, 5, 7)
        self.commands_map=commands(self.N, self.cell_size, 2, 4)
        self.wheel_manlfunction=0.99
        self.sampleMoves()

    def sampleMoves(self):
        trials=100e3

        ##obst=np.loadtxt('src/umc_turtlebot/src/obstacles_2x2.txt')
        obst=np.load('src/umc_turtlebot/src/obstacles_3x3.npz')['arr_0']

        cell_occ=[]

        for o in obst:
            cell=self.getCellPos(o[0],o[1])
            cell_occ.append(cell)

        XY=[]
        path_transitions='src/umc_turtlebot/model_generator/output/output_'

        for x in np.arange(self.N):
            for y in np.arange(self.N):
                fail=0
                for o in cell_occ:
                    if x==o[0] and y==o[1]:
                        fail=1
                        break
                if not fail:
                    XY.append([x,y])
                    ## TODO check if file already exists and then append new data to it
                    np_file=path_transitions+str(x)+'-'+str(y)+'.npz'
                    if not os.path.exists(np_file):
                        np.savez(np_file, np.zeros([4,4,73]))
                    else:
                        print(np_file + " already exists")
        print(XY)
        angles=np.array([[0.25*np.pi, 0.75*np.pi],[-0.25*np.pi, 0.25*np.pi],[-0.75*np.pi, -0.25*np.pi], [-1.25*np.pi, -0.75*np.pi]])


        transitions_count={}
        for xy in XY:
            transitions_count[(xy[0],xy[1])]=np.ones([4,4])

        for t in np.arange(trials):
            print('Trial ',t)
            mid_diff=self.cell_size/2.0
            # pos_noise=np.random.uniform(-mid_diff/2.0,mid_diff/2.0,2)
            pos_noise=0.0
            rand_ind=np.random.randint(0,len(XY))
            start_pos=pos_noise+np.array([self.cell_size*XY[rand_ind][0]+mid_diff,self.cell_size*XY[rand_ind][1]+mid_diff])
            ##start_theta=np.random.uniform(angles[initial_dir,0],angles[initial_dir,1],1)
            rand_ind=np.random.randint(0,len(angles))
            start_theta=np.array([np.sum(angles[rand_ind,:])/2.0])
            self.gu.smsClient('turtlebot3_waffle_pi', [start_pos[0], start_pos[1],0], start_theta[0])

            damaged=0

            rospy.sleep(5)
            self.gu.collision=False

            while not damaged:
                pose=self.gu.gms_client('turtlebot3_waffle_pi','')
                start_x_cell, start_y_cell=self.getCellPos(pose.pose.position.x, pose.pose.position.y)
                (_, _, start_z_theta) = euler_from_quaternion ([pose.pose.orientation.x,pose.pose.orientation.y,pose.pose.orientation.z,pose.pose.orientation.w])
                initial_dir=self.getThetaDir(start_z_theta)
                self.theta=initial_dir
                outcome=np.load(path_transitions+str(start_x_cell)+'-'+str(start_y_cell)+'.npz')['arr_0']

                ## Sample with highest probability the least taken combination
                transitions_probs=transitions_count[(start_x_cell,start_y_cell)][initial_dir,:].copy()
                command=np.argmin(transitions_probs)
                ## Move robot
                command=np.random.randint(0,4)
                self.move(command)
                transitions_count[(start_x_cell,start_y_cell)][initial_dir,command]+=1
                ## Record transition
                pose=self.gu.gms_client('turtlebot3_waffle_pi','')
                x_cell, y_cell=self.getCellPos(pose.pose.position.x, pose.pose.position.y)
                (_, _, z_theta) = euler_from_quaternion ([pose.pose.orientation.x,pose.pose.orientation.y,pose.pose.orientation.z,pose.pose.orientation.w])
                theta_dir=self.getThetaDir(z_theta)
                if x_cell<0 or x_cell>self.N-1 or y_cell<0 or y_cell>self.N-1:
                    #outside_count[initial_dir, command]+=1
                    outcome[initial_dir, command, 72]+=1
                    damaged=1
                else:
                    x_change=-1
                    y_change=-1
                    if x_cell==start_x_cell-1:
                        x_change=0
                    elif x_cell==start_x_cell:
                        x_change=3
                    elif x_cell==start_x_cell+1:
                        x_change=6

                    if y_cell==start_y_cell-1:
                        y_change=0
                    elif y_cell==start_y_cell:
                        y_change=1
                    elif y_cell==start_y_cell+1:
                        y_change=2

                    pos_change=x_change+y_change
                    ## get index
                    collision_val=0
                    if self.gu.collision==True:
                        collision_val=1
                        damaged=1
                        print("BUMPED!")
                        self.gu.collision=False

                    state_index=(pos_change)*8+theta_dir*2+collision_val
                    
                    outcome[initial_dir,command,state_index]+=1
                np.savez(path_transitions+str(start_x_cell)+'-'+str(start_y_cell)+'.npz',outcome)

    def getThetaDir(self, theta):
        theta_dir=-1
        if theta>0.25*np.pi and theta<0.75*np.pi:
            theta_dir=0
        elif theta>-0.25*np.pi and theta<0.25*np.pi:
            theta_dir=1
        elif theta>-0.75*np.pi and theta<-0.25*np.pi:
            theta_dir=2
        elif theta>0.75*np.pi or theta<-0.75*np.pi:
            theta_dir=3
        return theta_dir

    def stop(self):
        self.vel.linear.x=0
        self.vel.angular.z=0
        self.vel_pub.publish(self.vel)

    def move(self, command):
        ## Check if facing right direction
        ##   Rotate if required
        # print(self.theta, command)
        #print(self.theta==command)
        if not self.theta==command:
            change=1-self.theta
            rotate=int(np.abs((command+change)%4))
            # print("Rotating!")
            self.rotate(rotate)
            # print("Finished rotating!")
        ## Move in direction
        self.forward()
    
    def forward(self):
        time_to_drive=self.cell_size/self.vel_linear
        vr=self.vel_linear
        vl=self.wheel_manlfunction*vr
        self.vel.linear.x=(vr+vl)/2
        ##self.vel.linear.x=self.vel_linear

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
        # print(time_to_rotate)
        wheel_dist=0.287
        vr=(self.vel_angular*np.sign(angles[rotate]))*wheel_dist/2.0
        vl=-1.0*self.wheel_manlfunction*vr

        #angular=vr-vl
        angular=(vr-vl)/wheel_dist
        self.vel.angular.z=angular

        ## Now include linear drift due to wheel defect
        self.vel.linear.x=(vr+vl)/2
        ##self.vel.angular.z=self.vel_angular*np.sign(angles[rotate])
        #print(self.vel)
        self.vel_pub.publish(self.vel)
        rospy.sleep(time_to_rotate)
        #print("Moving!")
        self.vel.angular.z=0
        self.vel_pub.publish(self.vel)

    ## Convert continuous postion to cell position
    def getCellPos(self, x, y):
        if x>0:
            x_cell=int(x/self.cell_size)
        else:
            x_cell=int(np.floor(x/self.cell_size))
        if y>0:
            y_cell=int(y/self.cell_size)
        else:
            y_cell=int(np.floor(y/self.cell_size))
        return [x_cell, y_cell]

    def start(self):
        while not rospy.is_shutdown():
            self.loop_rate.sleep()

if __name__=='__main__':
    rospy.init_node("robot", anonymous=True)
    ## Need to make this input argument
    _intensity=1.0
    robot=Robot()
    robot.start()