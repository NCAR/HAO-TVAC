import TextFileParser
import os

#Get the User Input for all the parameters we need
def GetUserInputFile():
    PieceWiseProfile = None

    while PieceWiseProfile == None:
        PieceWiseProfile = input("Enter the Piecewise Linear Profile Filename and location: ")
        #Check to see if the input is a valid filepath
        if os.path.isfile(PieceWiseProfile):
            PieceWiseProfile = LoadPieceWiseProfile(PieceWiseProfile)
        else:
            PieceWiseProfile = None
            print("Invalid Input")

    return PieceWiseProfile

#Have the User inpuyt the information manually from the command line
def GetUserInputManual():
    StartingTemperature = None
    RampDownRate = None
    LowTemperature = None
    WarmTemperature = None
    DwellColdTime = None
    RampUpRate=None
    DwellWarmTime = None
    Repetitions = None
    UseChaser = None
    UseExtendedOptions = None
    ChosenRTD = "Floating RTD"
    UseChaser = False
    SetPointTolerance = 0.1
    ThermalMass = "Small"
    while (StartingTemperature == None):
        x = input("What is the starting temperature [C]?\n")
        try: StartingTemperature = float(x)
        except: pass
    
    while (RampDownRate  == None):
        x = input("What cooling rate do you want [C/min]?\n")
        try: RampDownRate = float(x)
        except: pass
    while (LowTemperature  == None):
        x = input("What is the lower soak temperature [C]?\n")
        try: LowTemperature = float(x)
        except: pass
    while (DwellColdTime  == None):
        x = input("How long do you want to soak [minutes]?\n")
        try: DwellColdTime = float(x)
        except: pass
    while (WarmTemperature == None):
        x = input("What is upper soak temperature [C]?\n")
        try: WarmTemperature = float(x)
        except: pass
    while (RampUpRate  == None):
        x = input("What heating rate do you want [C/min]?\n")
        try: RampUpRate = float(x)
        except: pass
    while (DwellWarmTime  == None):
        x = input("How long do you want to soak warm [minutes]?\n")
        try: DwellWarmTime = float(x)
        except: pass
    while (Repetitions  == None):
        x = input("How many repetitions would you like to do?\n")
        try: Repetitions = int(x)
        except: pass
    while (UseExtendedOptions == None):
        x = input("Would you like to go through Extended Settings? [(0)no (1)yes]\n")
        try: UseExtendedOptions = bool(x)
        except: pass


    if UseExtendedOptions: 
        ChosenRTD = None
        UseChaser = None
        SetPointTolerance = None
        ThermalMass = None
        
        #Set the Desired RTD for Temperature Setpoint
        while (ChosenRTD == None):
            x = input("Which RTD would you like to use to base Measurents off of? [suggested: Floating RTD]\n\r(0) Internal Chiller Sensor\n\r(1) Plate RTD1\n\r(2) Plate RTD2\n\r(3) Plate RTD 3\n\r(4) Floating RTD\n\r")
            try: 
                IntRTD = int(x)
            except:
                pass
            if IntRTD == 0:
                ChosenRTD = 'Chiller'
            elif IntRTD == 1:
                ChosenRTD = 'Plate1'
            elif IntRTD == 2:
                ChosenRTD = 'Plate2'
            elif IntRTD == 3:
                ChosenRTD = 'Plate3'
            elif IntRTD == 4:
                ChosenRTD = 'Floating RTD'
                           
        while (UseChaser == None):
            x = input("Keep lowering or raising the Chiller until the RTD Reaches Setpoint?\n\r(0) no\n\r(1) yes\n")
            try: UseChaser = bool(x)
            except:
                pass


        if (UseChaser):
            while (ThermalMass == None):
                x = input("Set the Thermal Mass of the object you have RTD Attached too?\n\rThis Determines How Aggressive Temperature Chasing Algo is. [suggested: small]\n\r(0) Small\n\r(1) Medium\n\r(2) Large\n\r(3) XL\n\r")
                try: 
                    IntTM = int(x)
                except:
                    pass
                if IntTM == 0:
                    ThermalMass = 'Small'
                elif IntTM == 1:
                    ThermalMass = 'Medium'
                elif IntTM == 2:
                    ThermalMass = 'Large'
                elif IntTM == 3:
                    ThermalMass = 'XL'


        while(SetPointTolerance == None):
            x = input("Set the Tolerance of the Setpoint [C] (Minimum Value 0.1)\n\r")
            try: 
                SetPointTolerance = float(x)
                if SetPointTolerance < 0.1:
                    SetPointTolerance = 0.1
            except:
                pass
    return StartingTemperature, RampDownRate, LowTemperature, WarmTemperature, DwellColdTime, RampUpRate,DwellWarmTime,Repetitions,UseChaser,UseExtendedOptions,ChosenRTD,UseChaser,SetPointTolerance,ThermalMass



#load a piecewise profile from a json file using the TextFileParser
def LoadPieceWiseProfile(FileName):
    Data = TextFileParser.runReader(FileName)
    return Data


#Branch User Input to GetUserInputManual or GetUserInputFile
def GetUserInput():
    UseFile = None
    while UseFile == None:
        UseFile = input("Would you like to use a File to input the Temperature Profile? (y/n): ")
        if UseFile == "y":
            UseFile = True
        elif UseFile == "n":
            UseFile = False
        else:
            UseFile = None
            print("Invalid Input")
    
    return UseFile