import time
import customtkinter as tk
import tkinter
import os
import urllib.request
import paho.mqtt.client as mqtt
import cv2 as cv
import numpy as np
import datetime
import torch
import base64
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import tkintermapview
import mpu
import re
import sys
from KmlExtractor import KmlExtractor
from TowerSeeker import TowerSeekerClass
from RetrunDecider import ReturnCalculator
from SimulationArduPilot import SITL


class LeftFrame:  # class

    def buildFrame(self, fatherFrame):

        self.Leftframe = tk.CTkFrame(master=fatherFrame)
        self.Leftframe.pack(side="left", pady=2, padx=2, fill="both", expand=True)

        self.Leftframe_Top = tk.CTkFrame(master=self.Leftframe)
        self.Leftframe_Top.pack(side="top", pady=2, padx=2, fill="both", expand=True)

        self.Leftframe_Bottom = tk.CTkFrame(master=self.Leftframe)
        self.Leftframe_Bottom.pack(side="bottom", pady=2, padx=2, fill="both", expand=True)

        self.Title_top = tk.CTkLabel(master=self.Leftframe_Top, text="ARCHER APP")
        self.Title_top.pack(pady=2, padx=2)

        self.entryPath = tk.CTkEntry(master=self.Leftframe_Top, placeholder_text="C:/",
                                     width=300, height=25, border_width=2, corner_radius=10)
        self.entryPath.place(relx=0.3, rely=0.3, anchor=tkinter.CENTER)
        self.folder = "/"

        self.Browse = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                   text="Browse", command=self.fileDialog)
        self.Browse.place(relx=0.8, rely=0.3, anchor=tkinter.CENTER)

        self.startFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                    text="New Flight WP", command=self.StartFP, fg_color="green")
        self.startFP.place(relx=0.2, rely=0.6, anchor=tkinter.CENTER)

        self.finishFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                     text="Close Flight Plan", command=self.FinishFP, fg_color="red")
        self.finishFP.place(relx=0.43, rely=0.6, anchor=tkinter.CENTER)
        self.finishFP.place_forget()  # Hide button option before FP is drawed
        self.finish_pressed = 0  # Counting times the 'Close FP' button has been pressed. Change path color
        self.FP_leg_counter = 1  # Counts how many FP legs have been created
        # self.FP_leg_result="X1" #Leg codes: GX, R(X+1), O(X+2), Y(X+3)... Being X FP_leg_counter value

        self.ClearFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                    text="Clear All WPs", command=self.ClearFP, fg_color="red")
        self.ClearFP.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)
        self.ClearFP.place_forget()  # Hide button option before FP is drawed

        self.DeleteWP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                     text="Delete WP", command=self.DeleteWP, fg_color="red")
        self.DeleteWP.place(relx=0.43, rely=0.7, anchor=tkinter.CENTER)
        self.DeleteWP.place_forget()  # Hide button option before FP is drawed

        self.ClearMap = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,text="Clear Map", command=self.ClearMap, fg_color="red3")
        self.ClearMap.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)
        self.ClearMap.place_forget()

        self.EditFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,text="Modify Last Leg", command=self.ModifyFP)
        self.EditFP.place(relx=0.2, rely=0.8, anchor=tkinter.CENTER)
        self.EditFP.place_forget()

        self.CloseEditFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8, text="Save Modification", command=self.save_editWP)
        self.CloseEditFP.place(relx=0.43, rely=0.8, anchor=tkinter.CENTER)
        self.CloseEditFP.place_forget()

        self.DeleteWPEdit = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0,corner_radius=8, text="Delete WP", command=self.save_delete_lastWP)
        self.DeleteWPEdit.place(relx=0.66, rely=0.8, anchor=tkinter.CENTER)
        self.DeleteWPEdit.place_forget()

        self.UploadFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0,corner_radius=8, text="Send Data", command=self.uploadFP)
        self.UploadFP.place(relx=0.66, rely=0.8, anchor=tkinter.CENTER)
        self.UploadFP.place_forget()

        self.ConnectExtBroker = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,text="Connect UAV", command=self.ConectionExt, fg_color="red")
        self.ConnectExtBroker.place(relx=0.66, rely=0.7, anchor=tkinter.CENTER)
        self.ConnectExtBroker.place_forget()

        self.Con_state = tk.CTkLabel(master=self.Leftframe_Top, text="State: Disconnected")
        self.Con_state.place(relx=0.66, rely=0.6, anchor=tkinter.CENTER)
        self.Con_state.place_forget()

        self.ConnectCamera = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0,corner_radius=8, text="CAM TEST", command=self.CameraON)
        self.ConnectCamera.place(relx=0.8, rely=0.6, anchor=tkinter.CENTER)
        self.ConnectCamera.place_forget()
        self.CancellFP = tk.CTkButton(master=self.Leftframe_Top, width=120, height=22, border_width=0, corner_radius=8,
                                      text="Cancell FP", command=self.CancellFP, fg_color="red")
        self.CancellFP.place(relx=0.43, rely=0.6, anchor=tkinter.CENTER)
        self.CancellFP.place_forget()

        self.Range_value = tk.CTkLabel(master=self.Leftframe_Top, text="FP range: 0 m")
        self.Range_value.place(relx=0.53, rely=0.9, anchor=tkinter.CENTER)
        self.Range_value.place_forget()

        self.Planning = False  # Global statement to start flight plan drawing
        self.OpenedFile = False  # Statement to enable using flight plan buttons
        self.StartFP_pressed = False  # If FP Start button has been pressed. To hide/show drone slide settings
        self.Return_statement = False  # Statement that indicates if drone has to return or not
        self.Modify_FP = False  # Statement that indicates if modification button has been pressed
        self.ConnectUAV =False # Statement that indicates if modification button has been pressed

        self.total_distance = round(0, 0)  # Total distance, initial value
        self.new_suggested = 0  # New suggested WP variable. Defined here

        self.model = torch.hub.load('ultralytics/yolov5', 'custom',path='C:/Users/USUARIO/Documents/TFG\MISSION PLANNER/model/best.pt') #Load trained model weights file

        if self.internet_connection():
            self.Namepoint = []  # Vector that will host each tower Name from KmlExtractor class
            self.Xpoint = []  # Vector that will host each tower Xpos from KmlExtractor class
            self.Ypoint = []  # Vector that will host each tower Ypos from KmlExtractor class
            self.pathLine = []  # Vector that will host all path lines
            self.XYpoint_twr1 = []  # Vector of (x,y) tuples for Tower A. To draw line path between TWR_A-TWR_B
            self.XYpoint_twr2 = []  # Vector of (x,y) tuples for Tower B
            self.init_twr = []  # List of tower names A (kml description)
            self.final_twr = []  # List of tower names B (kml description)
            self.final_path=[] #Final path list solution that will be send to the simulation

            self.map_widget = tkintermapview.TkinterMapView(self.Leftframe_Bottom, width=700, height=500,
                                                            corner_radius=8)
            # self.map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            # self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
            # self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)  # google satellite

            if self.entryPath.get() == "":
                self.map_widget.set_zoom(17)
                self.map_widget.set_position(41.2755, 1.9872)  # Default map position

            self.KmlExtractorClass = KmlExtractor()
            self.icon_path_counter = False  # Statement to control if an icon has been already found

        else:
            messagebox.showinfo("Internet", "Not connected")  # Connection to the internet message
        #self.map_widget.canvas.bind("<Motion>", self.drag)  # Mouse motion

    def internet_connection(self):  # Function that detects if we have connection to internet. Otherwise MapViewwer will not show the map
        try:
            urllib.request.urlopen('https://google.com')
            return True
        except:
            return False

    def fileDialog(self):

        if self.folder == "/":
            self.folder = filedialog.askopenfilename(initialdir="/", title="Open file",
                                                     filetypes=((".kml", "*.kml"), ('.kmz', '*.kmz')))
        else:
            self.directory_path = os.path.dirname(self.folder)
            self.folder = filedialog.askopenfilename(initialdir=self.directory_path, title="Open file",
                                                     filetypes=((".kml", "*.kml"), ('.kmz', '*.kmz')))
            self.RightFrameClass.Clear_Table()  # Clear all flight plan from table

        # print("Folder Path: ", self.folder)
        self.entryPath.delete(0, 'end')  # Clean folder path
        self.finish_pressed = 0  # Reset leg color sequence
        self.markerFP_pos=0 #Create/Reset var that will control each marker inside the list
        self.path_accum=0 #Accumulated path created in all FPs

        # Case when filedialog window is cancelled
        if self.folder != "":
            self.OpenedFile = True
            self.entryPath.insert(0, self.folder)  # Insert new path into text box
            self.path = self.folder

        else:
            self.path = ""

        # Reset of the MAP. Reload it
        self.map_widget.destroy()
        self.map_widget = tkintermapview.TkinterMapView(self.Leftframe_Bottom, width=700, height=500, corner_radius=8)
        self.map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        # self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
        # self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",  max_zoom=22)  # google satellite
        # Load icons
        if self.icon_path_counter == False:
            self.towerseekerclass = TowerSeekerClass()
            # Only once, because it takes a lot of time. When we have a path, the other icons should be together to find them easier

            #Thread(target=self.LoadingBar()).start()

            self.icon_path = self.towerseekerclass.find_icon("C:/Users/USUARIO",
                                                             "tower_iconB.png")  # Look for the icon file in the system
            # self.icon_path = self.towerseekerclass.find_icon("C:/Users/USUARIO/Documents/TFG/MISSION PLANNER","tower_iconB.png")  # Look for the icon file in the system

            self.icon_path_counter = True

            self.base_path, self.ext = os.path.splitext(
                self.icon_path)  # Lets divide between the root path and its file
            self.path_icon = os.path.split(self.base_path)
            self.icon_path = self.path_icon[0]  # Delete specific file and save rest of icon path
            # print("ICONS PATH: ", self.icon_path)

        else:
            pass

        self.map_widget.add_left_click_map_command(self.left_click_event)  # Setup LH click command

        self.tower_iconWH = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/tower_iconWH.png")).resize((50, 50)))  # Define tower icon
        self.tower_iconB = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/tower_iconB.png")).resize((50, 50)))  # Define tower icon
        self.tower_iconBL = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/tower_iconBL.png")).resize((50, 50)).resize(
                (50, 50)))  # Define tower icon
        self.tower_iconRE = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/tower_iconRE.png")).resize((50, 50)).resize(
                (50, 50)))  # Define tower icon

        self.point_iconWH = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/pointWH.png")).resize((50, 50)))  # Define point icon
        self.point_iconB = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/pointB.png")).resize((50, 50)))  # Define point icon
        self.point_iconBL = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/pointBL.png")).resize((50, 50)).resize((50, 50)))  # Define point icon
        self.point_iconRE = ImageTk.PhotoImage(
            Image.open(self.icon_path + str("/pointRE.png")).resize((50, 50)).resize((50, 50)))  # Define point icon

        if self.path != "":
            self.Namepoint, self.Xpoint, self.Ypoint, self.XYpoint_twr1, self.XYpoint_twr2, self.init_twr, self.final_twr = self.KmlExtractorClass.KmlExtractor(
                self.path)  # Executing converter .kmz to .kml class
            # self.Namepoint, self.Xpoint, self.Ypoint, self.XYpoint_twr1, self.XYpoint_twr2 = self.KmlExtractorClass.KmlExtractor()

            # print("Namepoint: ", self.Namepoint)
            # print("Xpoint: ", self.Xpoint)
            # print("Ypoint: ", self.Ypoint)
            # print("TowerA: ", self.XYpoint_twr1)
            # print("TowerB: ", self.XYpoint_twr2)

            self.map_widget.set_position(float(self.Xpoint[0]), float(self.Ypoint[0]))  # Initial map position
            self.map_widget.set_zoom(15)

            i = 0
            for item in self.Xpoint:  # PLOT OF EACH TOWER WITH ITS CORRESPONDING NAME
                self.marker = self.map_widget.set_marker(float(self.Xpoint[i]), float(self.Ypoint[i]),
                                                         text=self.Namepoint[i], text_color="white", font="Helvetica",
                                                         icon=self.tower_iconB)
                # self.marker = self.map_widget.set_marker(float(self.Xpoint[self.i]), float(self.Ypoint[self.i]), text=self.Namepoint[self.i], text_color="white",font="Helvetica")  # position marker settings

                i = i + 1

            self.Lines = []  # List of power lines on the map
            self.coord_twr1_x = []
            self.coord_twr1_y = []
            self.coord_twr2_x = []
            self.coord_twr2_y = []

            for i in self.XYpoint_twr1:
                self.coord_twr1_x.append(i.split(",")[0])
                self.coord_twr1_y.append(i.split(",")[1])
            for i in self.XYpoint_twr2:
                self.coord_twr2_x.append(i.split(",")[0])
                self.coord_twr2_y.append(i.split(",")[1])

            self.i = 0
            for item in self.XYpoint_twr1:  # PLOT OF POWER LINES BETWEEN TOWERS
                self.Lines = self.map_widget.set_path(
                    [(float(self.coord_twr1_x[self.i]), float(self.coord_twr1_y[self.i])),
                     (float(self.coord_twr2_x[self.i]), float(self.coord_twr2_y[self.i]))], color='white', width=5)

                self.i = self.i + 1
            self.initial_path_len=len(self.map_widget.canvas_path_list)

            # Function: looking for relation between position and tower name when adding new waypoint
            self.towerseekerclass.load_data(self.Namepoint, self.Xpoint, self.Ypoint, self.init_twr, self.final_twr)  # Loading tower data once

        else:
            self.entryPath.insert(0, "C:/")
            self.map_widget.set_zoom(17)
            self.map_widget.set_position(41.2755, 1.9872)  # Default map position

        #Create a directory to save all images from the inspection every time a new file is opened
        self.now = datetime.datetime.now().strftime("%H.%M.%S")
        self.path_main_directory = "C:/Users/USUARIO/Pictures/INSPECTION " + str(datetime.date.today()) + " " + str(self.now)
        os.mkdir(self.path_main_directory)  # Create directory for each new Leg created

    def left_click_event(self, position):
        # messagebox.showinfo(title="Information", message=position)
        pass

    def setRightFrame(self, RightFrameClass):
        self.RightFrameClass = RightFrameClass  # RHFrame function

    def drag(self, e):  # CAN BE DELETED
        # self.x0 = e.x
        # self.y0 = e.y
        # print(self.x0, self.y0)
        pass

    def StartFP(self):

        if self.OpenedFile is True:
            if self.Planning is False:
                self.Planning = True  # Start FP, add points
                self.Return_statement = False  # Initial statement to return back the drone
                self.warning_message_ret = False  # Statement if warning message appeared before
                self.StartFP_pressed = True
                self.countFP = 0  # Number of added WP by user (ID)
                self.markerFP_pos=0 #Position of marker inside list
                self.hover_time = 0  # Default hover spent time. Set when adding new WP in fucntion return_wp from returnDecider
                self.added_new_paths=0 #Count how many paths had been added
                self.positionsFP = []
                self.markersFP = []  # Tuple of markers in a FP
                self.pathsFP = []  # New vector of paths
                self.counterWP = []  # WP counter list (NOT USED)
                self.distanceWP = []  # List to hold all final distances between WPs
                self.operationFP = []  # List of description operation for each segment
                self.cruise_time = []  # List of theoretical flight cruise timings
                self.suggested_markers = []
                self.markers_added=[] #List of number of number of markers added every time
                self.suggestions_pos = [] #Positions of suggested markers in self.markersFP list

                self.ClearMap.place_forget()  # Hide clear map option when creating new FP

                self.Range_value.configure(text="FP range: 0 m")  # Reset label value
                self.RightFrameClass.ShowHideSettings(self.StartFP_pressed)

                self.CancellFP.place(relx=0.43, rely=0.6, anchor=tkinter.CENTER)
                self.map_widget.add_right_click_menu_command(label="Add WP", command=self.add_marker,pass_coords=True)  # RH button menu
            else:
                messagebox.showwarning("Note", "Actual flight plan must be closed!")
        else:
            messagebox.showwarning("Note", "Open a file to start")

    def FinishFP(self):

        if self.Planning == True or self.Return_statement == True:
            # Only if New Flight Plan Button is clicked this function is available
            if self.countFP == 0:
                messagebox.showwarning("Note",
                                       "No waypoints added!")  # Any point has been already added. FP can't be closed
            elif self.countFP > 1:
                # To avoid closing a null list of FP

                self.operationFP.append("RETURN FROM WP" + str(self.countFP))
                print(self.operationFP)

                if self.warning_message_ret == True:  # In case of calling the funciton from warning message [Return drone to origin]
                    # Don't show warning message again
                    self.warning_message = True
                else:  # In case of calling the function by pressing the button
                    self.warning_message = messagebox.askokcancel("Close Flight Plan",
                                                                  "Are you sure?")  # If 'yes' returns True, if 'not' returns False statement

                if self.warning_message:
                    # Warning message before closing FP.
                    self.Planning = False
                    self.Return_statement = False
                    self.warning_message_ret = False
                    self.WP_ident = 1
                    self.ClearMap.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)
                    self.EditFP.place(relx=0.2, rely=0.8, anchor=tkinter.CENTER)
                    self.ConnectExtBroker.place(relx=0.66, rely=0.7, anchor=tkinter.CENTER)

                    #First delete added paths:
                    i=self.added_new_paths
                    while i>0:
                        self.map_widget.canvas_path_list[-1].delete()  # Go deleting last item from list
                        #print(len(self.map_widget.canvas_path_list))
                        self.added_new_paths=self.added_new_paths-1
                        i=i-1
                    i = 0
                    while i < len(self.markersFP):
                        self.map_widget.canvas_marker_list[-1].delete()  # Go deleting last item from list
                        i = i + 1

                    #Update new path color
                    if self.finish_pressed == 0:
                        color='lawngreen'
                    elif self.finish_pressed == 1:
                        color='red'
                    elif self.finish_pressed == 2:
                        color='darkorange'
                    elif self.finish_pressed == 3:
                        color='gold'
                        self.FP_leg_result = "Y" + str(self.FP_leg_counter)  # Creating FP code
                    else:
                        pass

                    i = 1
                    while i < len(self.positionsFP):
                        self.pathFP = self.map_widget.set_path([self.positionsFP[i-1],self.positionsFP[i]], color=color,width=5)  # Draw all the path with all the positions stores in vector
                        self.added_new_paths=self.added_new_paths+1
                        i = i + 1

                    #print("UPDATED ACTUAL NUM PATH", self.added_new_paths)

                    #Changing color of leg to show that has been closed
                    for item in self.positionsFP:
                        self.map_widget.set_marker(float(item[0]), float(item[1]), text=self.WP_ident,text_color="white", font="Helvetica", icon=self.point_iconWH)
                        self.WP_ident = self.WP_ident + 1

                    self.RightFrameClass.Insert_SecondTable(self.operationFP, self.FP_leg_result, self.finish_pressed,self.speed, self.hover_time, self.cruise_time,self.distanceWP)  # Fill Table2 with detailed info about each FP instruciton
                    self.save_last_leg(self.positionsFP,self.countFP,self.operationFP, self.finish_pressed,self.speed, self.cruise_time,self.distanceWP) #Save last leg info before deleting all data

                    self.RightFrameClass.Update_SecondTable()

                    if self.finish_pressed == 3:
                        self.finish_pressed = 0
                    else:
                        self.finish_pressed = self.finish_pressed + 1  # Counting pressed times. To change color of different FP legs

                    self.pathsFP.append(self.pathFP)
                    self.ClearFP.place_forget()  # Hide button when a FP is finally closed
                    self.DeleteWP.place_forget()  # Hide button when a FP is finally closed
                    self.finishFP.place_forget()  # Hide button when a FP is finally closed

                    self.ClearMap.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)  # Show again clear map option

                    self.countFP = 0
                    self.distanceWP.clear()  # Delete list values
                    self.distanceWP = []
                    self.total_distance = 0
                    self.markerFP_pos=0
                    self.map_widget.right_click_menu_commands.pop()  # Delete last "Add WP" option

                    self.StartFP_pressed = False
                    self.RightFrameClass.ShowHideSettings(self.StartFP_pressed)

                    self.FP_leg_counter = self.FP_leg_counter + 1  # FP created. Rise count for next one

                else:
                    pass
            else:
                # Case of having only one single point
                messagebox.showwarning("Invalid FP", "Must have at least 2 WP to be closed")
        else:
            pass

    def DeleteWP(self):
        # Delete last WP item from a FP

        self.countFP = self.countFP - 1  # Subtract marker item number

        if self.countFP > 0:
            self.DeleteWP.place(relx=0.43, rely=0.7, anchor=tkinter.CENTER)  # Button appears when there are enough waypoints to remove

            #Take info from number of last WP registered. This will be removed
            #Decide if we have to remove suggesion markers and added amrkers or only added markers

            #print("MRKRS LIST: ", self.markersFP)
            #print("ADDED LIST: ", self.markers_added)

            #[FIND A WAY TO SOLVE THIS PROBLEM!!!]
            if self.markers_added[-1]==1 and self.markers_added[-2]>1:
                self.map_widget.canvas_marker_list[-1].delete()
                self.markerFP_pos=self.markerFP_pos-1
                self.markers_added.pop()
                self.markersFP.pop()

                i=0
                while i<self.markers_added[-1]:
                    self.map_widget.canvas_marker_list[-1].delete()
                    self.markerFP_pos = self.markerFP_pos - 1
                    self.markersFP.pop()
                    i=i+1
                self.markers_added.pop()

            elif self.markers_added[-1] == 1 and self.markers_added[-2] == 1:
                self.map_widget.canvas_marker_list[-1].delete()
                self.markerFP_pos = self.markerFP_pos - 1
                self.markers_added.pop()
                self.markersFP.pop()

            print("MRKRS LIST DEL: ",self.markersFP)
            print("ADDED LIST DEL: ", self.markers_added)

            #self.map_widget.canvas_marker_list[-1].delete()  # Deletes marker item in canavs list
            self.map_widget.canvas_path_list[-1].delete()  # Deletes path items in canavs list
            self.added_new_paths=self.added_new_paths-1

            self.total_distance = self.total_distance - self.distanceWP[-1]  # Deleting the last distance register to update total value
            self.Range_value.configure(text="FP range: " + str(round(self.total_distance, 1)) + " m")  # Update actual range
            del self.positionsFP[-1]
            self.RightFrameClass.RemoveWP_Table()  # Delete WP from table
            #print("items: ", self.countFP)
            print(self.positionsFP)
            self.distanceWP.pop()
            self.operationFP.pop()  # Delete last register of instruction in the list
            self.operationFP.pop()  # Idem (twice because of the hover and cruise info)
            # print("Total distance: ",str(self.total_distance))
            self.Return_statement, self.LastWP, self.hover_time, self.cruise_time = self.ReturnWP.return_wp(self.distanceWP, self.speed,self.autonomy)  # Update time/dist lists for Table2 filling (later) when closing FP

            # Case of autonomy time reached. Drone must return, FP cant be extended until last WP is deleted
            if self.Return_statement == True:
                self.Planning = True  # Reset statements
                self.Return_statement = False  # Reset statements

            if self.countFP == 1:
                self.DeleteWP.place_forget()  # Hide button when a FP has a single point
                self.finishFP.place_forget()
            else:
                pass

        else:
            pass

    def ClearFP(self):

        # Function to clean up all FP created
        self.clear_warning_message = messagebox.askokcancel("Clear Flight Plan",
                                                            "Are you sure?")  # If 'yes' returns True, if 'not' returns False statement
        if self.clear_warning_message:
            self.countFP = 0

            i = 0
            while i < len(self.markersFP):
                self.map_widget.canvas_marker_list[-1].delete()
                i = i + 1

            for path in self.pathsFP:
                path.delete()
            self.pathsFP = []
            self.markers_added.clear()
            self.markersFP.clear()
            self.markersFP=[]
            self.markersFP = []
            self.distanceWP.clear()  # Delete list values
            self.distanceWP = []
            self.operationFP.clear()
            self.operationFP = []
            self.total_distance = 0
            self.markerFP_pos=0
            self.finish_pressed = 0
            del self.positionsFP  # Way to delete tuple objects
            self.Planning = False
            self.ClearFP.place_forget()  # Hide button when all FPs had been removed
            self.DeleteWP.place_forget()  # Hide button when all FPs had been removed
            self.finishFP.place_forget()

            self.StartFP_pressed = False
            self.RightFrameClass.ShowHideSettings(self.StartFP_pressed)

            self.Range_value.configure(text="FP range: 0 m")  # Actual range reset

            self.finish_pressed = self.RightFrameClass.RemoveFP_Table()  # Remove FP from table. Returns value to change color of the next path

        else:
            pass

    def ClearMap(self):

        self.clear_warning_message = messagebox.askokcancel("Clear Map",
                                                            "Are you sure?")  # If 'yes' returns True, if 'not' returns False statement
        if self.clear_warning_message:
            self.countFP = 0
            for path in self.pathsFP:
                path.delete()
            self.pathsFP = []
            self.markersFP.clear()
            self.distanceWP.clear()  # Delete list values
            self.distanceWP = []
            self.operationFP.clear()
            self.operationFP = []
            self.total_distance = 0
            self.finish_pressed = 0
            self.markerFP_pos=0
            self.FP_leg_counter = 1  # Reset value
            del self.positionsFP  # Way to delete tuple objects
            self.Planning = False
            self.OpenedFile = False
            self.ClearFP.place_forget()  # Hide button when all FPs had been removed
            self.DeleteWP.place_forget()  # Hide button when all FPs had been removed
            self.finishFP.place_forget()
            self.map_widget.delete_all_marker()  # Clear all map of markers
            self.map_widget.delete_all_path()  # Clear all map of paths

            self.StartFP_pressed = False
            self.RightFrameClass.ShowHideSettings(self.StartFP_pressed)

            self.Range_value.configure(text="FP range: 0 m")  # Actual range reset
            self.RightFrameClass.Clear_Table()  # Clear all flight plan from table
            self.map_widget.right_click_menu_commands.clear()  # Clear menu list
        else:
            pass

    def CancellFP(self):
        self.clear_warning_message = messagebox.askokcancel("Cancell Flight Plan", "Are you sure?")

        if self.clear_warning_message:
            self.Planning = False
            self.StartFP_pressed = False
            self.RightFrameClass.ShowHideSettings(self.StartFP_pressed)
            self.CancellFP.place_forget()
            self.finishFP.place_forget()
        else:
            pass

    def add_marker(self, positionFP):
        # self.map_widget.canvas.bind("<Motion>",self.mouse_pos)  # Captures mouse movement on canvas. Asociated to fucntion mouse_pos

        if self.Planning:

            self.CancellFP.place_forget()
            self.ClearFP.place(relx=0.2, rely=0.7, anchor=tkinter.CENTER)
            self.countFP = self.countFP + 1

            # Show suggested points option only if switch is activated
            if self.RightFrameClass.switch_event() == True:
                self.resXLH = []
                self.resYLH = []
                self.resXRH = []
                self.resYRH = []

                self.TWRName, self.dist_twr_wp = self.towerseekerclass.name_seeker(positionFP)  # Ask for tower ident
                self.set_dist_twr = int(self.RightFrameClass.setDist_TWR.get())
                self.resXLH, self.resYLH, self.resXRH, self.resYRH = self.towerseekerclass.equivalent_distance(self.set_dist_twr)
                # PASSING LIST OF TOWER1/TOWER2 CONNECTED BY THE POWERLINE

                i = 0
                while i < len(self.resXLH):
                    #Plotting suggestion markers. On LH and RH side of the next tower
                    self.map_widget.set_marker(float(self.resXLH[i]), float(self.resYLH[i]), icon=self.point_iconRE)
                    self.markerFP_pos = self.markerFP_pos + 1
                    self.markersFP.append(self.markerFP_pos)
                    self.suggestions_pos.append(self.markerFP_pos)#Save position of suggested marker in list
                    self.map_widget.set_marker(float(self.resXRH[i]), float(self.resYRH[i]), icon=self.point_iconRE)
                    self.markerFP_pos = self.markerFP_pos + 1
                    self.markersFP.append(self.markerFP_pos)
                    self.suggestions_pos.append(self.markerFP_pos)  # Save position of suggested marker in list
                    i = i + 1
                #print("suggestion mrks pos: ",self.suggestions_pos)
                if i!=0:
                    self.markers_added.append(i*2) #Num markers plot in the map at a moment
                else:
                    pass

                Xpoint, Ypoint = self.towerseekerclass.get_distance(positionFP)  # If WP is too close to suggestion, convert the WP to the exact point of the suggestion
                if Xpoint == -1 or Ypoint == -1:
                    #Don't change WP position
                    self.position_actual = positionFP
                    self.map_widget.set_marker(positionFP[0], positionFP[1], text=self.countFP,text_color="white", font="Helvetica",icon=self.point_iconBL)
                    self.markerFP_pos = self.markerFP_pos + 1
                    self.markersFP.append(self.markerFP_pos)
                    #print("marker-pos: ",self.markerFP_pos)
                    self.markers_added.append(1)  # Num markers plot in the map at a moment
                else:
                    # Change WP position to suggestion position
                    self.position_actual = (Xpoint, Ypoint)
                    self.map_widget.set_marker(Xpoint, Ypoint, text=self.countFP, text_color="white",font="Helvetica", icon=self.point_iconBL)
                    self.markerFP_pos = self.markerFP_pos + 1
                    self.markersFP.append(self.markerFP_pos)
                    #print("marker-pos: ",self.markerFP_pos)
                    self.markers_added.append(1)  # Num markers plot in the map at a moment
                #print("MRKS: ", self.markersFP)
            else:
                #SUggestion switch to OFF
                self.countSuggested = 0
                self.new_suggested=0
                # self.markerFP = self.map_widget.set_marker(positionFP[0], positionFP[1], text=self.countFP,text_color="blue", marker_color_circle="white", marker_color_outside="black")
                self.map_widget.set_marker(positionFP[0], positionFP[1], text=self.countFP,text_color="white", font="Helvetica", icon=self.point_iconBL)
                self.markerFP_pos = self.markerFP_pos + 1
                self.markersFP.append(self.markerFP_pos)
                #print("marker-pos: ",self.markerFP_pos)
                self.position_actual = positionFP
                self.markers_added.append(1)  # Num markers plot in the map at a moment
                #print("MRKS: ", self.markersFP)

            if self.countFP > 1:  # If counter >1 then we draw a line between the actual marker and the last in the vector
                # Button appears when there are enough waypoints to remove
                self.DeleteWP.place(relx=0.43, rely=0.7, anchor=tkinter.CENTER)
                self.finishFP.place(relx=0.43, rely=0.6,anchor=tkinter.CENTER)  # Clear All button appears when first marker is set
                self.pathFP = self.map_widget.set_path([self.positionsFP[-1], self.position_actual], color='blue',width=3)  # Draw line path
                self.added_new_paths=self.added_new_paths+1

                # Creates path line between actual positionFP(x,y) and last positionFP(x,y)
                self.pathsFP.append(self.pathFP)  # Save elements (path sections) into a list
                self.X1, self.Y1 = self.positionsFP[-1]  # Divide tuple value in x,y independent variables. Float
                self.X0, self.Y0 = self.position_actual  # Divide tuple value in x,y independent variables. Float

                self.dist = mpu.haversine_distance(self.positionsFP[-1],self.position_actual) * 1000  # Haversine distance between last marker and actual one (m)

                # Getting data from name_seeker function from TowerSeeker
                self.operationFP.append("CRUISE. FROM WP" + str(self.countFP - 1) + " TO WP" + str(
                    self.countFP))  # Saves expected drone operation to list
                self.operationFP.append("HOVER. SHOT " + str(self.TWRName))  # Saves expected drone operation to list
                # print(self.operationFP)

                self.total_distance = round(self.dist + self.total_distance, 2)  # Sum of accumulate total distance
                self.distanceWP.append(round(self.dist, 2))  # Save accumulate distance in list

                self.ReturnWP = ReturnCalculator()  # Initialize object
                self.speed = self.RightFrameClass.SetSpeed(
                    self.RightFrameClass.setSpeed.get())  # Get speed slider settings
                self.autonomy = self.RightFrameClass.SetAutonomy(
                    self.RightFrameClass.setAutonomy.get())  # Get autonomy slider settings

                self.Return_statement, self.LastWP, self.hover_time, self.cruise_time = self.ReturnWP.return_wp(
                    self.distanceWP, self.speed, self.autonomy)
                # Function that will return last WP to be reached and also the statement

                if self.Return_statement == True:  # Just do it once. Do not let adding more WP!
                    # print("FLIGHT PLAN CAN'T BE EXTENDED FURTHER THAN WP" + str(self.LastWP))
                    self.distanceWP.pop()  # Delete last element added on the list, because autonomy time is reached
                    self.operationFP.pop()  # Idem
                    self.operationFP.pop()  # Idem (twice because of the hover and cruise info)
                    # self.operationFP.append("RETURN FROM WP"+str(self.countFP))
                    self.Planning = False  # Disable function of FP building
                    """
                    i = 0
                    while i < self.new_suggested:
                        self.map_widget.canvas_marker_list[-1].delete()  # Deletes marker suggestedLH
                        self.map_widget.canvas_marker_list[-1].delete()  # Deletes marker suggestedRH
                        i = i + 1
                    self.map_widget.canvas_marker_list[-1].delete()  # Deletes last marker blue
                    self.map_widget.canvas_path_list[-1].delete()  # Deletes path items in canavs list
                    """
                    self.map_widget.canvas_path_list[-1].delete()  # Deletes path items in canavs list
                    self.countFP = self.countFP - 1  # Subtract marker item number
                    self.total_distance = round(abs(self.total_distance - self.dist),
                                                2)  # Subtract non desired WP. Resulting as the absolute value

                    self.warning_message_ret = messagebox.askokcancel("Warning",
                                                                      "Maximum flight time reached. Close FP?")
                    if self.warning_message_ret:  # Then close FP
                        self.FinishFP()  # Go to specific function
                    else:
                        pass
                else:
                    # print("Total distance: " + str(self.total_distance))
                    self.Range_value.configure(text="FP range: " + str(
                        round(self.total_distance, 2)) + " m")  # Update labell. Travelled dist by the drone
            else:
                self.TWRName, self.dist_twr_wp = self.towerseekerclass.name_seeker(positionFP)  # Get tower name
                self.towerseekerclass.fill_historic_twrs() #Keep updated the hist travelled towers list
                self.operationFP.append("TAKE-OFF. MOVE TO WP1")
                self.operationFP.append("HOVER. SHOT " + str(self.TWRName))

                self.dist = 0  # First waypoint has distance 0, there are no more points
                self.total_distance = round(0, 0)
                self.distanceWP.append(round(self.dist, 0))
                self.Range_value.configure(text="FP range: 0 m")

            if self.Return_statement == False and self.Planning == True:  # Building the FP

                self.positionsFP.append(self.position_actual)  # Save all positionFP(x,y) to list

                self.TWRName, self.dist_twr_wp = self.towerseekerclass.name_seeker(self.position_actual)
                self.towerseekerclass.fill_historic_twrs()  # Keep updated the hist travelled towers list
                # Given actual position, name seeker returns closest tower name and distance to WP.
                # Data was loaded at folderDialog() function

                if self.finish_pressed == 0:  # Create code of FP legs
                    self.FP_leg_result = "G" + str(self.FP_leg_counter)
                elif self.finish_pressed == 1:
                    self.FP_leg_result = "R" + str(self.FP_leg_counter)
                elif self.finish_pressed == 2:
                    self.FP_leg_result = "O" + str(self.FP_leg_counter)
                elif self.finish_pressed == 3:
                    self.FP_leg_result = "Y" + str(self.FP_leg_counter)

                self.RightFrameClass.Insert_Table(positionFP, self.dist, self.TWRName, self.countFP, self.dist_twr_wp,
                                                  self.finish_pressed,
                                                  self.FP_leg_result)  # Insert new wayoint to table
            else:
                pass




        else:
            if self.Planning == False and self.Return_statement == True:
                self.warning_message_ret = messagebox.askokcancel("Warning", "Maximum flight time reached. Close FP?")
                if self.warning_message_ret:  # Close FP
                    self.FinishFP()  # Go to function
                else:
                    pass
            else:
                messagebox.showwarning("Note", "Click to 'New Flight WP'")

    def ModifyFP(self):
        self.EditFP.place_forget()
        self.CloseEditFP.place(relx=0.43, rely=0.8, anchor=tkinter.CENTER)
        self.DeleteWPEdit.place(relx=0.66, rely=0.8, anchor=tkinter.CENTER)

        i = 1
        while i < len(self.positionsFP):
            self.pathFP = self.map_widget.set_path([self.positionsFP[i - 1], self.positionsFP[i]], color='cyan3',width=5)  # Draw all the path with all the positions stores in vector
            self.added_new_paths = self.added_new_paths + 1
            i = i + 1
        print("MOD ACTUAL NUM PATH", self.added_new_paths)

        self.saved_new_positions=[]
        self.final_leg = []
        tower_id=1
        self.ident_code=1 #Counter for the different modified elements added. For each leg
        self.ident_integer=0
        self.ident_codes_historic=[]
        self.saved_id=[]
        self.counter_mod_added=0 #Counter of mod markers added
        self.counter_mod_path_added=0 #Counter of mod paths added
        for item in self.saved_positions: #Change color to indicate modification mode is ON
            modified_markers=self.map_widget.set_marker(float(item[0]),float(item[1]), text=tower_id,text_color="cyan3", font="Helvetica", icon=self.point_iconRE)
            self.saved_id.append(tower_id)
            tower_id=tower_id+1
        self.map_widget.add_right_click_menu_command(label="Add New WP", command=self.edit_WP,pass_coords=True)  # RH button menu

        j = 1
        # Looking for a format list: (ID, COORDS)
        for item in self.base_values:
            self.final_leg.append((j, item))
            j = j + 1

    def save_last_leg(self,positionsFP,countFP,operationFP,color_code,speed,cruise_time,distanceWP):
        self.saved_positions=[] #Waypoints positions
        self.saved_ids=[] #Waypoints IDs
        self.saved_operations=[] #Actual drone instructions
        self.saved_speed=[] #Drone av cruise speed
        self.saved_distance=[] #Total travelled distance
        self.historic_modified=[] #List of actual WP IDs travelled
        self.base_values=[]

        self.saved_positions=positionsFP
        self.base_values=positionsFP
        self.saved_ids=countFP
        self.saved_operations=operationFP
        self.path_color=color_code
        self.airspeed=speed

        for item in positionsFP:
            self.final_path.append(("T",item)) #Build list of points for simulation. T means that the point has a tower to inspect

    def edit_WP(self,new_WP):

        twr1_id,twr1_pos,twr2_id,twr2_pos=self.towerseekerclass.find_sequence(new_WP,self.saved_positions,self.saved_id) #Getting values of AFT/FWD towers
        if twr1_id<=twr2_id:
            integer_value_id=twr1_id
        else:
            integer_value_id = twr2_id
        found=False #Statement when finding code saved before
        #Calculate the corresponding decimal value. EX: 1.X, where X is a sequential ID number
        i=0
        while (i <len(self.ident_codes_historic)) and found!=True:
            if self.ident_codes_historic[i][0]==integer_value_id:
                self.ident_code = int(self.ident_codes_historic[i][1]) + 1  # Increase in one
                self.ident_codes_historic[i] = (integer_value_id, self.ident_code)  # Update list
                found=True
            i=i+1

        if found==False:
            #Calculate the corresponding decimal value. EX: 1.X, where X is a sequential ID number
            self.ident_code=1
            self.ident_codes_historic.append((integer_value_id, self.ident_code))
        else:
            pass
        #print("HISTORIC: ",self.ident_codes_historic)
        ident_code=str(integer_value_id)+"."+str(self.ident_code) #Build up the full ID code for every added WP.
        self.int_val = integer_value_id  # Global variable int ID
        self.map_widget.set_marker(float(new_WP[0]), float(new_WP[1]), text=ident_code,text_color="cyan3", font="Helvetica", icon=self.point_iconRE)
        self.counter_mod_added=self.counter_mod_added+1 #New point added
        self.identifier_code=ident_code

        #All WP ordered process. Format (ID, COORDS)
        quit=False
        j=0
        i=0
        while i<len(self.final_leg) and quit!=True:
            #Strategy: Find the next int value and save the new ID before to achive a logic seq order
            if (self.final_leg[i][0]==integer_value_id+2 and self.final_leg[-1][0]!=integer_value_id+1):
                self.final_leg.insert(j-1,(ident_code,new_WP))
                quit=True
                #print("Found. Index: ",j-1,"//INT VALUE+1 ",integer_value_id+2,"//ITEM[0] ",item[0])

            elif (self.final_leg[-1][0]==integer_value_id+1):
                #Case of last value in the list
                self.final_leg.insert(len(self.final_leg)-1, (ident_code, new_WP))
                quit = True
            i=i+1
            j = j+1
        #print(self.final_leg)

    def save_editWP(self):
        warning_message = messagebox.askokcancel("Close Modification Mode","Are you sure?")  # If 'yes' returns True, if 'not' returns False statement
        if warning_message:
            self.CloseEditFP.place_forget()
            self.DeleteWPEdit.place_forget()
            # First Delete previous path and markers
            i=0
            while i < len(self.saved_positions):
                self.map_widget.canvas_marker_list[-1].delete()
                i = i + 1

            # First delete added paths:
            i = self.added_new_paths
            while i > 0:
                self.map_widget.canvas_path_list[-1].delete()  # Go deleting last item from list
                self.added_new_paths = self.added_new_paths - 1
                i = i - 1

            #Now proceed building the new solution
            #White marker
            for item in self.final_leg:
                self.map_widget.set_marker(float(item[1][0]), float(item[1][1]), text=item[0], text_color="white",font="Helvetica", icon=self.point_iconWH)

            # Proper path painting
            coords=[]
            for item in self.final_leg:
                coords.append(item[1])
            # Update new path color
            if self.path_color == 0:
                color = 'lawngreen'
            elif self.path_color == 1:
                color = 'red'
            elif self.path_color == 2:
                color = 'darkorange'
            elif self.path_color == 3:
                color = 'gold'
            else:
                pass

            i=1
            while i<len(coords):
                self.map_widget.set_path([coords[i-1],coords[i]], color=color,width=5)  # Draw all the path with all the positions stores in vector
                self.path_accum=self.path_accum+1
                i=i+1

            self.added_new_paths=0 #Reset counter

            self.map_widget.right_click_menu_commands.pop() #Delete last menu command from menu list
            #self.RightFrameClass.Update_SecondTable(self.final_leg)

            #Prepare path list to be sent to simulator
            self.final_path.clear() #Delete used list
            for item in self.final_leg:
                #print(item)
                pattern=r'^\d{1}.\d{1}$' #pattern to be matched "X.X"
                res = self.check_pattern(pattern,str(item[0]))
                #print(res)

                if res==1:
                    #Pattern matches. Cruise/Obstacle avoidance point
                    self.final_path.append(("C", item[1]))
                elif res==0:
                    # Pattern doesnt match. Tower point
                    self.final_path.append(("T", item[1]))

            #print("LIST FINAL_LEG: ", self.final_leg)
            #print("FINAL PATH: ",self.final_path)
        else:
            pass

    def save_delete_lastWP(self):

        if self.counter_mod_added>1:
            self.map_widget.canvas_marker_list[-1].delete()
            self.counter_mod_added = self.counter_mod_added - 1
            i = 0
            while (i < len(self.ident_codes_historic)):
                if self.ident_codes_historic[i][0] == self.int_val: #Update historic list of IDs
                    val=str(self.int_val)+"."+str(self.ident_code)
                    for item in self.final_leg:
                        print(item[0], val)
                        if str(item[0]) == str(val):
                            self.final_leg.remove(item)
                    subtract_dec = int(self.ident_codes_historic[i][1]) - 1  # Decrease in one
                    self.ident_codes_historic[i] = (self.int_val, str(subtract_dec))  # Update list
                i=i+1
            print(self.final_leg)
            if self.ident_code>1:
                self.ident_code=self.ident_code-1
            else:
                pass
        else:
            pass

    def uploadFP(self):
        """#print("FINAL FP: ", self.saved_positions)
        altitude = 5 #Altitude in meters
        # Send list of positions and start simulation
        ArduPilotSim = SITL()
        #SimulationFlight = ArduPilotSim.Simulate(self.saved_positions, self.airspeed, altitude)
        SimulationFlight = ArduPilotSim.Simulate(self.final_path, self.airspeed, altitude)"""

        self.client.publish("TT_Dashboard/autopilotService/setWaypoints",str(self.final_path))  # Publish inspection leg to the connection to broker
        print("TT_Dashboard/autopilotService/setWaypoints", str(self.final_path))
        # time.sleep(0.5)

    def check_pattern(self,a,b):
        if re.match(a, b):
            return 1 #String matches with the pattern
        else:
            return 0 #String does not match with the pattern

    def ConectionExt(self):

        if self.ConnectUAV==False:
            self.ConnectUAV=True #Connect button pressed

            connection_mode = sys.argv[1]  # global or local
            operation_mode = sys.argv[2]  # simulation or production
            username = None
            password = None
            if connection_mode == "global":
                external_broker = sys.argv[3]
                """if external_broker == "classpip.upc.edu":
                    username = sys.argv[4]
                    password = sys.argv[5]"""
            else:
                external_broker = None

            self.BrokerConnection(connection_mode, operation_mode, external_broker, username, password)

            self.path_images=self.path_main_directory+"/"+self.FP_leg_result
            if os.path.exists(self.path_images):
                print("Directory already exists")
                pass
            else:
                os.mkdir(self.path_images) #Create directory for each new Leg created

            self.counter = 0 #Counter for images name [TEMPORAL]
            self.tower_pos=0 #Counter to sync user app and AutopilotService while inspecting towers

        else:
            messagebox.showwarning("Note", "Connection already established")

    def BrokerConnection(self, connection_mode, operation_mode, external_broker, username, password):
        #Dasboard connects to external broker

        global op_mode
        global external_client
        global state
        global cap
        global colorDetector

        print("Connection mode: ", connection_mode)
        print("Operation mode: ", operation_mode)
        op_mode = operation_mode

        if connection_mode == "global":
            external_broker_address = external_broker
        else:
            external_broker_address = "localhost"
            #external_broker_address = "10.10.10.1" #UAV WIFI address (production mode)

        print("External broker: ", external_broker_address)

        # the external broker must run always in port 8000
        external_broker_port = 8000

        self.client = mqtt.Client(transport="websockets") #Create new client object

        """if external_broker_address == "classpip.upc.edu":
            external_client.username_pw_set(username, password)"""

        self.client.on_message = self.on_message #Attach function to callback msg
        self.client.connect(external_broker_address, external_broker_port,keepalive=60) #Connection to the ext broker

        self.client.publish("TT_Dashboard/autopilotService/connect")  # Publish the connection to AutopilotService
        time.sleep(0.5)
        #self.final_path, self.airspeed, altitude

        self.client.subscribe("autopilotService/TT_Dashboard/setWaypoints")  # Subscription to Autopilot topic (Broker answer when action is completed)
        self.client.subscribe("autopilotService/TT_Dashboard/inspTakeOff")  # Subscription to Autopilot topic (Broker answer when action is completed)
        self.client.subscribe("cameraService/TT_Dashboard/pictureFP")  # Subscription to CameraServ topic (Broker answer when action is completed)"""
        self.client.subscribe("autopilotService/TT_Dashboard/nextWP")
        self.client.subscribe("autopilotService/TT_Dashboard/readyScan")
        self.client.subscribe("autopilotService/TT_Dashboard/landed")

        #external_client.subscribe("+/TT_Dashboard/#") #Subscribe to all messages that match the pattern

        """self.client.publish("TT_Dashboard/autopilotService/setWaypoints",str(self.final_path)) #Publish inspection leg to the connection to broker
        print("TT_Dashboard/autopilotService/setWaypoints", str(self.final_path))
        #time.sleep(0.5)"""

        #external_client.loop_forever()
        self.client.loop_start()

        self.Con_state.place(relx=0.66, rely=0.6, anchor=tkinter.CENTER)
        self.Con_state.configure(text="State: Connected")
        self.ConnectExtBroker.configure(fg_color="green")
        self.UploadFP.place(relx=0.66, rely=0.8, anchor=tkinter.CENTER) #Show option for sending data to UAV

    def on_message(self, client,userdata,message):

        #External message reception from broker
        print("external message rx: ", message.topic)
        if message.topic == "autopilotService/TT_Dashboard/setWaypoints":
            print("Answer: ", message.payload)
            if str(message.payload)=="b'OK'":
                client.publish("TT_Dashboard/autopilotService/setAirspeed",str(self.airspeed))  # Publish aispeed to the connection to broker
                print("TT_Dashboard/autopilotService/setAirspeed",str(self.airspeed))
                time.sleep(0.5)
                client.publish("TT_Dashboard/autopilotService/inspTakeOff")
            else:
                print("ERROR")

        if message.topic == "autopilotService/TT_Dashboard/inspTakeOff":
            print("Answer: ", message.payload)
            if str(message.payload)=="b'OK'":
                print("Altitude reached. Ready to inspect")
                client.publish("TT_Dashboard/autopilotService/startInsp",str(self.tower_pos))
            else:
                print("ERROR")

        if message.topic == "autopilotService/TT_Dashboard/nextWP":
            self.tower_pos = int(message.payload) + 1 #Update position
            if self.tower_pos<=len(self.final_path)-1:
                print("next tower pos", int(self.tower_pos))
                client.publish("TT_Dashboard/autopilotService/startInsp",str(self.tower_pos))
            else:
                client.publish("TT_Dashboard/autopilotService/inspLand")  # Last WP reached. Proceed to return and land

        if message.topic == "autopilotService/TT_Dashboard/readyScan":
            scan_rate=30 #Deg increment. For each value a picture is taken
            client.publish("TT_Dashboard/autopilotService/startScan",str(scan_rate))

        if message.topic == "autopilotService/TT_Dashboard/landed":
            #cap.release()
            cv.destroyAllWindows()
            client.publish("TT_Dashboard/autopilotService/disconnect")
            self.client.disconnect()
            self.final_path.clear() #Delete inspected list
            self.ConnectExtBroker.place_forget()
            self.ConnectExtBroker.configure(fg_color="red")
            self.UploadFP.place_forget() #Hide upload option
            self.ConnectUAV = False



        if message.topic == "cameraService/TT_Dashboard/pictureFP":
            found=False

            img = base64.b64decode(message.payload)
            jpg_as_np = np.frombuffer(img, dtype=np.uint8)
            img = cv.imdecode(jpg_as_np, 1)
            # Decode to Original Frame
            res = cv.cvtColor(img, cv.COLOR_BGR2RGB)

            img = cv.resize(img, (416, 416))  # Resize original frame (416x416 to follow algorithm)
            img2 = cv.resize(img, (720, 720))  # Saved image

            detect = self.model(img)  # NEW
            info = detect.pandas().xyxy[0]  # im1 predictions
            for index, row in info.iterrows():
                #print(" -- class object: ", row['class'], "confidence: ", row['confidence'], " --")

                if str(row['class']) == '2':
                    # Number of class
                    print("TOWER FOUND! Confidence: ", row['confidence']," SAVED IMAGE INTO DIRECTORY")
                    found=True

            cv.imshow("Picture", np.squeeze(detect.render()))
            cv.waitKey(1)

            if found==True:
                #Tower detected
                self.tower_pos = self.tower_pos + 1
                if self.tower_pos<=len(self.final_path)-1:
                    print("Go to next WP")
                    time.sleep(3)
                    client.publish("TT_Dashboard/autopilotService/startInsp", str(self.tower_pos))  # Go to next tower
                else:
                    time.sleep(1)
                    client.publish("TT_Dashboard/autopilotService/inspLand")  # Last WP reached. Proceed to return and land

                # Save image of tower in the proper directory
                image_name=str(self.final_path[self.counter][1][0])+","+str(self.final_path[self.counter][1][1])
                print("SAVE IMG: ", self.path_images + "/" + image_name + '.jpg')
                cv.imwrite(self.path_images + "/" + image_name + '.jpg', img2)

                self.counter = self.counter + 1

            else:
                # Tower not detected
                scan_rate=32
                time.sleep(1)
                client.publish("TT_Dashboard/autopilotService/startScan",str(scan_rate))



    def CameraON(self):

        global op_mode
        global external_client
        global state
        global cap

        connection_mode = sys.argv[1]  # global or local
        operation_mode = sys.argv[2]  # simulation or production
        username = None
        password = None
        if connection_mode == "global":
            external_broker = sys.argv[3]
            """if external_broker == "classpip.upc.edu":
                username = sys.argv[4]
                password = sys.argv[5]"""
        else:
            external_broker = None

        print("Connection mode: ", connection_mode)
        print("Operation mode: ", operation_mode)
        op_mode = operation_mode

        if connection_mode == "global":
            external_broker_address = external_broker
        else:
            external_broker_address = "localhost"

        print("External broker: ", external_broker_address)

        # the external broker must run always in port 8000
        external_broker_port = 8000

        external_client = mqtt.Client(transport="websockets")  # Create new client object

        """if external_broker_address == "classpip.upc.edu":
            external_client.username_pw_set(username, password)"""

        external_client.on_message = self.on_message  # Attach function to callback msg
        external_client.connect(external_broker_address, external_broker_port,keepalive=60)  # Connection to the ext broker

        print("Sending Start Streming command")
        external_client.publish("TT_Dashboard/cameraService/startVideoStreamFP")  #CAN BE DELETED
