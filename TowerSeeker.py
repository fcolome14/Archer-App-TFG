from math import sin, cos, sqrt, atan2, radians
import os
from geographiclib.geodesic import Geodesic
from difflib import SequenceMatcher

class TowerSeekerClass:  # Tower name detection+distance from WP class

    def find_icon(self,path, name):
        #Given a path and a filename, looks in every directory and file inside the given path for a match
        for root, dirs, files in os.walk(path):
            if name in files:
                 return os.path.join(root, name)

    def load_data(self, Namepoint, Xpoint, Ypoint,init_twr,final_twr):
        #Namepoint --> List of tower names
        #Xpoint, Ypoint --> List of X,Y tower points
        #init_twr/final_twr --> List of tower names in each segment of Google Earth's route
        self.Namepoint=Namepoint
        self.Xpoint = Xpoint
        self.Ypoint=Ypoint
        self.init_twr=init_twr
        self.final_twr=final_twr
        #print("Tuple TWR: ", self.positionTWR)

        self.dist_list_before = []
        self.dist_list = []
        self.twrs_historic=[] #List of historic towers travelled through
        self.suggestions_historic = []  # List of historic suggestions

    def name_seeker(self, positionFP):
        geod = Geodesic.WGS84  # Initialize object

        #self.X0, self.Y0 = positionFP  # Divide tuple value in x,y independent variables. Float
        self.dist=1000000 #initial comp. distance (m)
        #self.R = 6373.0 # Approximate radius of earth in km
        self.lat2,self.lon2 = positionFP #Actual position
        #self.lat2= radians(float(self.lat2))
        #self.lon2 = radians(float(self.lon2))

        for i in range(len(self.Xpoint)):

            """
            self.lat1 = radians(float(self.Xpoint[i]))
            self.lon1 = radians(float(self.Ypoint[i]))

            self.dlon = self.lon2 - self.lon1
            self.dlat = self.lat2 - self.lat1

            self.a = sin(self.dlat / 2) ** 2 + cos(self.lat1) * cos(self.lat2) * sin(self.dlon / 2) ** 2
            self.c = 2 * atan2(sqrt(self.a), sqrt(1 - self.a))

            self.new_dist = self.R * self.c *1000 #distance in meters between actual waypoint and each tower loaded

            #print("Distance (km): ",self.new_dist)
            #print("ACTUAL", positionFP)
            #print("XTOWER",self.Xpoint[i])
            #print("YTOWER",self.Ypoint[i])
            """
            g = geod.Inverse(float(self.lat2), float(self.lon2), float(self.Xpoint[i]),float(self.Ypoint[i]))
            #print(g)
            self.new_dist = float(g['s12'])
            if self.new_dist<=self.dist:
                #print(self.new_dist)
                self.dist=self.new_dist
                self.index_twr = i
            else:
                pass


        self.TowerName=self.Namepoint[self.index_twr] #final result. Closest tower name found
        self.dist=round(self.dist,2) #--> Distance between waypoint and tower

        return self.TowerName,self.dist

    def equivalent_distance(self,distance):

        self.geod = Geodesic.WGS84 #Initialize object
        self.possible_towers=[]
        self.azimuth_list=[]
        self.azimuthLH=[]
        self.azimuthRH = []
        self.latLH=[]
        self.lonLH = []
        self.latRH = []
        self.lonRH = []

        """
        self.index_next_twr=self.tower_finder(list_twr1, list_twr2,self.Xpoint[self.index_twr],self.Ypoint[self.index_twr])
        #print(self.index_next_twr)
        #print(len(list_twr2))
        #print(len(list_twr1))
        # EVALUATE RESULT
        self.resultX1 = list_twr1[self.index_next_twr[0]].split(",")[0]
        self.resultY1 = list_twr1[self.index_next_twr[0]].split(",")[1]
        self.resultX2 = list_twr2[self.index_next_twr[0]].split(",")[0]
        self.resultY2 = list_twr2[self.index_next_twr[0]].split(",")[1]
        # Find which is the NEXT tower. Final deduction (WITHOUT FORKS!)
        if self.resultX1 == self.Xpoint[self.index_twr] and self.resultY1 == self.Ypoint[self.index_twr]:
            self.resultX=self.resultX2 #Next tower component X
            self.resultY = self.resultY2 #Next tower component Y
        elif self.resultX2 == self.Xpoint[self.index_twr] and self.resultY2 == self.Ypoint[self.index_twr]:
            self.resultX = self.resultX1 #Next tower component X
            self.resultY = self.resultY1 #Next tower component Y
        """

        self.possible_towers=self.find_direction() #Returns possible towers positions (index)

        #print(len(self.Xpoint),len(self.Ypoint))
        for item in self.possible_towers:
            g = self.geod.Inverse(float(self.Xpoint[self.index_twr]), float(self.Ypoint[self.index_twr]),float(self.Xpoint[item]), float(self.Ypoint[item]))
            # By passing the coordinates of both towers we can obtain info about the azimuth angle and distance between them
            #g = self.geod.Inverse(float(self.Xpoint[self.index_twr]), float(self.Ypoint[self.index_twr]),float(self.resultX), float(self.resultY))
            azimuth = 180 - float(g['azi2'])
            azimuth=360-azimuth #Angle Correction
            self.azimuth_list.append(azimuth) #Save each value of azimuth
            #print(self.azimuth_list)

        for angle in self.azimuth_list:
            # TO GET A WP in LH/ RH SIDE ALWAYS ORTHOGONAL TO TOWER. TARGET: AVOID CROSSING THE POWERLINE!
            if angle >= 0 and angle < 45:
                azimuthLH = angle + 270  # Correction applied to force that each WP suggested is printed in LH side/DOWN
                azimuthRH = angle + 90  # Correction applied to force that each WP suggested is printed in RH side/UP
            elif angle >= 45 and angle < 90:
                azimuthLH = azimuth + 270  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth + 90  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 90 and angle < 135:
                azimuthLH = azimuth + 90  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth + 270  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 135 and angle < 180:
                azimuthLH = azimuth + 90  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth - 90  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 180 and angle < 225:
                azimuthLH = azimuth + 90  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth - 90  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 225 and angle < 270:
                azimuthLH = azimuth + 90  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth - 90  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 270 and angle < 315:
                azimuthLH = azimuth - 90  # Correction applied to force that each WP suggested is printed in LH side
                azimuthRH = azimuth + 90  # Correction applied to force that each WP suggested is printed in RH side
            elif angle >= 315 and angle < 360:
                azimuthLH = azimuth - 90  # Correction applied to force that each WP suggested is printed in LLH side
                azimuthRH = azimuth - 270  # Correction applied to force that each WP suggested is printed in RH side
            else:
                azimuthLH = 0
                azimuthRH=0
            self.azimuthLH.append(azimuthLH)
            self.azimuthRH.append(azimuthRH)

        #print("Corrected AzimuthLH/AzimuthRH: ",azimuthLH,azimuthRH)

        #g_LH = self.geod.Direct(float(self.Xpoint[self.index_twr]), float(self.Ypoint[self.index_twr]), azimuthLH,distance) #Get coordinates of the perpendicular point
        #g_RH = self.geod.Direct(float(self.Xpoint[self.index_twr]), float(self.Ypoint[self.index_twr]), azimuthRH,distance)  # Get coordinates of the perpendicular point

        #g_LH = self.geod.Direct(float(self.resultX), float(self.resultY), azimuthLH,distance)  # Get coordinates of the perpendicular point
        #g_RH = self.geod.Direct(float(self.resultX), float(self.resultY), azimuthRH,distance)  # Get coordinates of the perpendicular point

        for item in self.possible_towers:

            i=0
            while i<len(self.azimuthLH):
                g_LH = self.geod.Direct(float(self.Xpoint[item]), float(self.Ypoint[item]), self.azimuthLH[i],distance)  # Get coordinates of each perpendicular point
                g_RH = self.geod.Direct(float(self.Xpoint[item]), float(self.Ypoint[item]), self.azimuthRH[i],distance)  # Get coordinates of each perpendicular point
                # print("Value:",g)
                i = i + 1

            self.latLH.append(float(g_LH['lat2']))
            self.lonLH.append(float(g_LH['lon2']))
            self.latRH.append(float(g_RH['lat2']))
            self.lonRH.append(float(g_RH['lon2']))

            i=0
            while i<len(self.latLH):
                value=(self.latLH[i],self.lonLH[i]) #Building a tuple
                self.suggestions_historic.append(value)
                i=i+1
            i = 0
            while i < len(self.latRH):
                value = (self.latRH[i], self.lonRH[i])  # Building a tuple
                self.suggestions_historic.append(value)
                i = i + 1

        return self.latLH, self.lonLH,self.latRH, self.lonRH
        #return self.resultX,self.resultY

    def tower_finder(self,list_twr1,list_twr2,actual_twrX,actual_twrY):

        self.twrAX = []
        self.twrAY = []
        self.twrBX = []
        self.twrBY = []
        self.index_actual_twr = []
        self.counter = 0
        self.statement=True

        for i in list_twr2: #Save X,Y components in separate lists
            self.twrAX.append(i.split(",")[0])
            self.twrAY.append(i.split(",")[1])

        #print("Expected: ", actual_twrX, actual_twrY)

        #First find the nearest tower to the actual detected tower (closest to WP)
        for i in range(len(self.twrAX)):
            scoreX=self.similar(self.twrAX[i],actual_twrX)
            scoreY = self.similar(self.twrAY[i], actual_twrY)
            if (self.twrAX[i]==actual_twrX and self.twrAY[i]==actual_twrY) or (scoreX>0.95 and scoreY>0.95):
                self.statement = False
                self.index_actual_twr.append(i) #Position of actual tower in this list. List because some times there are forks
                #print("FOUND: ",self.twrAX[i],self.twrAY[i])
            else:
                pass
                #self.index_actual_twr.append(-1) #Tower not found

        # Extract tower1 components
        for i in range(len(list_twr1)):  # Save X,Y components in separate lists
            self.twrBX.append(list_twr1[i].split(",")[0])
            self.twrBY.append(list_twr1[i].split(",")[1])

        if self.statement==True: #Try in tower1
            #print(len(list_twr1),len(self.twrAX),len(self.twrAY),range(len(list_twr1)))
            for i in range(len(self.twrBX)):
                scoreX=self.similar(self.twrBX[i],actual_twrX)
                scoreY = self.similar(self.twrBY[i], actual_twrY)
                #print(self.twrAX[i],self.twrAY[i],scoreX,scoreY)
                if (self.twrBX[i]==actual_twrX and self.twrBY[i]==actual_twrY) or (scoreX>0.95 and scoreY>0.95):
                    self.index_actual_twr.append(i) #Position of actual tower in this list. List because some times there are forks
                    #print("FOUND: ",self.twrBX[i],self.twrBY[i])
                else:
                    pass
                    #self.index_actual_twr.append(-1) #Tower not found
        else:
            pass

        #print(self.index_actual_twr)

        #for i in self.index_actual_twr:
            #print("TOWER A: ", self.twrAX[i],self.twrAY[i])
            #print("TOWER  B: ", self.twrBX[i],self.twrBY[i])

        return self.index_actual_twr

    def similar(self,a,b):
        return SequenceMatcher(None,a,b).ratio()#Return matching value of strings

    def find_direction(self):
        self.index_next_twr = []
        self.id_next_twr = []
        self.next_twrA=[] #Taking into account different forks
        self.next_twrB = [] #Taking into account different forks
        self.found=False #Found next tower

        self.actual_twr = self.Namepoint[self.index_twr] #Actual tower name
        self.twrs_historic.append(self.actual_twr) #Add actual tower to the register
        #print("ACTUAL ", self.actual_twr)

        # Find direction of propagation
        #print(self.twrs_historic)
        if len(self.twrs_historic) > 1:
            i = 0
            for twr in self.init_twr:
                if self.similar(twr, self.actual_twr) > 0.95:
                    self.next_twrA.append(self.final_twr[i])  # Save next tower id. Direction A
                    #print("NEXT TWR A", self.next_twrA)
                i = i + 1
            i = 0
            for twr in self.final_twr:
                if self.similar(twr, self.actual_twr) > 0.95:
                    self.next_twrB.append(self.init_twr[i])  # Save next tower id. Direction B
                    #print("NEXT TWR B", self.next_twrB)
                i = i + 1

            #FIND POSSIBLE NEXT TOWERS
            for tower in self.next_twrA:
                if self.twrs_historic[-2] == tower:  # Means the last tower registered has already been passed
                    self.found = True

                    if len(self.next_twrA)>1:
                        # NEXT TOWER IS IN TOWER B OR IF ITS LEN>1 ALSO IN TWR A. THERE IS A FORK
                        self.next_twrA.remove(tower) #Remove passed tower from list

                        i=0
                        while i<len(self.next_twrA):
                            #print(self.next_twrA[i])
                            self.id_next_twr.append(self.next_twrA[i])
                            i=i+1
                        i = 0
                        while i < len(self.next_twrB):
                            self.id_next_twr.append(self.next_twrB[i])  #List includes all possibilities from TowerA + TowerB
                            i = i + 1
                    else:
                        # NEXT TOWER IS IN TOWER B. Just one element
                        i = 0
                        while i < len(self.next_twrB):
                            self.id_next_twr.append(
                                self.next_twrB[i])  # List includes all possibilities from TowerA + TowerB
                            i = i + 1
            if self.found==False:
                for tower in self.next_twrB:
                    if self.twrs_historic[-2] == tower:  # Means the last tower registered has already passed

                        if len(self.next_twrB)>1:
                            # NEXT TOWER IS IN TOWER A OR IF ITS LEN>1 ALSO IN TWR B. THERE IS A FORK
                            self.next_twrB.remove(tower) #Remove passed tower from list

                            i = 0
                            while i < len(self.next_twrB):
                                #print(self.next_twrB[i])
                                self.id_next_twr.append(self.next_twrB[i])
                                i = i + 1
                            i = 0
                            while i < len(self.next_twrA):
                                self.id_next_twr.append(self.next_twrA[i])  # List includes all possibilities from TowerB + TowerA
                                i = i + 1
                        else:
                            # NEXT TOWER IS IN TOWER A
                            i = 0
                            while i < len(self.next_twrA):
                                self.id_next_twr.append(self.next_twrA[i])  # List includes all possibilities from TowerA + TowerB
                                i = i + 1
            # print("POSSIBILITIES: ", self.id_next_twr)

            # Get index values of each possible tower
            for item in self.id_next_twr:
                j = 0
                while j < len(self.Namepoint):
                    if self.Namepoint[j] == item:
                        self.index_next_twr.append(j)
                    j = j + 1
        else:
            #Initial point after switching to suggestion mode
            #Show possibilities for next move. AFT/FWD Tower
            i = 0
            for twr in self.init_twr:
                if self.similar(twr, self.actual_twr) > 0.95:
                    self.next_twrA.append(self.final_twr[i])  # Save next tower id. Direction A
                    #print("NEXT TWR A", self.next_twrA)
                i = i + 1
            i = 0
            for twr in self.final_twr:
                if self.similar(twr, self.actual_twr) > 0.95:
                    self.next_twrB.append(self.init_twr[i])  # Save next tower id. Direction B
                    #print("NEXT TWR B", self.next_twrB)
                i = i + 1

            if len(self.next_twrA)>0: #Not empty
                for item in self.next_twrA:
                    j=0
                    while j<len(self.Namepoint):
                        if self.Namepoint[j] == item:
                            self.index_next_twr.append(j)
                        j = j + 1
            if len(self.next_twrB)>0: #Not empty
                for item in self.next_twrB:
                    j=0
                    while j<len(self.Namepoint):
                        if self.Namepoint[j] == item:
                            self.index_next_twr.append(j)
                        j = j + 1

            #print(self.index_next_twr)

        return self.index_next_twr

    def get_distance(self,positionWP):
        geod = Geodesic.WGS84  # Initialize object

        i=0
        dist=8
        j=-1
        #Look for closest point of LH side
        while(i<len(self.suggestions_historic)):
            g = geod.Inverse(float(positionWP[0]), float(positionWP[1]),float(self.suggestions_historic[i][0]), float(self.suggestions_historic[i][1]))
            dist_new = float(g['s12'])
            if dist_new<=dist:
                dist=dist_new
                j=i
            i=i+1

        if j!=-1:
            final_Xpos = self.suggestions_historic[j][0]
            final_Ypos = self.suggestions_historic[j][1]
        else:
            final_Xpos = -1
            final_Ypos = -1


        return final_Xpos,final_Ypos

    def update_historic_suggestion(self):
        self.twrs_historic.pop()#When DeleteWP is executed, must delete the last tower register
        print("HISTORIC AFTER: ",self.suggestions_historic)

    def fill_historic_twrs(self):
        #Still updating historic of travelled towers. This way if user switches ON the button, the system will know the next suggestion twr
        self.twrs_historic.append(self.Namepoint[self.index_twr])

    def find_sequence(self,new_WP,actual_positions,pos_id):
        geod = Geodesic.WGS84
        distances=[]
        segment_distances=[]
        segment_positions=[] #Tuple of positions
        segment_azimuth = []
        intermediate_points_to_add=[]
        total_points_pos=[] #Tuple of each point
        final_res=[]
        i=0
        while (i < len(actual_positions)-1): #Find distance of each segment bewteen twr(i) and twr(i-1). And azimuth
            g = geod.Inverse(float(actual_positions[i][0]), float(actual_positions[i][1]), float(actual_positions[i+1][0]), float(actual_positions[i+1][1]))
            dist_new = float(g['s12'])
            #azimuth = 180 - float(g['azi2'])
            azimuth = float(g['azi2'])
            #print("AZ RAW:",float(g['azi2']))
            #azimuth = 360 - azimuth  # Angle Correction
            segment_positions.append((float(actual_positions[i][0]), float(actual_positions[i][1]), float(actual_positions[i+1][0]), float(actual_positions[i+1][1])))
            segment_distances.append(dist_new)
            segment_azimuth.append(azimuth)

            i=i+1
        #print("SEG DISTANCES: ",segment_distances)
        min_segment_dist=(min(segment_distances))/10 #To be sure its a significant low value for the segmentation
        #print("MIN_SEGMENT_DIST: ",min_segment_dist)
        #print("AZ VALUES: ", segment_azimuth)
        #print("SEG POS: ", segment_positions)
        for item in segment_distances: #Find how many intermediate points must to be added on each segment
            result=round(item/min_segment_dist,0)
            intermediate_points_to_add.append(int(result))
        #print("INTERMEDIATE POINTS TO ADD: ",intermediate_points_to_add)
        i=0
        #dist_div=segment_distances[i]/intermediate_points_to_add[i]
        while i<len(segment_positions):
            dist=0
            j = 0
            if intermediate_points_to_add[i]>1:
                dist_div=(segment_distances[i]/intermediate_points_to_add[i]) #Divisions of distance dist_div for each segment
                #print("intermediate_points_to_add: ", intermediate_points_to_add[i])
                #("dist_div ", dist_div)
            else:
                dist_div=0
            while j<intermediate_points_to_add[i]:
                if j==0:
                    dist=0
                else:
                    dist = dist + dist_div

                g = geod.Direct(segment_positions[i][0],segment_positions[i][1], segment_azimuth[i], dist)
                #print(segment_positions[i][0],segment_positions[i][1], segment_azimuth[i], dist)
                lat = float(g['lat2'])
                lon = float(g['lon2'])
                total_points_pos.append(((i+1),(lat,lon))) #Reference points generated for each segment
                j=j+1

            i=i+1
        #print("TOTAL POINTS: ", total_points_pos)

        i=0
        dist=1000
        #Loop to find closest point to new one added in modification mode
        while (i < len(total_points_pos)):
            g = geod.Inverse(float(total_points_pos[i][1][0]),float(total_points_pos[i][1][1]),float(new_WP[0]),float(new_WP[1]))
            dist_new= float(g['s12'])
            if dist_new <= dist:
                dist = dist_new+50
                tuple_dist_id_pos=(dist_new,total_points_pos[i][0],float(total_points_pos[i][1][0]),float(total_points_pos[i][1][1])) #Tuple: DIST, ID, POX,POSY
                final_res.append(tuple_dist_id_pos)
                distances.append(dist_new)
            i = i + 1
        #print(tuple_dist_id_pos)
        first_min_value=min(distances)
        distances.remove(min(distances)) #Eliminate first candidate from list. Then find second one
        second_min_value = min(distances)

        i=0
        while i<len(final_res):
            if final_res[i][0]==first_min_value:
                tower1_pos=(final_res[i][2],final_res[i][3])
                tower1_id=final_res[i][1]
            elif final_res[i][0]==second_min_value:
                tower2_pos = (final_res[i][2], final_res[i][3])
                tower2_id = final_res[i][1]

            i=i+1

        return tower1_id,tower1_pos,tower2_id,tower2_pos
