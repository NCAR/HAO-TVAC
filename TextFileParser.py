#This Will parse Json Files as Setup by the User

import json
import matplotlib.pyplot as plt
import numpy as np

class RunReader:
    def __init__(self, FileName):
        self.FileName = FileName
        self.data = self.readData()
        self.RunName = self.readParameter("RunName")
        self.UseChaser = self.readParameter("UseChaser")
        self.ChosenRTD = self.readParameter("ChosenRTD")
        self.ThermalMass = self.readParameter("ThermalMass")
        self.StartingPoint = self.readParameter("StartingPoint")
        self.EndingPoint = self.readParameter("EndingPoint")
        self.Profiles = []
        self.getProfiles()
        
        self.getPlot()

    def readParameter(self, ParameterName):
        return self.data[ParameterName]
    
    def readData(self):
        f = open(self.FileName, "r")
        data = json.loads(f.read())
        f.close()
        return data
    
    def getProfiles(self):
        profiles = self.data["Profiles"]
        for profile in profiles:
            self.Profiles.append(Profile(profile))

    def getPlot(self):
        array = []

        
        for x in range(len(self.Profiles)):
            for i in range(self.Profiles[x].Repititions):
                for j in range(len(self.Profiles[x].SetPoints)):
                    #Exceptions for Determining the Starting Temperature
                    #if this is the First point we are looking at Start at room temp
                    if j == 0 and i == 0 and x ==0 :
                        startingTemp = 20
                    #if we are looking at the first point in a series of point look at the last point of the previous profile 
                    elif j == 0 and i == 0: 
                        startingTemp = self.Profiles[x-1].SetPoints[-1].Temp
                    
                    elif j == 0: 
                        startingTemp = self.Profiles[x].SetPoints[-1].Temp
                    else: 
                        startingTemp = self.Profiles[x].SetPoints[j-1].Temp
                    print(self.Profiles[x].SetPoints[j].Temp)
                    if startingTemp < self.Profiles[x].SetPoints[j].Temp: direction = 1
                    else: direction = -1
                    
                    tempDifference = abs(float(self.Profiles[x].SetPoints[j].Temp) - startingTemp)
                    rampDuration = abs(tempDifference/float(self.Profiles[x].SetPoints[j].RampRate))

                    for k in range(round(rampDuration)):
                        array.append(startingTemp+((direction)*self.Profiles[x].SetPoints[j].RampRate*k))
                    for k in range(round(self.Profiles[x].SetPoints[j].Hold)):
                        array.append(self.Profiles[x].SetPoints[j].Temp)
        

        fig, ax = plt.subplots(1,1)
        
        p=ax.plot(array)
        xt = ax.get_xticks()
        yt = ax.get_yticks()
        for x in range(len(self.Profiles)):
            for j in range(len(self.Profiles[x].SetPoints)):
                yt=np.append(yt,self.Profiles[x].SetPoints[j].Temp)
                print(self.Profiles[x].SetPoints[j].Name)
                ytl=yt.tolist()
                ytl[-1]=self.Profiles[x].SetPoints[j].Name
                ax.set_yticks(yt)
                ax.set_yticklabels(ytl)
                ax.set_yticks(yt)
                ax.set_yticklabels(ytl)
                ax.axhline(self.Profiles[x].SetPoints[j].Temp, linestyle = '--', linewidth = 1, color = 'gray') 
                
               
        
        ax.set_title(f"Expected Profiles from {self.RunName}")
        ax.set_xlabel("Time [Min]")
        ax.set_ylabel("Temp [C]")
        fig.show()
        plt.show()
        

                    


class Profile:
    def __init__(self, data):
        self.data = data
        self.ProfileName = self.readParameter("TempProfileName")
        self.Repititions = self.readParameter("Repititions")
        self.SetPoints = []
        self.getSetPoints()
    
    def readParameter(self, ParameterName):
        return self.data[ParameterName]
    
    def getSetPoints(self):
        setpoints = self.data["Setpoint_Series"]
        for setpoint in setpoints:
            self.SetPoints.append(SetPoint(setpoint))

class SetPoint:
    def __init__(self, data):
        print(data)
        self.data = data
        self.Name = self.readParameter("SetPointName")
        self.Temp = self.readParameter("Temp [C]")
        self.Hold = self.readParameter("Hold [Min]")
        self.RampRate = self.readParameter("Ramp Rate To Temp [C/Min]")

    def readParameter(self, ParameterName):
        return self.data[ParameterName]


run = RunReader("Example.json")

