# from errno import ELIBBAD
# from typing import Set
#from Automated_Soak_Test import StartingTemperature
from chiller_support import chiller
from rtd import rtd
from tvac import tvac
from UserInputTree import GetUserInput


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
    Chiller = chiller()
    rtd = rtd()

    #Ugly Way to Do this But Should Work
    StartingTemperature, RampDownRate, LowTemperature, WarmTemperature, DwellColdTime, RampUpRate,DwellWarmTime,Repetitions,UseChaser,UseExtendedOptions,ChosenRTD,UseChaser,SetPointTolerance,ThermalMass = GetUserInput()
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
        