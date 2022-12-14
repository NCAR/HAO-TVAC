import nidaqmx
import time
from tvac_logger import logger

from nidaqmx.constants import (
    TerminalConfiguration, VoltageUnits, CurrentUnits,
    CurrentShuntResistorLocation, TemperatureUnits, RTDType,
    ResistanceConfiguration, ExcitationSource, ResistanceUnits, StrainUnits,
    StrainGageBridgeType, BridgeConfiguration)


class rtd:
    def __init__(self):
        
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_rtd_chan(
            "cDAQ9184-195CAD8Mod3/ai0:3", name_to_assign_to_channel="RTD0Channel",
            min_val=-40.0, max_val=120.0, units=TemperatureUnits.DEG_C,
            rtd_type=RTDType.PT_3851,
            resistance_config=ResistanceConfiguration.THREE_WIRE,
            current_excit_source=ExcitationSource.INTERNAL,
            current_excit_val=0.001, r_0=100.0)

        self.task.ai_channels.add_ai_rtd_chan(
            "RTDs/ai0:2", name_to_assign_to_channel="RTD1Channel",
            min_val=-40.0, max_val=120.0, units=TemperatureUnits.DEG_C,
            rtd_type=RTDType.PT_3851,
            resistance_config=ResistanceConfiguration.THREE_WIRE,
            current_excit_source=ExcitationSource.INTERNAL,
            current_excit_val=0.001, r_0=100.0)
        #Some Type of Structure
        self._Channels = {"RTD0": 0, "RTD1": 1, "RTD2": 2, "RTD3": 3, "RTD4": 4, "RTD5": 5, "RTD6": 6}
    
    def __del__(self):
         self.task.close()
    
    def Read(self, channel=None):
        
        data = self.task.read(number_of_samples_per_channel=1)
        if channel is None:
            return data
        else:
            return data[channel]


if __name__ == "__main__":
    rtds = rtd()
    read_interval = int(input("Enter the Read Interval in Seconds: "))
    #Ask if user want to output information to a text file
    output_file = input("Do you want to output the data to a text file? (Y/N): ")
    if output_file == "Y" or output_file == "y":
        #Get the file name
        file_name = input("Enter the file name: ")
        #Open the file
        file = open(file_name, "w")
        #Write the header
        file.write(f"Time\tRTD0\tRTD1\tRTD2\tRTD3\tRTD4\tRTD5\tRTD6\r\n")
        file.close()

    print(f"Time\tRTD0\tRTD1\tRTD2\tRTD3\tRTD4\tRTD5\tRTD6")
    while(True):
        read = rtds.Read()
        #Get Current Date time
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #Print the data
        data = f"{time_stamp}\t{read[0][0]:.2f}\t{read[1][0]:.2f}\t{read[2][0]:.2f}\t{read[3][0]:.2f}\t{read[4][0]:.2f}\t{read[5][0]:.2f}\t{read[6][0]:.2f}"
        if output_file == "Y" or output_file == "y":
            file = open(file_name, "a")
            file.write(data)
            file.close()
        print(data)
        time.sleep(read_interval)
        