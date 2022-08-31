print("Getting ready...")
from chiller_support import chiller

StartingTemperature = None
RampDownRate = None
LowTemperature = None
DwellColdTime = None
RampUpRate = None
DwellWarmTime = None
Repetitions = None

while (StartingTemperature == None):
    x = input("What is the starting temperature [C]?\n")
    try: StartingTemperature = float(x)
    except: pass
while (RampDownRate  == None):
    x = input("What cooling rate do you want [C/min]?\n")
    try: RampDownRate = float(x)
    except: pass
while (LowTemperature  == None):
    x = input("What is the soak temperature [C]?\n")
    try: LowTemperature = float(x)
    except: pass
while (DwellColdTime  == None):
    x = input("How long do you want to soak [minutes]?\n")
    try: DwellColdTime = float(x)
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

print("Please wait a moment for the testing to begin.")
Chiller = chiller()

for i in range(Repetitions):
    print("Starting repetition {:d}.".format(i+1))
    Chiller.Target = StartingTemperature
    Chiller.WaitForTemperature()
    Chiller.RampTemperatureTo(LowTemperature,RampDownRate)
    Chiller.WaitForTemperature()
    Chiller.Wait(DwellColdTime)
    Chiller.RampTemperatureTo(StartingTemperature,RampUpRate)
    Chiller.WaitForTemperature()
    Chiller.Wait(DwellWarmTime)

del Chiller
input("\nThis test has finished. Press Enter to close both windows.\n")