import numpy as np
import os
import rospy
import geometry_msgs.msg
from gazebo_msgs.srv import GetModelState
from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.srv import SetLightProperties
from gazebo_msgs.msg import ContactsState
from std_srvs.srv import Empty

class GazeboUtils(object):
    def __init__(self):
        ## Ros service for clearing cost maps
        self.clear_maps=rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
        ## Ros service for getting model states
        self.model_coordinates=rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)

        self.init_pose=rospy.Publisher("/initialpose",geometry_msgs.msg.PoseWithCovarianceStamped, queue_size=1)

        self.collision_detector=rospy.Subscriber('/tb3_gazebo_bumper', ContactsState, self.collisionDetector, queue_size=1)

        self.collision=False
        print('Gazebo utilities setup completed')


    def collisionDetector(self, data):
        if len(data.states)>0:
            for state in data.states:
                if 'box' in state.collision1_name or 'box' in state.collision2_name:
                    self.collision=True
                    return

    def gms_client(self,model_name,relative_entity_name):
        rospy.wait_for_service('/gazebo/get_model_state')
        try:
            gms = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp1 = gms(model_name,relative_entity_name)
            return resp1
        except rospy.ServiceException as e:
            print("Service call failed: %s"%e)

    def smsClient(self, model_name, pos, euler):
        state_msg = ModelState()
        state_msg.model_name = model_name
        state_msg.pose.position.x = pos[0]
        state_msg.pose.position.y = pos[1]
        state_msg.pose.position.z = pos[2]
        state_msg.pose.orientation.x = 0
        state_msg.pose.orientation.y = 0
        state_msg.pose.orientation.z = np.sin(euler/2.0)
        state_msg.pose.orientation.w = np.cos(euler/2.0)

        rospy.wait_for_service('/gazebo/set_model_state')
        try:
            set_state = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
            resp = set_state( state_msg )

        except rospy.ServiceException as e:
            print("Service call failed: %s" % e)

    def resetWorld(self):
        print("Resetting world!")
        self.clear_maps()
        ## Set robot's position
        self.smsClient('robot', [4, 3, 0.0],-1.57)
        rospy.sleep(5)
        pos_robot=self.gms_client("robot", "").pose.position
        ont_robot=self.gms_client("robot","").pose.orientation
        self.setInitialPose([pos_robot.x,pos_robot.y,pos_robot.z],[ont_robot.z,ont_robot.w])
        ##rospy.sleep(3)
        self.found=0
        self.clear_maps()

        ## Set box's position
        # pos=np.random.rand(2)*3.5
        pos=np.array([0.0,0.0,0.0])
        pos[0]=np.random.rand()*4.0
        pos[1]=np.random.rand()*3.0-3
        orientation=(1-2*np.random.rand())*np.pi/8
        self.smsClient('qr_box', pos, orientation)

        ## Place object ontop of box (orientation does not matter)
        pos[2]=0.26 # height of box plus half height of object
        self.smsClient('object', pos, 0)

    def setInitialPose(self, pos, orientation):
        pose = geometry_msgs.msg.PoseWithCovarianceStamped()
        pose.header.frame_id = "map"
        pose.pose.pose.position.x=pos[0]
        pose.pose.pose.position.y=pos[1]
        pose.pose.pose.position.z=pos[2]
        pose.pose.covariance=[0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.06853891945200942]
        pose.pose.pose.orientation.z=orientation[0]
        pose.pose.pose.orientation.w=orientation[1]
        # rospy.loginfo(pose)
        # rospy.spin()
        # rospy.loginfo(pose)
        # self.loop_rate.sleep()
        self.init_pose.publish(pose)

    def setLightValue(self, light_name, intensity):
        command="rosservice call /gazebo/set_light_properties \"light_name: \'"+light_name+"\'\ndiffuse: {r: "+str(intensity)+", g: "+str(intensity)+", b: "+str(intensity)+", a: 0.0}\"" 
        os.system(command)