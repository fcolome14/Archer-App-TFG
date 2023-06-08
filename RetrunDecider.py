
class ReturnCalculator:  # Tower name detection+distance from WP class

    def return_wp(self,dist,speed, autonomy):

        self.speed = round(speed * 0.2777, 3)  # To m/s
        # self.range = range
        self.autonomy = round(autonomy * 60, 1)  # To seconds
        #print("Settings of Speed [m/s]: " + str(self.speed) + "//Autonomy [s]: " + str(self.autonomy))

        self.extra_time = 60  # in seconds. Time dedicated to yaw, detect and take shots of the tower
        self.error_range = 1 #Error due to wind and other factors
        self.time = []
        self.WP_go_back=0
        self.max_time_reached=False #Statement

        self.time=[x/self.speed for x in dist] #Get cruise time to each segment of the FP

        self.total_time =0
        self.total_time_back=0
        self.counter=0
        self.WP_ident=1

        self.result_autonomy=self.autonomy*self.error_range #Autonomy apllying an error margin by default
        #print("Autonomy applying margin: "+str(self.result_autonomy))
        #print(self.time)

        while self.max_time_reached!=True and self.counter<len(self.time):

            self.total_time = self.time[self.counter] + self.total_time + self.extra_time
            self.total_time_back = self.total_time_back + self.time[self.counter]
            #print("Drone at WP" + str(self.WP_ident) + ". Time of flight: " + str(self.time[self.counter]))
            """
            if self.counter>=1:
                print("Drone hovering +60s. Time elapsed: " + str(self.total_time))
                print("Return time: " + str(self.total_time_back))
                pass
            else:
                pass
            """

            if (self.total_time+self.total_time_back >= self.result_autonomy):
                self.WP_ident = self.WP_ident = self.WP_ident = self.WP_ident - 1  # Return the last accepted WP
                self.max_time_reached=True #Break loop. Drone autonomy has been reached, no more WP can't be added to this FP
            else:
                self.counter = self.counter + 1
                self.WP_ident = self.WP_ident + 1

        return self.max_time_reached, self.WP_ident,self.extra_time,self.time  # Return statement and last WP ident