import serial
import time
import sys
import pandas as pd
from io import StringIO

class QHC_Controller:

    def __init__(self, port):
        self.port = port
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.ser.flushInput()
        self.ser.flushOutput()
        self.raw_data_table = None
        self.Channels = [QHC_Channel(1, "Channel1"), QHC_Channel(2, "Channel2"), QHC_Channel(3, "Channel3"), QHC_Channel(4, "Channel4")]
        
    def __del__(self):
        self.ser.close()


    #Prints out all the information that the Controller has
    def Get_RAW(self):
        command = "RAW"
        return self.Send_Command(command)
        
    
    #Send a Command to the Controller
    def Send_Command(self, command):
        self.ser.write(f"{command}\n".encode())
        time.sleep(0.5)
        return self.ser.read_all().decode('utf-8')

 #read in the Raw data and place it into a pandas table
    def Read_Raw(self):
        #Header on the First row
        #remove all threpeated spaces from the string
        StringData = StringIO(self.Get_RAW().strip())
        self.raw_data_table = pd.read_csv(StringData, sep=" ", header=0, skipinitialspace=True, index_col=0)
        
       # self.raw_data_table = self.raw_data_table.loc[:, ~self.raw_data_table.columns.str.contains('^Unnamed')]
        #dropna(axis=1, how='all')
        print(self.raw_data_table)

    #Get Information for a specific channel
    def Get_Channel(self, channel):
        command = f"C{channel}"
        return self.Send_Command(command)

    #Parse the Information for a specific channel
    #reads the Raw output and parses it into QHC_Channel objects
    def Update_Channels(self):
        self.Read_Raw()
        for Channel in self.Channels:
            Channel.kp = self.raw_data_table.loc[f"C{Channel.channel}", "kp"]
            Channel.kd = self.raw_data_table.loc[f"C{Channel.channel}", "kd"]
            Channel.ki = self.raw_data_table.loc[f"C{Channel.channel}", "ki"]
            Channel.ep = self.raw_data_table.loc[f"C{Channel.channel}", "ep"]
            Channel.ed = self.raw_data_table.loc[f"C{Channel.channel}", "ed"]
            Channel.ei = self.raw_data_table.loc[f"C{Channel.channel}", "ei"]
            Channel.effort = self.raw_data_table.loc[f"C{Channel.channel}", "effort"]
            Channel.curr = self.raw_data_table.loc[f"C{Channel.channel}", "curr"]
            Channel.temp_current = self.raw_data_table.loc[f"C{Channel.channel}", "temp"]
            Channel.temp_average = self.raw_data_table.loc[f"C{Channel.channel}", "average"]
            Channel.temp_target = self.raw_data_table.loc[f"C{Channel.channel}", "target"]
            Channel.i2c_address = self.raw_data_table.loc[f"C{Channel.channel}", "i2c"]
            Channel.histery_length = self.raw_data_table.loc[f"C{Channel.channel}", "hist"]
            Channel.frequency = self.raw_data_table.loc[f"C{Channel.channel}", "freq"]
            Channel.enabled = self.raw_data_table.loc[f"C{Channel.channel}", "enabled"]
            Channel.sensor_status = self.raw_data_table.loc[f"C{Channel.channel}", "sensor"]
            
    #Print the information header in tsv format
    def info_header(self):
        return "Channel\tName\tkp\tkd\tki\tep\ted\tei\teffort\tcurr\ttemp_current\ttemp_average\ttemp_target\ti2c_address\thistery_length\tfrequency\tenabled\tsensor_status"

class QHC_Channel:
    def __init__(self, channel, name):
        self.channel = channel
        self.name = name
        self.kp = None
        self.kd = None
        self.ki = None
        self.ep = None
        self.ed = None
        self.ei = None
        self.effort = None
        self.curr = None
        self.temp_current = None
        self.temp_average = None
        self.temp_target = None
        self.i2c_address = None
        self.histery_length = None
        self.frequency = None
        self.enabled = None
        self.sensor_status = None

    def __str__(self):
        return f"Channel: {self.channel} Name: {self.name} kp: {self.kp} kd: {self.kd} ki: {self.ki} ep: {self.ep} ed: {self.ed} ei: {self.ei} effort: {self.effort} curr: {self.curr} temp_current: {self.temp_current} temp_average: {self.temp_average} temp_target: {self.temp_target} i2c_address: {self.i2c_address} histery_length: {self.histery_length} frequency: {self.frequency} enabled: {self.enabled} sensor_status: {self.sensor_status}"

        @property
        def duty_Cyle(self):
            return self.kp*self.ep

    




if __name__ == "__main__":
    port = input("Enter the Port: ")
    controller = QHC_Controller(port)
    controller.Update_Channels()
    
    #ask if the user wants to output to a text file
    output = input("Output to File? (y/n): ")
    if output == "y":
        #get the file name
        filename = input("Enter the File Name: ")
        #open the file
        file = open(filename, "w")
        #write the header
        file.write(controller.info_header())


    while(True):
        #create a time stamp
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #Get user input
        time.sleep(1)
        controller.Update_Channels()
        print(controller.Channels[0])

