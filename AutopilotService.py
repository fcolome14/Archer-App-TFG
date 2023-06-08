import json
import math
import threading
import paho.mqtt.client as mqtt
import time
import dronekit
from dronekit import connect, Command, VehicleMode, LocationGlobalRelative
#from dronekit import LocationGlobalRelative #TT Inspections contribution
from pymavlink import mavutil


def arm():
    """Arms vehicle and fly to aTargetAltitude"""
    print("Basic pre-arm checks")  # Don't try to arm until autopilot is ready
    vehicle.mode = dronekit.VehicleMode("GUIDED")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)
    print("Arming motors")
    # Copter should arm in GUIDED mode

    vehicle.armed = True
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)
    print(" Armed")

def take_off(a_target_altitude, manualControl):
    global state
    vehicle.simple_takeoff(a_target_altitude)
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= a_target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

    state = 'flying'
    if manualControl:
        w = threading.Thread(target=flying)
        w.start()


def prepare_command(velocity_x, velocity_y, velocity_z):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0,
        0,  # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0,
        0,
        0,  # x, y, z positions (not used)
        velocity_x,
        velocity_y,
        velocity_z,  # x, y, z velocity in m/s
        0,
        0,
        0,  # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0,
        0,
    )  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    return msg
'''
These are the different values for the state of the autopilot:
    'connected' (only when connected the telemetry_info packet will be sent every 250 miliseconds)
    'arming'
    'armed'
    'disarmed'
    'takingOff'
    'flying'
    'returningHome'
    'landing'
    'onHearth'

The autopilot can also be 'disconnected' but this state will never appear in the telemetry_info packet 
when disconnected the service will not send any packet
'''
def get_telemetry_info ():
    global state
    telemetry_info = {
        'lat': vehicle.location.global_frame.lat,
        'lon': vehicle.location.global_frame.lon,
        'heading': vehicle.heading,
        'groundSpeed': vehicle.groundspeed,
        'altitude': vehicle.location.global_relative_frame.alt,
        'battery': vehicle.battery.level,
        'state': state
    }
    return telemetry_info


def send_telemetry_info():
    global external_client
    global sending_telemetry_info
    global sending_topic

    while sending_telemetry_info:
        external_client.publish(sending_topic + "/telemetryInfo", json.dumps(get_telemetry_info()))
        time.sleep(0.25)


def returning():
    global sending_telemetry_info
    global external_client
    global internal_client
    global sending_topic
    global state

    # wait until the drone is at home
    while vehicle.armed:
        time.sleep(1)
    state = 'onHearth'

def flying():
    global direction
    global go
    speed = 1
    end = False
    cmd = prepare_command(0, 0, 0)  # stop
    while not end:
        go = False
        while not go:
            vehicle.send_mavlink(cmd)
            time.sleep(1)
        # a new go command has been received. Check direction
        if direction == "North":
            cmd = prepare_command(speed, 0, 0)  # NORTH
        if direction == "South":
            cmd = prepare_command(-speed, 0, 0)  # SOUTH
        if direction == "East":
            cmd = prepare_command(0, speed, 0)  # EAST
        if direction == "West":
            cmd = prepare_command(0, -speed, 0)  # WEST
        if direction == "NorthWest":
            cmd = prepare_command(speed, -speed, 0)  # NORTHWEST
        if direction == "NorthEst":
            cmd = prepare_command(speed, speed, 0)  # NORTHEST
        if direction == "SouthWest":
            cmd = prepare_command(-speed, -speed, 0)  # SOUTHWEST
        if direction == "SouthEst":
            cmd = prepare_command(-speed, speed, 0)  # SOUTHEST
        if direction == "Stop":
            cmd = prepare_command(0, 0, 0)  # STOP
        if direction == "RTL":
            end = True



def distanceInMeters(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def executeFlightPlan(waypoints_json):
    global vehicle
    global internal_client, external_client
    global sending_topic
    global state



    altitude = 6
    origin = sending_topic.split('/')[1]

    waypoints = json.loads(waypoints_json)

    state = 'arming'
    arm()
    state = 'takingOff'
    take_off(altitude, False)
    state = 'flying'


    wp = waypoints[0]
    originPoint = dronekit.LocationGlobalRelative(float(wp['lat']), float(wp['lon']), altitude)

    distanceThreshold = 0.50
    for wp in waypoints [1:]:

        destinationPoint = dronekit.LocationGlobalRelative(float(wp['lat']),float(wp['lon']), altitude)
        vehicle.simple_goto(destinationPoint)

        currentLocation = vehicle.location.global_frame
        dist = distanceInMeters (destinationPoint,currentLocation)

        while dist > distanceThreshold:
            time.sleep(0.25)
            currentLocation = vehicle.location.global_frame
            dist = distanceInMeters(destinationPoint, currentLocation)
        print ('reached')
        waypointReached = {
            'lat':currentLocation.lat,
            'lon':currentLocation.lon
        }

        external_client.publish(sending_topic + "/waypointReached", json.dumps(waypointReached))

        if wp['takePic']:
            # ask to send a picture to origin
            internal_client.publish(origin + "/cameraService/takePicture")

    vehicle.mode = dronekit.VehicleMode("RTL")
    state = 'returningHome'

    currentLocation = vehicle.location.global_frame
    dist = distanceInMeters(originPoint, currentLocation)

    while dist > distanceThreshold:
        time.sleep(0.25)
        currentLocation = vehicle.location.global_frame
        dist = distanceInMeters(originPoint, currentLocation)

    state = 'landing'
    while vehicle.armed:
        time.sleep(1)
    state = 'onHearth'


def executeFlightPlan2(waypoints_json):
    global vehicle
    global internal_client, external_client
    global sending_topic
    global state



    altitude = 6
    origin = sending_topic.split('/')[1]

    waypoints = json.loads(waypoints_json)
    state = 'arming'
    arm()
    state = 'takingOff'
    take_off(altitude, False)
    state = 'flying'
    cmds = vehicle.commands
    cmds.clear()

    #wp = waypoints[0]
    #originPoint = dronekit.LocationGlobalRelative(float(wp['lat']), float(wp['lon']), altitude)
    for wp in waypoints:
        cmds.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,0, 0, 0, 0, float(wp['lat']), float(wp['lon']), altitude))
    wp = waypoints[0]
    cmds.add(
        Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0,
                0, 0, 0, 0, float(wp['lat']), float(wp['lon']), altitude))
    cmds.upload()

    vehicle.commands.next = 0
    # Set mode to AUTO to start mission
    vehicle.mode = VehicleMode("AUTO")
    while True:
        nextwaypoint = vehicle.commands.next
        print ('next ', nextwaypoint)
        if nextwaypoint == len(waypoints):  # Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
            print("Last waypoint reached")
            break;
        time.sleep(0.5)

    print('Return to launch')
    state = 'returningHome'
    vehicle.mode = VehicleMode("RTL")
    while vehicle.armed:
        time.sleep(1)
    state = 'onHearth'




def process_message(message, client):
    global vehicle
    global direction
    global go
    global sending_telemetry_info
    global sending_topic
    global op_mode
    global sending_topic
    global state
    global TTpositions
    global TTairspeed
    global TTActual
    global found

    splited = message.topic.split("/")
    origin = splited[0]
    command = splited[2]
    sending_topic = "autopilotService/" + origin

    if command == "connect":
        if state == 'disconnected':
            print("Autopilot service connected by " + origin)
            if op_mode == 'simulation':
                connection_string = "tcp:127.0.0.1:5763"
            else:
                connection_string = "/dev/ttyS0"


            vehicle = connect(connection_string, wait_ready=False, baud=115200)

            vehicle.wait_ready(True, timeout=5000)

            print ('Connected to flight controller')
            state = 'connected'

            #external_client.publish(sending_topic + "/connected", json.dumps(get_telemetry_info()))


            sending_telemetry_info = True
            y = threading.Thread(target=send_telemetry_info)
            y.start()
        else:
            print ('Autopilot already connected')



    if command == "disconnect":
        vehicle.close()
        sending_telemetry_info = False
        state = 'disconnected'


    if command == "takeOff":
        state = 'takingOff'
        w = threading.Thread(target=take_off, args=[5,True ])
        w.start()



    if command == "returnToLaunch":
        # stop the process of getting positions
        vehicle.mode = dronekit.VehicleMode("RTL")
        state = 'returningHome'
        direction = "RTL"
        go = True
        w = threading.Thread(target=returning)
        w.start()

    if command == "armDrone":
        state = 'arming'
        arm()

        # the vehicle will disarm automatically is takeOff does not come soon
        # when attribute 'armed' changes run function armed_change
        vehicle.add_attribute_listener('armed', armed_change)
        state = 'armed'

    if command == "disarmDrone":
        vehicle.armed = False
        while vehicle.armed:
            time.sleep(1)
        state = 'disarmed'


    if command == "land":

        vehicle.mode = dronekit.VehicleMode("LAND")
        state = 'landing'
        while vehicle.armed:
            time.sleep(1)
        state = 'onHearth'

    if command == "go":
        direction = message.payload.decode("utf-8")
        print("Going ", direction)
        go = True

    if command == 'executeFlightPlan':
        waypoints_json = str(message.payload.decode("utf-8"))
        w = threading.Thread(target=executeFlightPlan2, args=[waypoints_json, ])
        w.start()

    #----------------- UAV TT INSPECTION FUNCTIONALITIES-----------------
    if command == 'setWaypoints':

        TTpositions = eval(message.payload.decode("utf-8"))
        print("WPs: ", TTpositions, type(TTpositions), len(TTpositions))
        client.publish("autopilotService/" + origin + "/setWaypoints", "OK") #Feedback
        print("Publish setWP OK")

    if command == 'setAirspeed':
        TTairspeed = message.payload.decode("utf-8")
        TTairspeed=int(TTairspeed)*(1000/3600)
        print("Airspeed: ", TTairspeed, " m/s")

    if command == 'inspTakeOff':
        # Arms vehicle and fly it to a Target Alt
        print("Basic pre-arm checks")
        # Don't try tot arm until autopilot is ready
        while not vehicle.is_armable:
            print("Waiting for vehicle to initialise...")
            time.sleep(1)
        print("Arming motors")
        # UAV should arm in GUIDED mode
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        # Confirm vehicle armed before attempting to take-off
        while not vehicle.armed:
            print("Waiting for arming...")
            time.sleep(5)
        #Arming sequence done
        state = 'takingOff'
        vehicle.simple_takeoff(3)  # Take-off instruction to Target Alt
        #Proceed to takeOff until 5m reached
        print("Taking Off")
        time.sleep(0.5)
        # Wait until the vehicle reaches a safe height before proceeding to inspection
        while True:
            print("Altitude", vehicle.location.global_relative_frame.alt, "m Heading: ", vehicle.heading, "º")

            if vehicle.location.global_relative_frame.alt >= 3 * 0.95:
                print("Reached target altitude")
                client.publish("autopilotService/" + origin + "/inspTakeOff", "OK")  # While stabilized. Return feedback
                break
            time.sleep(0.5)

    if command == "startInsp":
        TTActual = int(message.payload.decode("utf-8")) #Decode payload info about actual tower to reach
        #inspectionFP(TTpositions, origin, TTActual)
        w = threading.Thread(target=inspectionFP, args=[TTpositions,origin,TTActual])
        w.start()
        w.join()

    if command == 'startScan':
        Angle_inc = int(message.payload.decode("utf-8"))  # Decode payload info about angle increment
        # The point has a tower to inspect. Need rotation sequence
        relative = True  # Rotate relative to UAVs heading (True) or absolute (False)
        w = threading.Thread(target=yaw_manoeuvreFP, args=[relative, origin, Angle_inc])
        w.start()
        w.join()

    if command == 'inspLand':

        del TTpositions[-1]  # Delete last item of list (its the actual pos)
        inv_positions = list(TTpositions)  # Reverse items form list
        inv_positions.reverse()
        #disarm_and_landFP(inv_positions)
        w = threading.Thread(target=disarm_and_landFP, args=[inv_positions,origin])
        w.start()
        w.join()


def inspectionFP(TTpositions,origin,TTActual):

    global vehicle
    global internal_client, external_client
    global sending_topic
    global state
    global heading
    global scan_rounds

    print("FLYING TO NEXT TOWER: ", TTpositions[TTActual])
    point = LocationGlobalRelative(float(TTpositions[TTActual][1][0]), float(TTpositions[TTActual][1][1]), 3)
    # print("Point ", point)
    time.sleep(1)
    vehicle.simple_goto(point)  # Instruction to move to a point
    arrived = False
    previousPosition = vehicle.location.global_relative_frame
    time.sleep(1)
    while not arrived:
        arrived = compare_location(previousPosition,vehicle.location.global_relative_frame)  # Call compare_location to know if UAV has arrived to wp
        previousPosition = vehicle.location.global_frame
        time.sleep(0.3)
    print("POSITION REACHED")

    if TTpositions[TTActual][0] == "T":
        # The point has a tower to inspect. Need rotation sequence
        time.sleep(2)
        heading=vehicle.heading #Initial heading
        scan_rounds=0
        external_client.publish("autopilotService/" + origin + "/readyScan") #Notify user that position is reached and is ready to scan
        # internal_client.publish(origin + "/cameraService/stopVideoStreamFP")
    else:
        # The point is only to avoid obstacles or cruise mode
        print("TOWER TYPE C (OBSTACLE AVOIDANCE)")
        print("Actual tower pos ", TTActual)
        #TTActual=int(TTActual)+1
        print("Next tower pos ",TTActual)
        time.sleep(2)
        external_client.publish("autopilotService/" + origin + "/nextWP", str(TTActual))

def yaw_manoeuvreFP(relative,origin,heading_increase):
        global heading
        global TTActual
        global scan_rounds

        time.sleep(1)
        #Change yaw behaviour by starting a rotation of 360 deg and mantaining alt
        if relative:
            is_relative = 1  # yaw relative to direction of travel
        else:
            is_relative = 0  # yaw is an absolute angle

        change=False
        yaw_speed=10 # Rotating speed deg/s --CHANGED TO 10 deg/s for flight test---
        #heading_target=heading_target+vehicle.heading
        heading_target=vehicle.heading+heading_increase

        if heading_target>=360:
            #Reset value
            heading_target=heading_target-360
            change=True
            scan_rounds=scan_rounds+1 #Number of full rotations made


        print("Initial Heading:", vehicle.heading)
        print("Target: ",heading_target)
        if change==False:
            #msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, heading_target,yaw_speed,0, is_relative, 0, 0, 0)  # param 5 ~ 7 not used
            msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,heading_increase, yaw_speed, 1, is_relative, 0, 0, 0)
            # send command to vehicle
            vehicle.send_mavlink(msg)
        else:
            msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, heading_increase, yaw_speed, 1, is_relative, 0, 0, 0)
            # Rotate UAV to first quadrant
            vehicle.send_mavlink(msg)
            time_wait = heading_increase / yaw_speed
            print(time_wait)
            time.sleep(time_wait)


        while True:
            #print(vehicle.heading)
            if vehicle.heading >= heading_target * 0.99:
                msg = vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0,0, 0, 1, is_relative, 0, 0, 0) #Increase of 0 (stop)
                vehicle.send_mavlink(msg)  # Commamd interruption and hold actual heading
                break

        print("Final Heading:", vehicle.heading)

        if (scan_rounds==1 and vehicle.heading>=heading*0.99):
            print("Tower not detected. Abort scanning")
            time.sleep(2)
            print("Next tower pos ", TTActual)
            time.sleep(2)
            external_client.publish("autopilotService/" + origin + "/nextWP", str(TTActual))

        else:
            print("Take photo")
            time.sleep(2)
            internal_client.publish(origin + "/cameraService/takePictureFP")  # SCANNING WHILE TAKING PICTURES TEST.COMMENTED ---

def disarm_and_landFP(return_path,origin):
        global internal_client, external_client
        global TTpositions

        # At the end, when all waypoints had been reached
        for pos in return_path:
            print("FLY BACK TO TOWER: ", pos)
            point = LocationGlobalRelative(float(pos[1][0]), float(pos[1][1]), 5)
            vehicle.simple_goto(point)  # Instruction to move to a point
            arrived = False
            previousPosition = vehicle.location.global_relative_frame
            time.sleep(0.5)
            while not arrived:
                arrived = compare_location(previousPosition,vehicle.location.global_relative_frame)  # Call compare_location to know if UAV has arrived to wp
                previousPosition = vehicle.location.global_frame
                time.sleep(0.3)
        vehicle.parameters['RTL_ALT'] = 0 #Set same altitude to RTL mode
        vehicle.mode = VehicleMode("RTL")  # Change mode to Return To Launch
        while True:
            #print("RTL. Altitude", self.vehicle.location.global_relative_frame.alt,"m Heading: ",self.vehicle.heading,"º")
            if vehicle.location.global_relative_frame.alt >=0:
                pass
            else:
                print("TOUCHDOWN")
                break

        external_client.publish("autopilotService/" + origin + "/landed")
        internal_client.publish(origin + "/cameraService/shutCamOFF")
        vehicle.armed = False  # Disarm UAV
        vehicle.flush()
        print("DISARMED")

def armed_change(self, attr_name, value):
    global vehicle
    global state

    if vehicle.armed:
        state = 'armed'
    else:
        state = 'disarmed'

def compare_location(previous,current):
    #Compare position. TT Inspection contribution
    if previous.lat==current.lat and previous.lon == current.lon:
        return True
    else:
        return False

def on_internal_message(client, userdata, message):
    global internal_client
    process_message(message, internal_client)

def on_external_message(client, userdata, message):
    global external_client
    process_message(message, external_client)

def AutopilotService (connection_mode, operation_mode, external_broker, username, password):
    global op_mode
    global external_client
    global internal_client
    global state

    state = 'disconnected'

    print ('Connection mode: ', connection_mode)
    print ('Operation mode: ', operation_mode)
    op_mode = operation_mode

    # The internal broker is always (global or local mode) at localhost:1884
    internal_broker_address = "localhost"
    internal_broker_port = 1884

    if connection_mode == 'global':
        external_broker_address = external_broker
    else:
        external_broker_address = 'localhost'


    print ('External broker: ', external_broker_address)



    # the external broker must run always in port 8000
    external_broker_port = 8000



    external_client = mqtt.Client("Autopilot_external", transport="websockets")
    if external_broker_address == 'classpip.upc.edu':
        external_client.username_pw_set(username, password)

    external_client.on_message = on_external_message
    external_client.connect(external_broker_address, external_broker_port)


    internal_client = mqtt.Client("Autopilot_internal")
    internal_client.on_message = on_internal_message
    internal_client.connect(internal_broker_address, internal_broker_port)

    print("Waiting....")
    external_client.subscribe("+/autopilotService/#", 2)
    internal_client.subscribe("+/autopilotService/#")
    if operation_mode == 'simulation':
        external_client.loop_forever()
    else:
        external_client.loop_start()
    internal_client.loop_start()


if __name__ == '__main__':
    import sys
    connection_mode = sys.argv[1] # global or local
    operation_mode = sys.argv[2] # simulation or production
    username = None
    password = None
    if connection_mode == 'global':
        external_broker = sys.argv[3]
        if external_broker == 'classpip.upc.edu':
            username = sys.argv[4]
            password = sys.argv[5]
    else:
        external_broker = None

    AutopilotService(connection_mode,operation_mode, external_broker, username, password)
