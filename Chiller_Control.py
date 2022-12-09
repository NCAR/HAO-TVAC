import nidaqmx
import time
from tvac_logger import logger

from nidaqmx.constants import (
    TerminalConfiguration, VoltageUnits, CurrentUnits,
    CurrentShuntResistorLocation, TemperatureUnits, RTDType,
    ResistanceConfiguration, ExcitationSource, ResistanceUnits, StrainUnits,
    StrainGageBridgeType, BridgeConfiguration)

task = nidaqmx.Task()
task.do_channels.add_do_chan("NI-6002/port2/line0:0", name_to_assign_to_lines="Chiller Enable")
task.write([1])

