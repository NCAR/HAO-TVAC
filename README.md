# HAO-TVAC
Control System Codebase for the HAO TVAC

The HAO-TVAC Control System Uses NI Port to Connect to the RTD
and Communicates with the Chiller

## How to Use:
This Software is Built to be ran on the HAO-TVAC System in the Dowstairs lab

Before beginning ensure that the TVAC is turned on and Connected to the Computer VIA the 9 Pin
Ensure that the NI interface rack is connected to the Computer via a network cable. The RTDs should also be connected to the rack.

Once Hardware Connections have been confirmed 
Open up a powershell windo and navigate to the Github folder on the Desktop

run the Following code in the PowerShell Window:

`python ./main.py`

This will Begin a series of prompts which will ask the User how they prefer to run the TVAC Chiller

There are two main ways to use the TVAC Scripts
  -JSON Template
  -Manual Entry
  
### JSON Template
The Json Template is a way to make complex temperature Profiles and reuse them over and over again.
A JSON file will layout a description of a certain desired profile.
Checkout Example JSON to get a better understanding of the Full form but below is a brief description

The JSON Files will layout a Run
A run is composed of multiple Profiles
and profiles are composed of multipl Setpoints
Lets look at the Following JSON File

Example.JSON
```
{
    "RunName": "Example Cycles",
    "UseChaser": true,
    "ChosenRTD": "RTD0",
    "ThermalMass": "Small",
    "StartingPoint": "Ambient",
    "EndingPoint": "Ambient",
    "SetPointTolerance": 0.8,
    "Profiles": [
        {  
        "TempProfileName": "Survival Temps",
        "Repititions": 1,
        "Setpoint_Series": [
            {
            "SetPointName": "Survival Upper",
            "Temp [C]": 20,
            "Hold [Min]": 2,
            "Ramp Rate To Temp [C/Min]": 1
            },{
            "SetPointName": "Survival Lower",
            "Temp [C]": -10,
            "Hold [Min]": 2,
            "Ramp Rate To Temp [C/Min]":1
            }]
        },{
        "TempProfileName":"Operating Range Cycle",
        "Repititions": 8,
        "Setpoint_Series": [
            {
            "SetPointName": "Operating Range Upper",
            "Temp [C]": 10,
            "Hold [Min]": 2,
            "Ramp Rate To Temp [C/Min]": 1
            },{
            "SetPointName": "Operating Range Lower",
            "Temp [C]": -5,
            "Hold [Min]": 2,
            "Ramp Rate To Temp [C/Min]":1
            }]
        }
    ]
}
```
### Creating a JSON File
#### RunNames
The Run is the Top-Level Structure and Defines the Thermal Run. Runs Can be composed of Multiple Profiles

`RunName` type String, Used to Identify the Profile to the End User

`UseChaser` type boolean, This parameter will push the Chiller lower or higher in an attempt to drive the temperature at the RTD to the correct level.
The Chaser Algorythm check for three primary stipulations.

--Has the Chiller Reached the Set point

--Has the RTD NOT Reached the Setpoint

--is the RTD's temperature Flat (is it still moving to the setpoint)

If all of the above are true. The Chiller Temperature will lower periodically to get the RTD temperature to move down

`ChosenRTD` type String Must be one of the Following: ["Chiller","RTD0","RTD1","RTD2","RTD3","RTD4","RTD5","RTD6"] This sets which RTD we will be tracking.

`ThermalMass` type String Must Be one of the Following ["Small", "Medium", "Large", "XL"]
The thermal Mass Dictates how aggressively to use the Chasing algorythim. ie if the thermal mass is very small the Chaser will move the Chiller setpoint if the RTD temp has been flat after a short amount of time. If it is XL it will wait a substantially longer time before it starts moving the chiller setpoint. A way to think about this is 'thermal momentum' We want to give the system enough time to react to movements in the temperature


`StartingPoint` type float or String "Ambient". What temp we should reach before starting the thermal cycle. Currently "Ambient" just sets the Temp to 20C but this should be improved in the Future to be an actual ambient temperature

`EndingPoint` type float or String "Ambient" is where we should end the Thermal Cycle

`SetPointTolerance` type float. How close to the Setpoint we should get before we move on ie a SetPointTolerance of 0.8 Would mean that we only need to get with in +/-0.8C to the Setpoint before we consider it "at the Setpoint"

`Profiles` List a Set of Profiles

#### Profiles
Profiles are the Mid-level Structure and are composed of Multiple SetPoints
Each Profile should have the Following Parameters 

`TempProfileName` type String Makes an Identifier for the Profile

`Repititions` type int. The number of times that this profile should be repeated 

`Setpoint_Series` Defines a list of Setpoints to that make up this profile

#### SetPoints
The SetPoint is the Bottom-Level Structure
Each SetPoint Should have the Following Parameters

`SetPointName` type String: A name that will be referenced in the ideal profile and Runtime

`Temp [C]` type float [bound by chiller_support ranges] The Temp that the RTD will be brought to

`Hold [Min]`: type float. How long we want to stay at that set point

`Ramp Rate To Temp [C/Min]`: type float. How quickly we want to move to that set point

