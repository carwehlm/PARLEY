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

        self.cell_size=1

        # self.N=10
        self.N=5

        self.theta=0

        ## Publishers
        self.vel_pub=rospy.Publisher("/cmd_vel", Twist,queue_size=1)
        rospy.sleep(2)
        self.stop()
        self.gu.smsClient('turtlebot3_waffle_pi', [0.5,0.5,0],np.pi/2)

        ## End positions don't matter, just here to get map
        # self.commands_map=commands(self.N, self.cell_size, 5, 7)
        self.commands_map=commands(self.N, self.cell_size, 2, 3)

        self.sampleMoves()

    def sampleMoves(self):
        trials=1

        obst=np.loadtxt('src/umc_turtlebot/src/obstacles.txt')

        cell_occ=[]

        for o in obst:
            cell=self.getCellPos(o[0],o[1])
            cell_occ.append(cell)

        XY=[]

        for x in np.arange(self.N):
            for y in np.arange(self.N):
                fail=0
                for o in cell_occ:
                    if x==o[0] and y==o[1]:
                        fail=1
                        break
                if not fail:
                    XY.append([x,y])

        angles=np.array([[0.25*np.pi, 0.75*np.pi],[-0.25*np.pi, 0.25*np.pi],[-0.75*np.pi, -0.25*np.pi], [-1.25*np.pi, -0.75*np.pi]])
        total=0

        similar_neighbours={}

        path_transitions='src/umc_turtlebot/model_generator/output/output_'
        # path_outside='output/output_outside_'
        # path_collisions='output/output_collision_'

        for xy in XY:
            neighbours=self.commands_map.getNeighbours(xy[0],xy[1])
            # print(neighbours)
            if neighbours in similar_neighbours.keys():
                oldfile=path_transitions+similar_neighbours[neighbours]+'.npz'
                newfile=path_transitions+str(xy[0])+'-'+str(xy[1])+'.npz'
                shutil.copyfile(oldfile, newfile)

                # oldfile=path_outside+similar_neighbours[neighbours]+'.npz'
                # newfile=path_outside+str(xy[0])+'-'+str(xy[1])+'.npz'
                # shutil.copyfile(oldfile, newfile)

                # oldfile=path_collisions+similar_neighbours[neighbours]+'.npz'
                # newfile=path_collisions+str(xy[0])+'-'+str(xy[1])+'.npz'
                # shutil.copyfile(oldfile, newfile)
            else:
                start=time.time()
                ## (initial direction, command, state change)
                outcome=np.zeros([4, 4, 73])

                for initial_dir in np.arange(len(angles)):
                    self.theta=initial_dir
                    for command in np.arange(4):
                        for t in np.arange(trials):
                            ## Initialise 
                            mid_diff=self.cell_size/2.0
                            # mid_diff=0.0/2.0
                            # pos_noise=np.random.uniform(-mid_diff/2.0,mid_diff/2.0,2)
                            pos_noise=0.0
                            start_pos=pos_noise+np.array([xy[0]+mid_diff,xy[1]+mid_diff])
                            ##start_theta=np.random.uniform(angles[initial_dir,0],angles[initial_dir,1],1)
                            start_theta=np.array([np.sum(angles[initial_dir,:])/2.0])
                            self.gu.smsClient('turtlebot3_waffle_pi', [start_pos[0], start_pos[1],0], start_theta[0])

                            ## Execute command
                            self.move(command)

                            ## Record transition
                            pose=self.gu.gms_client('turtlebot3_waffle_pi','')
                            x_cell, y_cell=self.getCellPos(pose.pose.position.x, pose.pose.position.y)
                            ##orientation_list = [pose.orientation.x, orientation_q.y, orientation_q.z, orientation_q.w]
                            (_, _, z_theta) = euler_from_quaternion ([pose.pose.orientation.x,pose.pose.orientation.y,pose.pose.orientation.z,pose.pose.orientation.w])
                            ##print(z_theta, 2*np.arcsin(pose.pose.orientation.z))
                            theta_dir=self.getThetaDir(z_theta)
                            if x_cell<0 or x_cell>self.N-1 or y_cell<0 or y_cell>self.N-1:
                                #outside_count[initial_dir, command]+=1
                                outcome[initial_dir, command, 72]+=1
                            else:
                                x_change=-1
                                y_change=-1
                                if x_cell==xy[0]-1:
                                    x_change=0
                                elif x_cell==xy[0]:
                                    x_change=3
                                elif x_cell==xy[0]+1:
                                    x_change=6

                                if y_cell==xy[1]-1:
                                    y_change=0
                                elif y_cell==xy[1]:
                                    y_change=1
                                elif y_cell==xy[1]+1:
                                    y_change=2

                                pos_change=x_change+y_change
                                ## get index
                                collision_val=0
                                if self.gu.collision==True:
                                    collision_val=1
                                    self.gu.collsion=False

                                state_index=(pos_change)*8+theta_dir*2+collision_val
                                
                                outcome[initial_dir,command,state_index]+=1
                            total+=1

                            ## Record collision
                            # if self.gu.collision==True:
                                # collision_count[initial_dir, command]+=1
                                # self.gu.collsion=False
                end=time.time()
                print("Time to complete cell: ", end-start)
                np.savez(path_transitions+str(xy[0])+'-'+str(xy[1])+'.npz',outcome)
                # np.savez(path_collisions+str(xy[0])+'-'+str(xy[1])+'.npz',collision_count)
                # np.savez(path_outside+str(xy[0])+'-'+str(xy[1])+'.npz',outside_count)
                similar_neighbours[neighbours]=str(xy[0])+'-'+str(xy[1])

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
        self.vel.linear.x=self.vel_linear
        self.vel_pub.publish(self.vel)
        rospy.sleep(time_to_drive)

        self.vel.linear.x=0
        self.vel_pub.publish(self.vel)
        rospy.sleep(1)

    def rotate(self, rotate):
        angles=[np.pi/2.0,0,-np.pi/2.0,np.pi]
        time_to_rotate=np.abs(angles[rotate]/self.vel_angular)
        # print(time_to_rotate)

        self.vel.angular.z=self.vel_angular*np.sign(angles[rotate])
        # print(self.vel)
        self.vel_pub.publish(self.vel)
        rospy.sleep(time_to_rotate)
        # print("Moving!")
        self.vel.angular.z=0
        self.vel_pub.publish(self.vel)

    ## Convert continuous postion to cell position
    def getCellPos(self, x, y):
        x_cell=int(x/self.cell_size)
        y_cell=int(y/self.cell_size)
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