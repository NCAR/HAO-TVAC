# from errno import ELIBBAD
# from typing import Set
#from Automated_Soak_Test import StartingTemperature
from chiller_support import chiller
from rtd import rtd
from tvac import tvac
from UserInputTree import GetUserInput, GetUserInputFile, GetUserInputManual
import TextFileParser

# tvac = tvac(RTD=rtd, Chiller=Chiller, TargetSensor='Floating RTD', ThermalMass='Small')
#print(rtd.Read())
# tvac.Target = 25
# tvac.WaitForTemperature(useDumbChaser=True)
#tvac.Wait(duration = 3*60, useDumbChaser=True)
# tvac.Target = 25
# tvac.WaitForTemperature(useDumbChaser=True)
#tvac.RampTemperatureTo(TargetTemperature=25 ,RampRate=1, tolerance=0.1, UseDumbChaser=True)
#tvac.Wait(duration = 3*60, useDumbChaser=True)
#tvac.RampTemperatureTo(TargetTemperature=25,RampRate=1, tolerance=0.1, UseDumbChaser=True)
# tvac.Wait(duration = 3*60, useDumbChaser=True)
# tvac.RampTemperatureTo(TargetTemperature=25,RampRate=.5, tolerance=0.1, UseDumbChaser=True)

#Default Values




if __name__ == "__main__":
    #import the Chiller and the RTDs
    print("Requesting User Input")
    
    Chiller = chiller()
    rtd = rtd()
    
    useFile = GetUserInput()

    if not useFile:
        #Ugly Way to Do this But Should Work
        StartingTemperature, RampDownRate, LowTemperature, WarmTemperature, DwellColdTime, RampUpRate,DwellWarmTime,Repetitions,UseChaser,UseExtendedOptions,ChosenRTD,UseChaser,SetPointTolerance,ThermalMass = GetUserInputManual()
        #Create TVAC
        tvac = tvac(RTD=rtd, Chiller=Chiller, TargetSensor=ChosenRTD, ThermalMass=ThermalMass)
        tvac.Target = StartingTemperature
        for i in range(Repetitions):
            print("Starting repetition {:d}.".format(i+1))
            print(f"Begin Cooling Phase")    
            tvac.RampTemperatureTo(TargetTemperature=LowTemperature ,RampRate=RampDownRate, tolerance=SetPointTolerance, UseDumbChaser=UseChaser)
            print("Reached Cool Temp")
            print("Waiting")
            tvac.Wait(duration = DwellColdTime, useDumbChaser=UseChaser)
            print("Begin Warming Temp")
            print("Waiting")
            tvac.RampTemperatureTo(TargetTemperature=WarmTemperature ,RampRate=RampUpRate, tolerance=SetPointTolerance, UseDumbChaser=UseChaser)
            print("Reached Warm Temp")
            print("Waiting")
            tvac.Wait(duration = DwellWarmTime, useDumbChaser=UseChaser)
    
    
    else:
        #Load the File
        piecewise = GetUserInputFile()
        #Setup the TVAC Using the Parameters From the TextFileParser
        tvac = tvac(RTD=rtd, Chiller=Chiller, TargetSensor=piecewise.ChosenRTD, ThermalMass=piecewise.ThermalMass)
        tvac.Target = piecewise.StartingPoint
        tvac.WaitForTemperature(useDumbChaser=piecewise.UseChaser)
        for i in range(len(piecewise.Profiles)):
            print(f"Starting Profile {piecewise.Profiles[i].ProfileName}")
            for j in range(piecewise.Profiles[i].Repititions):
                print(f"Starting Repition {j}")
                for k in range(len(piecewise.Profiles[i].SetPoints)):
                    print(f"Setting Temperature to {piecewise.Profiles[i].SetPoints[k].Temp}")
                    tvac.RampTemperatureTo(TargetTemperature=piecewise.Profiles[i].SetPoints[k].Temp ,RampRate=piecewise.Profiles[i].SetPoints[k].RampRate, tolerance=piecewise.setPointTolerance, UseDumbChaser=piecewise.UseChaser)
                    print("Waiting")
                    tvac.Wait(duration = piecewise.Profiles[i].SetPoints[k].Hold, useDumbChaser=piecewise.UseChaser)
    
    tvac.Target = piecewise.EndingPoint
    print(f"Moving to End Temperature: {tvac.Target}")
    tvac.WaitForTemperature(useDumbChaser=piecewise.UseChaser)
    print("Done")
                
        