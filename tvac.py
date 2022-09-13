import rtd
import chiller_support
from tvac_logger import logger

#Principles TVAC Has a Chiller and RTDs
#TVAC will handle all the Logging. Only requesting data from and Commanding
import __main__
from pathlib import Path
import datetime
import time
import sys
import matplotlib.pyplot as plt
from functools import partial
from numpy import diff


try:
    ExecFileURL = Path(__main__.__file__)
except:
    ExecFileURL = Path(".")

#TODO Style: Need to make it so that Temperature readings are all being called from the Function Dictionary
#TODO Stlye Figure out Who handles data cleaning with the Temperature calls 
#TODO ENG: Communication or readings from the to Check current pressure in Vacuum Chamber
#TODO Style: Implement Error Checking for input TargetSensor ensure its in the Dict
#TODO Style: Implement Error Checking For WaitForTemperature Routine ie dont allow more than 36 hours etc
#TODO Gen: More error Checking and reporting
#TODO Gen: Data Streams probably shouldnt be stored in memory Maybe either load CSV data OR only Display the last X Points?
class tvac:
    def __init__(self, Chiller, RTD, TargetSensor = 'Chiller', ThermalMass = 'Small'):
        """Opens a connection to the chiller and initializes a .CSV file."""
        #Setup peripherials
        self.Chiller = Chiller
        self.RTDs = RTD


        #Limits for Temp
        self._LowerLimit = chiller_support.chillerLowerLimit
        self._UpperLimit = chiller_support.chillerUpperLimit
        #Set up the parameters for our TVAC run
        self._TargetTempSensor = TargetSensor
        self._TargetTemperature = False
        self._Temperature = False
        self._TemperatureSampleTime = False
        self._TemperatureSampleInterval = 2
        self._ChillerSetTemp = False
        

        

        #How long does it take for the Sensor Temp to move Once the Chiller temp Changes
        #Set ThermalMass Weight Set in Time before expected temperature begins to move
        self._ThermalMass = ThermalMass
        self.ThermalMassWeightDict = {
            'Small': 60*2,
            'Medium': 60*5,
            'Large': 60*10,
            'XL': 60*20

        }
        
        ### Temperature Polling ###

        #To Be Edited If we get new Sensors. 
        #This is a dictionary of functions that will request Temperaturs in C for each of the sensors
        #The purpose of these are so that we can have one super function Temperature and _TempDataStream to call each of the Sensors based on what the enduser wants
        


        #This Dictionary Contains Functions to poll the various sensors 
        self.TemperatureFuncDict = {
            'Chiller': self.ChillerTemperature,
            'Plate1': partial(self.RTDTemperature, 3),
            'Plate2': partial(self.RTDTemperature, 2),
            'Plate3': partial(self.RTDTemperature, 1),
            'Floating RTD': partial(self.RTDTemperature, 0)
            }

                #Data Streams
        self._DataTime = []
        self._DataChillerTemperature = []
        self._DataRTDsTemperature = []
        self._DataTarget = []
        self._DataChillerSetTemp = []

        
        #This will poll the Data Stream
        #partial is used to pass in the function to call and the channel to call it on
        self.TemperatureDataStreamDict = {
            'Chiller': self._DataChillerTemperature,
            'Plate1': partial(self.Extract,self._DataRTDsTemperature, 3),
            'Plate2': partial(self.Extract,self._DataRTDsTemperature, 2),
            'Plate3': partial(self.Extract,self._DataRTDsTemperature, 1),
            'Floating RTD': partial(self.Extract,self._DataRTDsTemperature, 0)
            }
        
        
        

        

        ###### Data Logging ######
        #Data CSVs
        self.CSVFile = (ExecFileURL.parent / 'logs' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')).with_suffix(
            '.csv')

        #Graph Output
        self.PNGFile = (ExecFileURL.parent / 'logs' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')).with_suffix(
            '.png')

        #Set Data Time Info
        self.ExecStartTime = time.time()
        self.ExecStartDateTime = datetime.datetime.now()
        self.DryRun = False


        #Create CSV
        datafile = open(self.CSVFile, mode='w')
        datafile.write("minutes, ChillerTemp, TargetTemp, PlateTemp1, PlateTemp2, PlateTemp3, FloatTemp, ChillerSetTemp\n")
        datafile.close()

        #Create Plot
        self._fig = plt.figure(1)
        self.LogTemperature()



    def __del__(self):
        logger.info("Done.")


#Plots the Data And Displays: will Clear out previous data
    def PlotData(self):
        # plot the data
        plt.clf()
        plt.plot(self._DataTime, self._DataChillerTemperature, label="Chiller Temp")
        plt.plot(self._DataTime, self._DataTarget, label="Target Temp")
        plt.plot(self._DataTime, self._DataChillerSetTemp, label="Chiller Set Temp")
        #Todo Choose Which Channels to plot
        plt.plot(self._DataTime, self.Extract(self._DataRTDsTemperature, 3), label="Plate Temp 1")
        plt.plot(self._DataTime, self.Extract(self._DataRTDsTemperature, 0), label="Floating RTD Temp")
        plt.plot(self._DataTime, self.Extract(self._DataRTDsTemperature, 2), label="Plate Temp 2")
        plt.plot(self._DataTime, self.Extract(self._DataRTDsTemperature, 1), label="Plate Temp 3")

        plt.xlabel("Elapsed Time [m]")
        plt.ylabel("Temperature [C]")
        plt.title("Thermal Vacuum Test {:s}".format(self.ExecStartDateTime.strftime('%Y-%m-%d %H:%M:%S')))
        plt.legend()
        plt.ion()  # spawns the graph in a child thread
        plt.show()  # show the graph
        plt.pause(0.01)  # graph drawing is done when main thread is idle
        plt.savefig(self.PNGFile)

    #Log Temperature in the CSV File
    #This will Go through and Pull all the data from the Data Streams and log it to the CSV
    def LogTemperature(self):
        """Writes temperature and target values to a CSV file."""
        DataTime = (time.time() - self.ExecStartTime) / 60


        DataRTDsTemperature = self.RTDs.Read()
        DataChillerTemperature = self.Chiller.Temperature
        DataChillerSetTemp = self.ChillerSet
        DataTarget = self.Target

        # save data for graphing
        self._DataTime.append(DataTime)
        self._DataChillerTemperature.append(DataChillerTemperature)
        self._DataTarget.append(DataTarget)
        self._DataRTDsTemperature.append(DataRTDsTemperature)
        self._DataChillerSetTemp.append(DataChillerSetTemp)


        logger.debug("The chiller temperature is {:.1f} C.".format(DataChillerTemperature))
        
        
        # write to the log file
        datafile = open(self.CSVFile, mode='a')
        entry = "{:7.1f},{:5.1f},{:5.1f},{:5.1f},{:5.1f},{:5.1f},{:5.1f},{:5.1f}\n"
        
        datafile.write(entry.format(DataTime, DataChillerTemperature, DataTarget, DataRTDsTemperature[3][0],
                                    DataRTDsTemperature[2][0],DataRTDsTemperature[1][0],DataRTDsTemperature[0][0],DataChillerSetTemp))
        datafile.close()
        
        self.PlotData()

    
    #Temp Sensors Functions
    #Need More Clarity in who handles what cleaning eg Time delays negative numbers etc
    #Temperature is the Default Function that will be called to check the Temp of the Target Sensor.
    #If new Temp sensors are added to the System they will have {SensorName}Temperature Reading functions here
    #TODO There is an issue here with the Chiller Temperature. It is not returning the correct value.
    @property
    def _TempDataStream(self):
        _TempDataStream = [item for sublist in self.TemperatureDataStreamDict[self._TargetTempSensor]() for item in sublist]
        return _TempDataStream
    
    @property
    def Temperature(self):
        if ((int(time.time()) - self._TemperatureSampleTime)  > self._TemperatureSampleInterval):  # if we have no samples from this second
            self._Temperature = self.TemperatureFuncDict[self._TargetTempSensor]()
            self._TemperatureSampleTime = int(time.time())
        return self._Temperature
    
    def ChillerTemperature(self):
            x = self.Chiller.ReadRegister(0x1000) / 10
            # handle negative numbers
            if x > 6000:
                x = x - 6553.6
            return x
                
    def RTDTemperature(self, channel):
        x = self.RTDs.Read(channel)[0]
        
        return x


    #Set the Target for temperature that we want the Sensor to reach Does not Write to Chiller
    @property
    def Target(self):
        return self._TargetTemperature

    #TODO This needs to be updated to pull the lab ambient
    @property
    def Ambient(self):
        return 20 #degrees C

    @Target.setter
    def Target(self, value):
        #TODO Need to Find ambient Temp Setter
        if value == "Ambient":
            value = self.Ambient
        if value > self._UpperLimit:
            logger.warning("Attempt to set temperature too high!")
            return
        if value < self._LowerLimit:
            logger.warning("Attempt to set temperature too low!")
            return
        if round(value * 10) != round(self._TargetTemperature * 10):  # don't set the same temperature we have
            logger.info("Setting target temperature to {:.1f} C.".format(value))
            self._TargetTemperature = value


    #Set the Set Temp For the Chiller Writes to the the Chiller and reads from the register
    @property
    def ChillerSet(self):
        if self._ChillerSetTemp == False:
            x = self.Chiller.ReadRegister(0x1001) / 10
            if x > 6000:
                x = x-6553.6
                logger.info("Setting Chiller temperature to {:.1f} C.".format(x))
            self._ChillerSetTemp = x
        return self._ChillerSetTemp
        
    @ChillerSet.setter
    def ChillerSet(self, value):
        #TODO We need to implement an Ambient Temp Finder
        if value == "Ambient":
            value = self.Ambient
        if value > self._UpperLimit:
            logger.warning("Attempt to set temperature too high!")
            return
        if value < self._LowerLimit:
            logger.warning("Attempt to set temperature too low!")
            return
        if round(value * 10) != round(self._ChillerSetTemp * 10):  # don't set the same temperature we have
            logger.info("Setting Chiller temperature to {:.1f} C.".format(value))
            self._ChillerSetTemp = value
            # handle negative numbers
            if value < 0:
                value += 6553.6
            self.Chiller.WriteRegister(0x1001, round(value * 10))


#######################
    #TVAC Functionality
    def Wait(self, duration, useDumbChaser = False):
        """Waits for x number of minutes."""
        start = time.time()
        if duration == 1:
            logger.info("Waiting for {:.1f} minute.".format(duration))
        else:
            logger.info("Waiting for {:.1f} minutes.".format(duration))
        if self.DryRun == False:
            ChaserTime = time.time()
            while (((time.time() - start) / 60) < duration):
                self.Tick()
                if (useDumbChaser):
                    if time.time() >= ChaserTime + self.ThermalMassWeightDict[self._ThermalMass]:
                        if(self.DumbTempChaser(self.Target, self._TempDataStream) ): ChaserTime = time.time()

        else:
            self.Tick()
        sys.stdout.write('\n')

    def WaitForTemperature(self, TimeoutHours = 4, DegCTolerance = 0.5, TargetTemperature=False, useDumbChaser = False):
        """Wait for the chiller to reach a specific temperature (Within DegC Tolerance). If no temperature is given, function will wait until chiller
        reaches its current target."""
        startTime = time.time()
        if TargetTemperature == False:
            target = self.Target
        else:
            target = TargetTemperature
        
        self.ChillerSet = target
        logger.info("Waiting for a temperature of {:.1f} C.".format(target))
        
        if self.DryRun == False:
            
            ChaserTime = time.time()

            while (abs(self.Temperature - target) > DegCTolerance):
                self.Tick()
                if (useDumbChaser):
                    if time.time() >= ChaserTime + self.ThermalMassWeightDict[self._ThermalMass]:
                        if(self.DumbTempChaser(target, self._TempDataStream) ): ChaserTime = time.time()

                if (abs(startTime - time.time()) > TimeoutHours*60*60):
                    logger.warning(f"TVAC Sensor: {self._TargetTempSensor} could not reach target Temperature {self.Target} before timeout: {TimeoutHours}hrs")
                    logger.warning(f"Exiting WaitForTemperature Routine")
                    break
        else:
            self.Tick()
        sys.stdout.write('\n')

    def Tick(self):
        """This is a 1 minute time step which takes care of data logging and informing the user."""
        if self.DryRun == False:
            start = time.time()
            while ((time.time() - start) < 30):
                self.UpdateUser()
            self.LogTemperature()
            while ((time.time() - start) < 60):
                self.UpdateUser()
            self.LogTemperature()
        else:
            self.UpdateUser()
            self.LogTemperature()

    def Extract(self, lst, column):
        return [item[column] for item in lst]

#Print to terminal Info
    def UpdateUser(self):
        """Erase any previous text on the current line and print a new line of text in its place."""
        for i in range(55):
            sys.stdout.write('\b')
        print("{:s}  UPDATE - {:+5.1f} C -> {:+5.1f} C   ".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                  self.Temperature, self.Target), end='')
        sys.stdout.flush()
        plt.pause(0.3)


    #ToDo How Should This work??
    #Think it should puller ChillerSet Down with the TargetTemperature
    #Then if Target Sensor still hasent reached target temperature. Use DumbTempChaser to pull that down at the same rate as specified by RampRate
    def RampTemperatureTo(self, TargetTemperature, RampRate, tolerance = 0.1, UseDumbChaser = False):
        """Control the rate of temperature change of the chiller. RampRate is given in degrees C per minute."""
        RampRate = abs(RampRate)
        if RampRate < 0.01:
            logger.error("Cannot ramp slower than 0.01")
        logger.info(
            "Slewing chiller temperature to {:.1f} C at a rate of {:.2f} C/min.".format(TargetTemperature, RampRate))
        
        self.ChillerSet = self.Target
        while (abs(self.Target - TargetTemperature) > tolerance):
            DeltaT = TargetTemperature - self.ChillerSet
            DeltaT = max(DeltaT, -RampRate)
            DeltaT = min(DeltaT, RampRate)
            self.ChillerSet = self.ChillerSet + DeltaT
            self.Target = self.ChillerSet
            self.Tick()
            sys.stdout.write('\n')
        logger.info(
            "Chiller= temperature has reached {:.1f}".format(TargetTemperature))
        if not ((abs(self.Temperature - TargetTemperature) > tolerance) or UseDumbChaser): return
        
        #Get DumbWithIt
        logger.info(f"Target Sensor {self._TargetTempSensor} has still not reached the Desiserd Temp {TargetTemperature}.\n The Dumb Temp Chaser Will now take over with a max increment of {RampRate}")
        ChaserTime = time.time()
        while (abs(self.Temperature - TargetTemperature) > tolerance):
            self.Tick()
            if time.time() >= ChaserTime + self.ThermalMassWeightDict[self._ThermalMass]:
                if(self.DumbTempChaser(TargetTemperature, self._TempDataStream, MaxTempIncrement=RampRate) ): ChaserTime = time.time()

    #Check to see if the temps on the given data streem is relativley flat for the last n entries
    def TempFlatish(self, _DataSensorTemp, tolerance = .2, lengthOfCheck = 10):
        if (len(_DataSensorTemp) < lengthOfCheck): return False
        
        upperLimit = _DataSensorTemp[-1] + float(tolerance/2)
        lowerLimit = _DataSensorTemp[-1] - float(tolerance/2)
        
        return not any((temp > upperLimit or temp < lowerLimit) for temp in _DataSensorTemp[-lengthOfCheck:-1])   
    
    #This will try to pull down the temperature of the chiller so that the given sensor can reach our desired temperature
    #Returns True if it changed the temp return false if it did not
    def DumbTempChaser(self, target, _DataSensorTemp, MaxTempIncrement = 5):
        if self.TempFlatish(_DataSensorTemp) and round(self.Chiller.Temperature) == round(self.ChillerSet):
            tempDiff = abs(_DataSensorTemp[-1]  - target)
            if tempDiff > MaxTempIncrement: tempDiff = MaxTempIncrement
            
            if _DataSensorTemp[-1] < target: self.ChillerSet = self.ChillerSet + tempDiff
            else: self.ChillerSet = self.ChillerSet - tempDiff
            return True
        return False
        #the Target sensor has not reached the Target Temp and the Chiller has reached its set temperature
        #if the Target Sensor has not changed signifigantly for x
            #Change the Chiller Temp down by an increment

    #My Thought Process here is to see if the Temperature has plateud if it has and we are still above the Target Temp we should pull the Chiller temp lower
    # def CalculateDerivativeSlope(self):
    #     dx = self._TemperatureSampleInterval
    #     dy = self.Extract(self._DataRTDsTemperature, 0)[-100:]
    #     dx/dy = 