# Archer App. Autonomous high-voltage tower detection employing UAVs
## Archer App
The purpose of the Archer App application is to create flight plan legs complying with current regulations, and then sending the data to the UAV to perform the inspection.


## Camera Service
The camera service is an on-board module that provides images to the rest of modules of the ecosystem, such as the Archer App.

The table bellow indicates all the commands that are accepted by the Camera Service applied to the Archer App.

Command | Description | Payload | Answer | Answer payload
--- | --- | --- | --- |---
*takePictureFP* | provides a picture | No | *picture* | Yes (see Note 1)


## Autopilot Service
The autopilot service is an on-board module that controls the operation of the flight controller, as required by the rest of modules in the Drone Engineering Ecosystem. 

The table bellow indicates all the commands that are accepted by the Autopilot Service applied to the Archer App.

Command | Description | Payload | Answer | Answer payload
--- | --- | --- | --- |--- 
*connect* | connect with the simulator or the flight controller depending on the operation mode | No | No (see Note 1) | No
*setWaypoints* | send data from Archer App to UAV | Yes | Yes ("OK") | No 
*setAirspeed* | send airspeed data | Yes | No  | No 
*inspTakeOff* | Arm and take-off procedure | No  | Yes ("OK") | No    
*startInsp* | Fly to next waypoint to inspect | No  | Yes ("OK") | No     
*startScan* | Start area scanning | No  |  Yes () | No
*nextWP* | Fly to next waypoint | No  | No | No
*inspLand* | Landing procedure | No  | No | Yes ("landed")

