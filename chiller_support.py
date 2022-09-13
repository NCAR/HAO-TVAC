#This is the Chiller Class Used to interface With the Chiller
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import pymodbus.exceptions
from tvac_logger import logger
import time

#Definitions for the Upper and lower capibilities of the chiller
chillerUpperLimit = 20 #Degrees C
chillerLowerLimit = -60 #Degrees C

class chiller:

    def __init__(self):
        """Opens a connection to the chiller and initializes a .CSV file."""
        self._TargetTemperature = False
        self._Temperature = False
        self._TemperatureSampleTime = False

        self._DataTemperature = []
        self._DataTarget = []

        self.client = ModbusClient(method='rtu', port='COM30', baudrate=9600, parity='E')
        self.client.connect()
        if not self.client.is_socket_open:
            logger.error("Unable to open connection to the chiller.")
            raise SystemExit()

    def __del__(self):
        logger.info("Done.")


    def ReadRegister(self, register):
        """Query one of the holding registers in the chiller controller."""
        for i in range(10):  # try up to ten times
            try:
                r = self.client.read_holding_registers(register, 1, unit=1)
                if ((type(r) == pymodbus.exceptions.ModbusIOException) or
                        (type(r) == pymodbus.pdu.ExceptionResponse)):
                    continue  # try again!
                return r.registers[0]
            except:
                pass
        logger.error("Unable to read data from chiller. Exiting.")
        raise SystemExit()

    def WriteRegister(self, register, value):
        """Write to of the registers in the chiller controller."""
        for i in range(30):  # try up to ten times
            try:
                r = self.client.write_register(register, value, unit=1)
                if ((type(r) == pymodbus.exceptions.ModbusIOException) or
                        (type(r) == pymodbus.pdu.ExceptionResponse)):
                    continue  # try again!
                return True
            except:
                pass
        logger.error("Unable to write data to chiller. Exiting.")
        raise SystemExit()

    @property
    def Temperature(self):
        if self._TemperatureSampleTime != int(time.time()):  # if we have no samples from this second
            x = self.ReadRegister(0x1000) / 10
            # handle negative numbers
            if x > 6000:
                x = x - 6553.6
            self._Temperature = x
            self._TemperatureSampleTime = int(time.time())
        return self._Temperature

    @property
    def ReadRawTarget(self):
        return self.ReadRegister(0x1001)
