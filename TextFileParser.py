#This Will parse Json Files as Setup by the User

import json
import matplotlib.pyplot as plt
import numpy as np
import chiller_support

#The JSONs should have the Following Structure
#Each JSON defines a Thermal Vaccum Chamber Test known as a Run
#Each Run is composed of a number of Profiles Sometimes one Sometimes many
#RunName -- Tha name of the Run
#UseChaser -- Should we use the Chasing algorythim to chase the temperature to the setpoint
#ChosenRTD -- Which RTD are We tracking
#ThermalMass -- What is the Thermal Mass of the Object you are Testing
#StartingPoint -- This is the Starting temperature of the Chamber
#EndingPoint -- This is the last temp point
#Profiles -- This is a list of Profiles

#Each Profile is composed of a number of Setpoints
#Each Profile has the Following Parameters
#Profile TempProfileName -- name of the profile
#Profile Rrepititions -- How many times to repeat the profile
#Profile Setpoints -- A list of Setpoints

#Each Setpoint has the Following parameters
#Setpoint name - The name of the Setpoint
#Setpoint Temp   - The Temperature the Chamber is set to
#Setpoint Hold   - Howlong the Chamber is set to the Setpoint Temp
#Setpoint RampRate - The Rate the Chamber is ramping up or down to the Setpoint Temp ie 1 C/min


#Reads a Json File and creates an object from it
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
        self.setPointTolerance = self.readParameter("SetPointTolerance")
        self.verifyData()
        self.Profiles = []
        self.getProfiles()
        
        self.getPlot()

    
    #read the parameter in the JSON File and returns it
    #Try to read the parameter if it fails throw an error and exiting the program
    def readParameter(self, ParameterName):
        try: 
            return self.data[ParameterName]
        except:
            print(f"ERROR: Couldnt Read Parameter: {ParameterName} in {self.FileName}")
            exit()


    #VerifyThat the RunName is a String
    def verifyRunName(self):
        if type(self.RunName) != str:
            print(f"ERROR: RunName is not a String in {self.FileName}")
            exit()
    #Verify That We can Convert the UserChaser to a Boolean
    def verifyUseChaser(self):
        if type(self.UseChaser) != bool:
            print(f"ERROR: UseChaser is not a Boolean in {self.FileName}")
            exit()
    
    #Verify that ChosenRTD is one of the Expected Values
    def verifyChosenRTD(self):
        if self.ChosenRTD not in [ "Chiller","Plate1", "Plate2", "Plate4", "Floating RTD"]:
            print(f"ERROR: ChosenRTD {self.ChosenRTD} is not a valid RTD in {self.FileName}\r\n Expected Values are: Chiller, Plate1, Plate2, Plate4, Floating RTD")
            exit()

    #Verify that ThermalMass is an expected value
    def verifyThermalMass(self):
        if self.ThermalMass not in ["Small", "Medium", "Large", "XL"]:
            print(f"ERROR: ThermalMass {self.ThermalMass} is not an expected value in {self.FileName}\r\n Expected Values are: Small, Medium, Large, XL")
            exit()    

    #Verify that StartingPoint is a Numberor the string "Ambient" and that it is within chiller_support.UpperTempLimit and chiller_support.LowerTempLimit
    def verifyStartingPoint(self):
        if type(self.StartingPoint) != int and type(self.StartingPoint) != float and self.StartingPoint != "Ambient":
            print(f"ERROR: StartingPoint {self.StartingPoint} is not a Number in {self.FileName}")
            exit()
        if self.StartingPoint != "Ambient" and self.StartingPoint > chiller_support.chillerUpperLimit:
            print(f"ERROR: StartingPoint {self.StartingPoint} is greater than Upper Limit of the Chiller {chiller_support.chillerUpperLimit} in {self.FileName}")
            exit()
        if self.StartingPoint != "Ambient" and self.StartingPoint < chiller_support.chillerLowerLimit:
            print(f"ERROR: StartingPoint {self.StartingPoint} is less than Lower Limit of the Chiller {chiller_support.chillerLowerLimit} in {self.FileName}")
            exit()
    
    #Verify that EndingPoint is a Number
    def verifyEndingPoint(self):
        if type(self.EndingPoint) != int and type(self.EndingPoint) != float and self.StartingPoint != "Ambient":
            print(f"ERROR: EndingPoint {self.EndingPoint} is not a Number in {self.FileName}")
            exit()
        if self.EndingPoint != "Ambient" and self.EndingPoint > chiller_support.chillerUpperLimit:
            print(f"ERROR: EndingPoint {self.EndingPoint} is greater than Upper Limit of the Chiller {chiller_support.chillerUpperLimit} in {self.FileName}")
            exit()
        if self.EndingPoint != "Ambient" and self.EndingPoint < chiller_support.chillerLowerLimit:
            print(f"ERROR: EndingPoint {self.EndingPoint} is less than Lower Limit of the Chiller {chiller_support.chillerLowerLimit} in {self.FileName}")
            exit()

    #Verify setpoint Tolerance is a number greater than .05
    def verifySetPointTolerance(self):
        if type(self.setPointTolerance) != int and type(self.setPointTolerance) != float:
            print(f"ERROR: SetPointTolerance {self.setPointTolerance} is not a Number in {self.FileName}")
            exit()
        if self.setPointTolerance < .05:
            print(f"ERROR: SetPointTolerance {self.setPointTolerance} is less than .05 in {self.FileName}")
            exit()
    
    #Verify that the JSON File is in the correct format
    def verifyData(self):
        self.verifyRunName()
        self.verifyUseChaser()
        self.verifyChosenRTD()
        self.verifyThermalMass()
        self.verifyStartingPoint()
        self.verifyEndingPoint()

    #read in the entire JSON File and place it into data variable
    def readData(self):
        f = open(self.FileName, "r")
        data = json.loads(f.read())
        f.close()
        return data
    
    #This will generate the Profile Objects from the JSON File
    def getProfiles(self):
        profiles = self.data["Profiles"]
        for profile in profiles:
            self.Profiles.append(Profile(profile))

    #This will build a plot from all the Data to ensure to the enduser that the data is correct
    #it should always be called last
    def getPlot(self):
        array = []

        #Go through Every Profile break it down
        for x in range(len(self.Profiles)):
            #If the Profile is repeated
            for i in range(self.Profiles[x].Repititions):
                for j in range(len(self.Profiles[x].SetPoints)):
                    #Exceptions for Determining the Starting Temperature
                    #if this is the First point we are looking at Start at room temp
                    if j == 0 and i == 0 and x ==0:
                        if self.StartingPoint == "Ambient":
                            startingTemp = 23
                        else:
                            startingTemp = self.StartingPoint
                            
                    #if we are looking at the first point in a series of point look at the last point of the previous profile 
                    elif j == 0 and i == 0: 
                        startingTemp = self.Profiles[x-1].SetPoints[-1].Temp
                    elif j == 0: 
                        startingTemp = self.Profiles[x].SetPoints[-1].Temp
                    else: 
                        startingTemp = self.Profiles[x].SetPoints[j-1].Temp
                    if startingTemp < self.Profiles[x].SetPoints[j].Temp: direction = 1
                    else: direction = -1
                    
                    tempDifference = abs(float(self.Profiles[x].SetPoints[j].Temp) - startingTemp)
                    rampDuration = abs(tempDifference/float(self.Profiles[x].SetPoints[j].RampRate))

                    for k in range(round(rampDuration)):
                        array.append(startingTemp+((direction)*self.Profiles[x].SetPoints[j].RampRate*k))
                    for k in range(round(self.Profiles[x].SetPoints[j].Hold)):
                        array.append(self.Profiles[x].SetPoints[j].Temp)
        ##Add in the EndingTemperature to the array
        startingTemp = self.Profiles[-1].SetPoints[-1].Temp
        tempDifference = abs(float(self.Profiles[x].SetPoints[j].Temp) - startingTemp)
        rampDuration = abs(tempDifference/float(self.Profiles[x].SetPoints[j].RampRate))

        for k in range(round(rampDuration)):
            array.append(startingTemp+((direction)*self.Profiles[x].SetPoints[j].RampRate*k))
        
        if self.EndingPoint == "Ambient":
            array.append(23)
        else:
            array.append(self.EndingPoint)
            
        

        fig, ax = plt.subplots(1,1)
        
        p=ax.plot(array)
        xt = ax.get_xticks()
        yt = ax.get_yticks()
        ytl=yt.tolist()
        
        #Go through Each Profile
        for x in range(len(self.Profiles)):
            #Go through Each Setpoint
            for j in range(len(self.Profiles[x].SetPoints)):
                yt=np.append(yt,self.Profiles[x].SetPoints[j].Temp)
                ytl = np.append(ytl,f"{self.Profiles[x].SetPoints[j].Name} [{self.Profiles[x].SetPoints[j].Temp}]")
                ax.axhline(self.Profiles[x].SetPoints[j].Temp, linestyle = '--', linewidth = 1, color = 'gray') 
        if self.StartingPoint == "Ambient":
            yt=np.append(yt,23)
            ytl = np.append(ytl,"Starting Point [23]")
            ax.axhline(23, linestyle = '--', linewidth = 1, color = 'gray')
        else:
            yt=np.append(yt,self.StartingPoint)
            ytl = np.append(ytl,f"Starting Point [{self.StartingPoint}]")
            ax.axhline(self.StartingPoint, linestyle = '--', linewidth = 1, color = 'gray')
        if self.EndingPoint == "Ambient":
            yt=np.append(yt,23)
            ytl = np.append(ytl,"Ending Point [23]")
            ax.axhline(23, linestyle = '--', linewidth = 1, color = 'gray')
        else:
            yt=np.append(yt,self.EndingPoint)
            ytl = np.append(ytl,f"Ending Point [{self.EndingPoint}]")
            ax.axhline(self.EndingPoint, linestyle = '--', linewidth = 1, color = 'gray')
        
        #Setup the plot and Display it
        ax.set_yticks(yt)
        ax.set_yticklabels(ytl)
        ax.set_yticks(yt)
        ax.set_yticklabels(ytl)

        ax.set_title(f"Expected Profiles from {self.RunName} as Detailed in {self.FileName}")
        ax.set_xlabel("Time [Min]")
        ax.set_ylabel("Temp [C]")
        fig.show()
        plt.show()
        

                    

#Subclass Utilized by RunReader to Read Profiles
class Profile:
    def __init__(self, data):
        self.data = data
        self.ProfileName = self.readParameter("TempProfileName")
        self.Repititions = self.readParameter("Repititions")
        self.verifyData()

        self.SetPoints = []
        self.getSetPoints()
    
    def readParameter(self, ParameterName):
        try: 
            return self.data[ParameterName]
        except:
            print(f"Error: {ParameterName} not found in {self.data}")
            exit()
    #VerifyThat the Profile name is correct
    def verifyProfileName(self):
        if type(self.ProfileName) != str:
            print(f"ERROR: RunName {self.ProfileName} is not a String in {self.ProfileName}")
            exit()


    #Verify That The Repititions are a number and greater than 0
    def verifyRepititions(self):
        if type(self.Repititions) != int:
            print(f"ERROR: Repititions {self.Repititions} is not a Integer in {self.ProfileName}")
            exit()
        if self.Repititions < 0:
            print(f"ERROR: Repititions {self.Repititions} is less than 0 in {self.ProfileName}")
            exit()

    #Verify Data is Correct
    def verifyData(self):
        self.verifyProfileName()
        self.verifyRepititions()

    def getSetPoints(self):
        setpoints = self.data["Setpoint_Series"]
        for setpoint in setpoints:
            self.SetPoints.append(SetPoint(setpoint))


#Subclass used by Profile to Read SetPoints
class SetPoint:
    def __init__(self, data):
        self.data = data
        self.Name = self.readParameter("SetPointName")
        self.Temp = self.readParameter("Temp [C]")
        self.Hold = self.readParameter("Hold [Min]")
        self.RampRate = self.readParameter("Ramp Rate To Temp [C/Min]")
        self.verifyData()

    def readParameter(self, ParameterName):
        try: 
            return self.data[ParameterName]
        except:
            print(f"Error: {ParameterName} not found in {self.data}")
            exit()

    #Verify That The Name is a String
    def verifyName(self):
        if type(self.Name) != str:
            print(f"ERROR: Name {self.Name} is not a String in {self.Name}")
            exit()
    #verify that the Temp is a number
    def verifyTemp(self):
        if type(self.Temp) != float and type(self.Temp) != int:
            print(f"ERROR: Temp {self.Temp} is not a Float in {self.Name}")
            exit()
        if  self.Temp > chiller_support.chillerUpperLimit:
            print(f"ERROR: Temp {self.Temp} is greater than Upper Limit of the Chiller {chiller_support.chillerUpperLimit} in {self.Name}")
            exit()
        if self.Temp < chiller_support.chillerLowerLimit:
            print(f"ERROR: Temp {self.Temp} is less than Lower Limit of the Chiller {chiller_support.chillerLowerLimit} in {self.Name}")
            exit()
    
    #Verify that the Hold is a number
    def verifyHold(self):
        if type(self.Hold) != float and type(self.Hold) != int:
            print(f"ERROR: Hold {self.Hold} is not a Float in {self.Name}")
            exit()
    #Verify that the RampRate is a number
    def verifyRampRate(self):
        if type(self.RampRate) != float and type(self.RampRate) != int:
            print(f"ERROR: RampRate {self.RampRate} is not a Float in {self.Name}")
            exit()

    #Verify Data is Correct
    def verifyData(self):
        self.verifyName()
        self.verifyTemp()
        self.verifyHold()
        self.verifyRampRate()

run = RunReader("Example.json")

