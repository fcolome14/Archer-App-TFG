
import xml.etree.ElementTree as ET
import xml.dom.minidom
from bs4 import BeautifulSoup
import os
from KmzToKml import KmzToKml

class KmlExtractor:

    def KmlExtractor(self,path):

        #path = 'C:/Users/USUARIO/Documents/TFG/LIST_KML/doc.kml'  # Folder with the .kmz we want to extract for the flight plan

        KmzToKmlClass = KmzToKml()
        self.result = KmzToKmlClass.KmzConverter(path)  # Executing converter .kmz to .kml class

        if self.result != -1:
            self.waypoints = []  # Tower names vector
            self.x_coord = [] #Xpoint of a tower
            self.y_coord = [] #Ypoint of a tower

            self.descrip_raw = []
            self.descrip_filtered = []
            self.t1 = []
            self.t2 = []
            self.init_tower = []
            self.final_tower = []

            self.coord_twr1 = []
            self.coord_twr2 = []

            self.directory_path = os.path.dirname(self.result)
            for filename in os.listdir(self.directory_path):
                if not filename.endswith('.kml'): continue
                self.doc = ET.parse(self.result)

            # nmsp = '{http://earth.google.com/kml/2.2}'
            self.nmsp = '{http://www.opengis.net/kml/2.2}'  # Using the .kmz to .kml converter
            self.count = 0
            self.count2 = 0

            for pm in self.doc.iterfind('.//{0}Placemark'.format(self.nmsp)):  # Iterative Loop until Placemark is found in the KML
                # print(pm.find('{0}name'.format(nmsp)).text) #Shows the name field <name> of each point
                self.waypoint_name = pm.find('{0}name'.format(self.nmsp)).text
                self.waypoints.append(self.waypoint_name)

                for ls in pm.iterfind('{0}Point/{0}coordinates'.format(self.nmsp)): #RECOVERING COORDINATES AND NAME FOR EACH TOWER OF A KML FILE
                    # Loop iterativo siguiendo la escala del formato hasta llegar a las coord, <Point> --> <coordinates>
                    # print(ls.text.strip().replace('\n', ''))
                    self.coordinate = str(ls.text.strip().replace('\n', ''))
                    # print(count, coordinate)
                    self.coordinate = self.coordinate.split(',')
                    self.x_coord.append(self.coordinate[1])
                    self.y_coord.append(self.coordinate[0])
                    #self.count = self.count + 1

                for mk in pm.iterfind('{0}LineString/{0}coordinates'.format(self.nmsp)): #RECOVERING COORDINATES BETWEEN TOWERS TO PLOT POWER LINES
                    # Loop iterativo siguiendo la escala del formato hasta llegar a las coord, <Point> --> <coordinates>
                    # print(ls.text.strip().replace('\n', ''))
                    self.coordinate_raw = str(mk.text.strip().replace('\n', ''))
                    self.coordinate_raw = self.coordinate_raw.split(' ')
                    self.coord_twr1.append(self.coordinate_raw[0])
                    self.coord_twr2.append(self.coordinate_raw[1])

                for des in pm.iterfind('{0}description'.format(self.nmsp)):
                    self.description = str(des.text.strip().replace('\n', ''))
                    # print(count, coordinate)
                    self.decription = self.description.split('<p>')
                    # print(description)
                    self.descrip_raw.append(self.description)

                pass
            #print(self.waypoints[self.tower], self.x_coord[self.tower], self.y_coord[self.tower])  # Coordinates Result

            #EXTRACTION OF TOWER NAMES BY ORDER
            for item in self.descrip_raw:
                self.descrip_filtered.append(item.split("</p>"))
                # print(item.split("</p>"))
            self.descrip_raw.clear()
            descrip_raw = []
            for item in self.descrip_filtered:
                #print("item: ", item[0], item[1])
                if item[0].split(" ")[0] == "<p>APOINI_MAT:":
                    self.t1.append(item[0].split("<p>")[1])
                    # print("List1: ",init_tower)
                if item[1].split(" ")[0] == "<p>APOFIN_MAT:":
                    # final_tower.append(item[1].split("<p>")[1])
                    self.t2.append(item[1].split("<p>")[1])
            #print(len(self.t2), len(self.t1))
            for item in self.t1:
                self.init_tower.append(item.split(": ")[1])
            for item in self.t2:
                self.final_tower.append(item.split(": ")[1])

            #print("INIT TOWER:", self.init_tower)
            #print("FINAL TOWER:", self.final_tower)


            #print(self.coord_twr1)
            #PRE-PROCESSING of coord_twr1/2
            self.coord_twr1_xy = []
            self.coord_twr2_xy = []

            for i in self.coord_twr1:
                self.coord_twr1_xy.append(i.split(",")[1]+","+i.split(",")[0])

            for i in self.coord_twr2:
                self.coord_twr2_xy.append(i.split(",")[1]+","+i.split(",")[0])

            #print(self.coord_twr1_xy)
            #print(self.coord_twr2_xy)

            return self.waypoints, self.x_coord, self.y_coord, self.coord_twr1_xy, self.coord_twr2_xy,self.init_tower,self.final_tower

        else:
            print("ERROR FILE FORMAT")