import datetime
import customtkinter as tk
import tkinter
from datetime import timedelta
from tkinter import ttk
from difflib import SequenceMatcher


class RightFrame:  # class

    def buildFrame(self, fatherFrame):
        self.Rightframe = tk.CTkFrame(master=fatherFrame)
        self.Rightframe.pack(side="right", pady=2, padx=2, fill="both", expand=False)

        self.RightframeTop = tk.CTkFrame(master=self.Rightframe)
        self.RightframeTop.pack(side="top", pady=2, padx=2, fill="both", expand=False)
        self.RightframeBttm = tk.CTkFrame(master=self.Rightframe)
        self.RightframeBttm.pack(side="top", pady=2, padx=2, fill="both", expand=False)

        self.Title_bttm = tk.CTkLabel(master=self.RightframeBttm, text="FLIGHT PLAN INFORMATION")
        self.Title_bttm.pack(pady=2, padx=2)

        self.Table=ttk.Treeview(self.RightframeBttm)
        s=ttk.Style()
        s.theme_use('clam')
        s.configure('Treeview.Heading', background='#3b4df5', foreground="white")
        self.Table['columns']=('Item','Waypoint','Tower','Position', 'Distance','Distance2','FP')
        self.Table.column("#0", width=0, stretch=tk.NO)
        self.Table.column("Item", anchor=tk.CENTER, width=60)
        self.Table.column("Waypoint", anchor=tk.CENTER, width=100)
        self.Table.column("Tower", anchor=tk.CENTER, width=180)
        self.Table.column("Position", anchor=tk.CENTER, width=250)
        self.Table.column("Distance", anchor=tk.CENTER, width=90)
        self.Table.column("Distance2", anchor=tk.CENTER, width=90)
        self.Table.column("FP", anchor=tk.CENTER, width=50)
        self.Table.heading("#0",text="",anchor=tk.CENTER)
        self.Table.heading("Item", text="Item", anchor=tk.CENTER)
        self.Table.heading("Waypoint", text="Waypoint", anchor=tk.CENTER)
        self.Table.heading("Tower", text="Tower", anchor=tk.CENTER)
        self.Table.heading("Position", text="Position", anchor=tk.CENTER)
        self.Table.heading("Distance", text="Distance (m)", anchor=tk.CENTER)
        self.Table.heading("Distance2", text="WP-TWR (m)", anchor=tk.CENTER)
        self.Table.heading("FP", text="FP Leg", anchor=tk.CENTER)
        self.Table.pack(fill='x',pady=2)

        self.Table2 = ttk.Treeview(self.RightframeBttm)
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('Treeview.Heading', background='#3b4df5', foreground="white")
        self.Table2['columns'] = ('FP','Operation','Distance','Time','Speed')
        self.Table2.column("#0", width=0, stretch=tk.NO)
        self.Table2.column("FP", anchor=tk.CENTER, width=70)
        self.Table2.column("Operation", anchor=tk.CENTER, width=230)
        self.Table2.column("Distance", anchor=tk.CENTER, width=150)
        self.Table2.column("Time", anchor=tk.CENTER, width=140)
        self.Table2.column("Speed", anchor=tk.CENTER, width=90)
        self.Table2.heading("#0", text="", anchor=tk.CENTER)
        self.Table2.heading("FP", text="FP Leg", anchor=tk.CENTER)
        self.Table2.heading("Operation", text="Detailed Operation", anchor=tk.CENTER)
        self.Table2.heading("Distance", text="Distance Travelled (m)", anchor=tk.CENTER)
        self.Table2.heading("Time", text="Time Spent (s)", anchor=tk.CENTER)
        self.Table2.heading("Speed", text="Speed (km/h)", anchor=tk.CENTER)
        self.Table2.pack(padx=2, pady=10)
        self.Table2_filled=False #Statement that indicates if the table has been filled before

        self.item=0 #For Table1
        self.item2 = 0 #For Table2

        # Choose button option->Activate suggestion mode
        self.switch_var = tk.StringVar(value="OFF")
        self.switch_1 = tk.CTkSwitch(master=self.RightframeTop, text="Suggested WP", command=self.switch_event,variable=self.switch_var, onvalue="ON", offvalue="OFF")
        self.switch_1.place(relx=0.7, rely=0.2)
        self.switch_1.place_forget()
        self.SuggestionMode=False

        # Slider to set drone speed
        self.setSpeed = tk.CTkSlider(master=self.RightframeTop, from_=10, to=60, button_color="white",command=self.SetSpeed)
        self.setSpeed.place(relx=0.2, rely=0.2, anchor=tkinter.CENTER)
        self.Speed_value = tk.CTkLabel(master=self.RightframeTop,text="Cruise drone speed: " + str(round(self.setSpeed.get())) + " km/h")
        self.Speed_value.place(relx=0.53, rely=0.2, anchor=tkinter.CENTER)
        self.setSpeed.place_forget()
        self.Speed_value.place_forget()

        # Slider to set drone distance from tower
        self.setDist_TWR = tk.CTkSlider(master=self.RightframeTop, from_=1, to=45, command=self.TWRDist)
        self.setDist_TWR.place(relx=0.2, rely=0.8, anchor=tkinter.CENTER)
        self.Dist_TWR_value = tk.CTkLabel(master=self.RightframeTop,text="Distance from tower: " + str(round(self.setDist_TWR.get())) + " m")
        self.Dist_TWR_value.place(relx=0.53, rely=0.8, anchor=tkinter.CENTER)
        self.setDist_TWR.place_forget()
        self.Dist_TWR_value.place_forget()

        # Slider to set drone altitude
        self.setAltitude = tk.CTkSlider(master=self.RightframeTop, from_=1, to=120, command=self.SetAltitude)
        self.setAltitude.place(relx=0.2, rely=0.6, anchor=tkinter.CENTER)
        self.Altitude_value = tk.CTkLabel(master=self.RightframeTop,text="Height: " + str(round(self.setDist_TWR.get())) + " m")
        self.Altitude_value.place(relx=0.53, rely=0.6, anchor=tkinter.CENTER)
        self.setAltitude.place_forget()
        self.Altitude_value.place_forget()

        # Slider to set drone autonomy
        self.setAutonomy = tk.CTkSlider(master=self.RightframeTop, from_=2, to=30,command=self.SetAutonomy)
        self.setAutonomy.place(relx=0.2, rely=0.4, anchor=tkinter.CENTER)
        self.Autonomy_value = tk.CTkLabel(master=self.RightframeTop,text="Drone autonomy: " + str(round(self.setAutonomy.get())) + " min")
        self.Autonomy_value.place(relx=0.53, rely=0.4, anchor=tkinter.CENTER)
        self.setAutonomy.place_forget()
        self.Autonomy_value.place_forget()

    def ShowHideSettings(self,statement):
        if statement==True:
            #Show setting buttons when starting new FP
            self.setSpeed.place(relx=0.2, rely=0.2, anchor=tkinter.CENTER)
            self.Speed_value.place(relx=0.53, rely=0.2, anchor=tkinter.CENTER)
            self.setAutonomy.place(relx=0.2, rely=0.4, anchor=tkinter.CENTER)
            self.Autonomy_value.place(relx=0.53, rely=0.4, anchor=tkinter.CENTER)
            self.switch_1.place(relx=0.7, rely=0.2)
            self.Altitude_value.place(relx=0.53, rely=0.6, anchor=tkinter.CENTER)
            self.setAltitude.place(relx=0.2, rely=0.6, anchor=tkinter.CENTER)
            self.switch_var.set("OFF")
        else:
            #Hide setting buttons
            self.setSpeed.place_forget()
            self.Speed_value.place_forget()
            self.setAutonomy.place_forget()
            self.Autonomy_value.place_forget()
            self.setDist_TWR.place_forget()
            self.Dist_TWR_value.place_forget()
            self.switch_1.place_forget()
            self.Altitude_value.place_forget()
            self.setAltitude.place_forget()

    def TWRDist(self,value):
        self.dist_twr=round(value)
        self.Dist_TWR_value.configure(text= "Distance to tower: "+str(self.dist_twr)+" m")
        return self.dist_twr

    def Insert_SecondTable(self,operation,leg_code,color_leg,speed,hover_time,cruise_time,distance):

        self.counter=0
        self.time_count=0
        self.dist_count=0
        self.dist=0
        self.return_time=0
        self.return_dist = 0
        self.time_go=0
        self.color_leg=str(color_leg)
        self.instruction_list=[]

        if self.Table2_filled == False:
            self.Table2_filled=True
        else:
            self.item2=self.item2+1 #To avoid overlapping error

        while self.counter<len(operation): #Fill table for all FP leg

            #Extract instruction
            self.instruction=operation[self.counter]
            self.instruction_list=self.instruction.split(".")
            self.instruction=self.instruction_list[0] #Get instr value

            if self.instruction=="HOVER":
                self.speed=0
                self.time=hover_time

            else:

                self.match=self.similar(self.instruction, "RETURN FROM WPX")
                if self.match>=0.9:
                    self.time=round(self.return_time,2)
                    self.dist = round(self.return_dist,2)

                else:
                    self.speed = speed  # Cruise speed

                    if self.time_count<len(cruise_time):
                        self.time = round(cruise_time[self.time_count], 2)  # units: sec
                        self.return_time = self.time + self.return_time
                        # print("RETURN TIME: ",self.return_time)
                        #print(cruise_time, self.time_count)
                        self.time_count = self.time_count + 1
                    else:
                        pass

                    if self.dist_count<len(distance):
                        self.dist = distance[self.dist_count]
                        self.return_dist = self.return_dist + self.dist
                        self.dist_count = self.dist_count + 1
                        #print(distance, self.dist_count)
                    else:
                        pass

            self.time_go = self.time_go + self.time
            self.Table2.insert(parent='', index='end', iid=self.item2, text='',values=(leg_code, operation[self.counter], self.dist, self.time, self.speed), tags=self.color_leg)

            #Paint to proper color code
            if self.color_leg=='0':
                self.Table2.tag_configure('0', background="green", foreground="white")
            elif self.color_leg == '1':
                self.Table2.tag_configure('1', background="red", foreground="white")
            elif self.color_leg == '2':
                self.Table2.tag_configure('2', background="darkorange", foreground="black")
            elif self.color_leg == '3':
                self.Table2.tag_configure('3', background="gold", foreground="black")
            else:
                pass

            self.counter=self.counter+1
            self.item2 = self.item2 + 1

        self.item2 = self.item2 + 1

        self.dist_result=str(self.dist)+" / "+str(self.dist)

        #self.time_go = round(self.time_go/60, 2) #To min
        self.time_go = str(datetime.timedelta(seconds=self.time_go)) #Formatted time representation
        self.time_go_split=self.time_go.split(".")
        #self.return_time=float(self.return_time)/60
        self.return_time = str(datetime.timedelta(seconds=self.return_time)) #Formatted time representation
        self.time_return_split = self.return_time.split('.')
        self_time_result=str(self.time_go_split[0])+" / "+str(self.time_return_split[0]) #To min

        self.Table2.insert(parent='', index='end', iid=self.item2, text='',values=(leg_code,"-- TOTAL VALUES [GO/BACK] --" , self.dist_result, self_time_result , ""), tags="END")
        self.Table2.tag_configure('END', background="white", foreground="black") #Print final results of the FP Leg

    def similar(self,a,b):
        return SequenceMatcher(None,a,b).ratio()#Return matching value of strings

    def Insert_Table(self, positionFP,dist,tower_name,waypoint_num,dist_to_twr,color_leg,leg_code):
        self.code_leg = str(leg_code)
        self.color_leg=str(color_leg)
        #print("COLOR_LEG TABLE: "+str(color_leg))
        self.item = self.item + 1 #register ident in table
        self.dist=round(dist,2) #Rounding distance decimal value
        self.Table.insert(parent='', index='end', iid=self.item, text='', values=(self.item,waypoint_num,tower_name,positionFP,self.dist,dist_to_twr,self.code_leg),tags=self.color_leg)

        #Painting rows depending on the FP leg
        if self.color_leg=='0':
            self.Table.tag_configure('0',background="green",foreground="white")
        elif self.color_leg=='1':
            self.Table.tag_configure('1', background="red",foreground="white")
        elif self.color_leg=='2':
            self.Table.tag_configure('2', background="darkorange",foreground="black")
        elif self.color_leg=='3':
            self.Table.tag_configure('3', background="gold",foreground="black")
        else:
            pass

    def RemoveWP_Table(self): #Remove last item from table
        self.Table.delete(self.item)
        self.item = self.item - 1
        #print(self.item)

    def Clear_Table(self): #Remove entire table
        self.item=0 #Counter Reset
        self.item2 = 0  # Counter Reset
        self.Table2_filled = False

        for i in self.Table.get_children():
            self.Table.delete(i)

        for i in self.Table2.get_children():
            self.Table2.delete(i)

    def SetSpeed(self, value):
        self.speed = round(value)
        self.Speed_value.configure(text="Cruise drone speed: " + str(self.speed) + " km/h")
        # print(str(self.range)+" m")
        return self.speed

    def SetAltitude(self, value):
        self.altitude = round(value)
        self.Altitude_value.configure(text="Height: " + str(self.altitude) + " m")
        return self.altitude

    def switch_event(self):
        #print("switch toggled, current value:", self.switch_var.get())
        if self.switch_var.get()=="ON":
            self.SuggestionMode = True
            self.setDist_TWR.place(relx=0.2, rely=0.8, anchor=tkinter.CENTER)
            self.Dist_TWR_value.place(relx=0.53, rely=0.8, anchor=tkinter.CENTER)
            return self.SuggestionMode
        else:
            self.SuggestionMode = False
            self.setDist_TWR.place_forget()
            self.Dist_TWR_value.place_forget()
            return self.SuggestionMode

    def SetAutonomy(self, value):
        self.autonomy = round(value)
        self.Autonomy_value.configure(text="Drone autonomy: " + str(round(self.setAutonomy.get())) + " min")
        # print(str(self.range)+" m")
        return self.autonomy

    def RemoveFP_Table(self):
        self.WP_list=[]

        for child in self.Table.get_children():
            self.WP_list.append(self.Table.item(child)["values"]) #Look for the FP to remove

        for waypoint in self.WP_list:
            if str(waypoint[6])==self.code_leg: #Compare last FP code_leg added to find the first index which count_remove value must start from
                self.count_remove=waypoint[0]
                self.Table.delete(self.count_remove)
                print(self.count_remove)
                self.item=self.item-1

        if self.color_leg == 0:  # Return next code of FP legs
            self.next_color=1
        elif self.color_leg == 1:
            self.next_color=2
        elif self.color_leg == 2:
            self.next_color=3
        elif self.color_leg == 3:
            self.next_color=0
        else:
            self.next_color=0

        return self.next_color #Once removed the FP. We need to return the next color code

    def Update_SecondTable(self):
        pass








