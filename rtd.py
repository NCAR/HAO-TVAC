import nidaqmx
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
            "cDAQ9184-195CAD8Mod3/ai3:0", name_to_assign_to_channel="RTDChannel",
            min_val=-40.0, max_val=120.0, units=TemperatureUnits.DEG_C,
            rtd_type=RTDType.PT_3851,
            resistance_config=ResistanceConfiguration.THREE_WIRE,
            current_excit_source=ExcitationSource.INTERNAL,
            current_excit_val=0.001, r_0=100.0)
        #Some Type of Structure
        self._Channels = {"Plate0": 0, "Plate1": 1, "Plate2": 2, "Float": 3}
    
    def __del__(self):
         self.task.close()
    
    def Read(self, channel=None):
        
        data = self.task.read(number_of_samples_per_channel=1)
        if channel is None:
            return data
        else:
            return data[channel]
