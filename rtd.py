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
    while(True):
        read = rtds.Read()
        print(f"RTD0{read[0]}\n\rRTD1{read[1]}\n\rRTD2{read[2]}\n\rRTD3{read[3]}\n\rRTD4{read[4]}\n\rRTD5{read[5]}\n\rRTD6{read[6]}")
        time.sleep(2)