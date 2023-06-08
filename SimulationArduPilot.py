from dronekit import connect,VehicleMode,LocationGlobalRelative
import time
from pymavlink import mavutil

class SITL:


    def Simulate(self,positions,airspeed,altitude):
        connection_string = 'tcp:127.0.0.1:5763'
        print("POS: ",positions)
        print("AIRSPEED: ",airspeed, "km/h")
        """ Port3 on TCP. Before running program ensure that Ardupilot is connected to TCP (selecting vehicle from SIMULATION window)
        If AttributeError: module 'collections' has no attribute 'MutableMapping' Error appear. Read TXT and follow steps
        Be sure to have in DATA->Actions: Mission. Wait until it starts by itself"""
        self.vehicle = connect(connection_string, wait_ready=False, baud=115200)
        print("Connecting...")
        self.vehicle.wait_ready(True, timeout=300)  # Had to change timeout to avoid issue
        print("Connected")

        input("Press Enter to continue...")
        self.arm_and_takeoff(altitude)  # Call take-off function

        aispeed_conv=airspeed*(1000/3600) #Conversion from km/h to m/s
        self.vehicle.airspeed = aispeed_conv  # Set airspeed (in m/s)
        print("AIRSPEED: ", airspeed, "m/s")

        #Procced to the flight
        for pos in positions:
            print("FLYING TO NEXT TOWER: ", pos)
            point = LocationGlobalRelative(float(pos[1][0]), float(pos[1][1]), altitude)
            #print("Point ", point)
            self.vehicle.simple_goto(point)  # Instruction to move to a point
            arrived = False
            previousPosition = self.vehicle.location.global_relative_frame
            time.sleep(1)
            while not arrived:
                arrived = self.compare_location(previousPosition,self.vehicle.location.global_relative_frame)  # Call compare_location to know if UAV has arrived to wp
                previousPosition = self.vehicle.location.global_frame
                time.sleep(0.3)
           #Arrived. Turn on the camera
            print("POSITION REACHED")
            if pos[0]=="T":
                #The point has a tower to inspect. Need rotation sequence
                relative = True #Rotate relative to UAVs heading (True) or absolute (False)
                self.yaw_manoeuvre(relative,point) #Time to start the tower-seeking phase by rotating the UAV until the tower is detected by ML
            else:
                #The point is only to avoid obstacles or cruise mode
                pass

        del positions[-1] #Delete last item of list (its the actual pos)
        inv_positions=list(positions)
        inv_positions.reverse()
        self.disarm_and_land(inv_positions)

    def arm_and_takeoff(self,aTargetAltitude):
        #Arms vehicle and fly to a Target Alt
        print("Basic pre-arm checks")
        #Don't try tot arm until autopilot is ready
        while not self.vehicle.is_armable:
            print("Waiting for vehicle to initialise...")
            time.sleep(1)
        print("Arming motors")
        #UAV should arm in GUIDED mode
        self.vehicle.mode=VehicleMode("GUIDED")
        self.vehicle.armed=True

        #Confirm vehicle armed before attempting to take-off
        while not self.vehicle.armed:
            print("Waiting for arming...")
            time.sleep(1)
        print("Taking off")
        self.vehicle.simple_takeoff(aTargetAltitude) #Take-off instruction to Target Alt

        #Wait until the vehicle reaches a safe height before processing the goto command
        while True:
            print("Altitude", self.vehicle.location.global_relative_frame.alt,"m Heading: ",self.vehicle.heading,"º")

            if self.vehicle.location.global_relative_frame.alt >=aTargetAltitude*0.95:
                print("Reached target altitude")
                break
            time.sleep(1)

    def disarm_and_land(self,return_path):
        # At the end, when all waypoints had been reached
        for pos in return_path:
            print("FLY BACK TO TOWER: ", pos)
            point = LocationGlobalRelative(float(pos[1][0]), float(pos[1][1]), 10)
            self.vehicle.simple_goto(point)  # Instruction to move to a point
            arrived = False
            previousPosition = self.vehicle.location.global_relative_frame
            time.sleep(1)
            while not arrived:
                arrived = self.compare_location(previousPosition,self.vehicle.location.global_relative_frame)  # Call compare_location to know if UAV has arrived to wp
                previousPosition = self.vehicle.location.global_frame
                time.sleep(0.3)
        self.vehicle.mode = VehicleMode("RTL")  # Change mode to Return To Launch
        while True:
            #print("RTL. Altitude", self.vehicle.location.global_relative_frame.alt,"m Heading: ",self.vehicle.heading,"º")
            if self.vehicle.location.global_relative_frame.alt >=0:
                pass
            else:
                print("TOUCHDOWN")
                break
            time.sleep(0.3)
        self.vehicle.armed = False  # Disarm UAV
        print("DISARMED")
        self.vehicle.close()

    def compare_location(self,previous,current):
        if previous.lat==current.lat and previous.lon == current.lon:
            return True
        else:
            return False

    def yaw_manoeuvre(self,relative,point):
        time.sleep(1)
        #Change yaw behaviour by starting a rotation of 360 deg and mantaining alt
        if relative:
            is_relative = 1  # yaw relative to direction of travel
        else:
            is_relative = 0  # yaw is an absolute angle

        #heading=180 #Full rotation
        yaw_speed=10 # Rotating speed deg/s
        heading_target=360 #Heading target
        msg = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, heading_target,yaw_speed,0, is_relative, 0, 0, 0)  # param 5 ~ 7 not used
        # send command to vehicle
        self.vehicle.send_mavlink(msg)
        while True:
            print("SCAN. Heading: ",self.vehicle.heading,"º")
            if self.vehicle.heading >=heading_target*0.5: #Simulating that the tower has been detected
                msg = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,self.vehicle.heading, 0, 0, 0, 0, 0,0)
                self.vehicle.send_mavlink(msg) #Commamd interruption and hold actual heading
                print("STOP ROTATION")
                print("START PHOTO SHOOTING")
                time.sleep(5)  # Wait 2s to stabilize
                break
            time.sleep(0.8)
        print("STOP PHOTO SHOOTING")
        time.sleep(5) #Wait 5s to stabilize