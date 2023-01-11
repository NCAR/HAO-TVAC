import serial
import time
import sys
import pandas as pd
from io import StringIO
#TODO -- Set Limits on Duty Cycle. Figure out why system is freezing [ZCrossing issue or Comm issue]
#Set Checks to not let user go over 15% Duty Cycle
#Auto Exit the Serial port Communication When task is closed

class QHC_Controller:

    def __init__(self, port):
        self.port = port
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.ser.flushInput()
        self.ser.flushOutput()
        self.raw_data_table = None
        self.Channels = [QHC_Channel(1, "Channel1"), QHC_Channel(2, "Channel2"), QHC_Channel(3, "Channel3"), QHC_Channel(4, "Channel4")]
        self.limit_duty_cycle = True
        self.max_duty_cycle = 0.2
        self.Upper_limit_duty_cycle = 0.2
        #Indicates if the QHC is frozen
        self.frozen = False


    def __del__(self):
        self.ser.close()

    #Set the max duty cycle
    def Set_Max_Duty_Cycle(self, duty_cycle):
        #check is the duty cycle is within the limits
        if duty_cycle > self.Upper_limit_duty_cycle:
            print(f"Error: Duty Cycle is too high. Max Duty Cycle is {self.Upper_limit_duty_cycle}")
            return
        self.max_duty_cycle = duty_cycle

    #Prints out all the information that the Controller has
    def Get_RAW(self):
        command = "RAW"
        return self.Send_Command(command)


    #This is a convoluted function Could use Clarity
    #Checks to see if we want to limit duty Cycle
    #If so is there is no value assignged to the Currentl temperature we cant do any thing
    def Check_KP_Good(self, channel, temp=None):
        if self.limit_duty_cycle:
            if self.Channels[channel-1].temp_current is None:
                #No Value assigned to the Current Temperature
                #We cant do anything
                return
            if temp is None:
                #if no temp is given we will use the current target temp
                temp = self.Channels[channel-1].temp_target.strip('C')
                
                if temp == "error" or temp is None:
                #If we got an error
                #Return
                    return
                else:
                    #Conver the temp to a float
                    temp = float(temp)

            #Check to see if value will work currently only compare to the 2 decimal places
          
            
            if round(temp - float(self.Channels[channel-1].temp_current.strip('C'))*float(self.Channels[channel-1].kp), 2) != round(self.max_duty_cycle, 2):        
                #Set the New Value so that the duty cycle is the max
                kp = round(self.max_duty_cycle/(temp - float(self.Channels[channel-1].temp_current.strip('C'))), 2)
                #format KP to 2 decimal places
                print(f"Warning: The KP value for channel {channel} is has changed. Setting KP to {kp} to maintain a duty cycle of {self.max_duty_cycle}")
                self.Set_KP(channel, kp)

    #Check if frozen
    def Check_Frozen(self):
        #see if a newly requested read is identical to the last read
        #If so we are frozen
        
        #Check for fres data three times before we declate frozen
        stale_count = 0
        for i in range(3):
            stale_data = self.raw_data_table
            self.raw_data_table = self.Read_RAW()
            if self.raw_data_table.equals(stale_data):
                stale_count += 1
                time.sleep(0.5)
            else:
                break

        if stale_count == 3:
            self.frozen = True
            print("Warning: QHC Controller is frozen. Check the connection and try again")
        else:
            self.frozen = False

        

        if self.raw_data_table.equals(stale_data):
            self.frozen = True
        else:
            self.frozen = False
        return
    #Select a Channel
    def Select_Channel(self, channel):
        command = f"C{channel}"
        self.Send_Command(command)
    
    #Set a new Temp and Check if we need to update the KP value
    def Set_Temp(self, channel, temp):
        self.Select_Channel(channel)
        self.Check_KP_Good(channel, temp)
        self.Send_Command(f"t{temp}")
        
    #Set the Frequency of the PWM
    def Set_Frequency(self, channel, frequency):
        self.Select_Channel(channel)
        self.Send_Command(f"freq={frequency}")

    #Set the proportional gain
    def Set_KP(self, channel, kp):
        self.Select_Channel(channel)
        self.Send_Command(f"p{kp}")

    #Set the Integral Gain
    def Set_KI(self, channel, ki):
        self.Select_Channel(channel)
        self.Send_Command(f"i{ki}")
    
    #Set the Derivative Gain
    def Set_KD(self, channel, kd):
        self.Select_Channel(channel)
        self.Send_Command(f"d{kd}")
    
    def Set_Enable(self, channel, enable):
        self.Select_Channel(channel)
        if enable:
            self.Send_Command(f"e")
        else:
            self.Send_Command(f"d")
    
    #Set the limit of; the I term
    def Set_LI(self, channel, li):
        self.Select_Channel(channel)
        self.Send_Command(f"I{li}")
    
    #Set the Address to Check for temperature at
    def Set_Address(self, channel, address):
        self.Select_Channel(channel)
        self.Send_Command(f"a{address}")

    #Set the History length for the integral term
    def Set_History(self, channel, history):
        self.Select_Channel(channel)
        self.Send_Command(f"h{history}")

    #Save the Current Settings to the EEPROM
    def Save_Settings(self, channel):
        self.Select_Channel(channel)
        self.Send_Command(f"s")
    
    def Reset(self):
        self.Send_Command(f"Bounce")

    #Send a Command to the Controller
    def Send_Command(self, command):
        self.ser.write(f"{command}\n".encode())
        time.sleep(0.5)
        data = self.ser.read_all().decode('utf-8')
        return data

 #read in the Raw data and place it into a pandas table to be parsed later
    def Read_Raw(self):
        #Header on the First row
        #remove all threpeated spaces from the string
        StringData = StringIO(self.Get_RAW().strip().replace("Config failed", "Failed"))
        self.raw_data_table = pd.read_csv(StringData, sep=" ", header=0, skipinitialspace=True, index_col=0)
    
       # self.raw_data_table = self.raw_data_table.loc[:, ~self.raw_data_table.columns.str.contains('^Unnamed')]
        #dropna(axis=1, how='all')
        

    #Get Information for a specific channel
    def Get_Channel(self, channel):
        command = f"C{channel}"
        return self.Send_Command(command)

    #Parse the Information for a specific channel
    #reads the Raw output and parses it into QHC_Channel objects
    def Update_Channels(self):
        try:
            self.Check_Frozen()
            self.Read_Raw()
        
            for Channel in self.Channels:
                Channel.clear_info()
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
                self.Check_KP_Good(int(Channel.channel))
        except:
            print("Error: Unable to read Raw Data")
            return
            
    #Print the information header in tsv format
    def info_header(self):
        return "Channel\tName\tkp\tkd\tki\tep\ted\tei\teffort\tcurr\ttemp_current\ttemp_average\ttemp_target\ti2c_address\thistery_length\tfrequency\tenabled\tsensor_status"
    
    #This is to make sure that the output that we are requesting is not stale


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
        self.user_requested_kp = None

    def __str__(self):
        #print all fields tab separated
        return f"{self.channel}\t{self.name}\t{self.kp}\t{self.kd}\t{self.ki}\t{self.ep}\t{self.ed}\t{self.ei}\t{self.effort}\t{self.curr}\t{self.temp_current}\t{self.temp_average}\t{self.temp_target}\t{self.i2c_address}\t{self.histery_length}\t{self.frequency}\t{self.enabled}\t{self.sensor_status}"
    
    @property
    def duty_Cyle(self):
        return self.kp*self.ep

    def clear_info(self):
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

    




if __name__ == "__main__":
    port = input("Enter the Port: ")
    try:
        controller = QHC_Controller(port)
    except:
        print(f"Could not Connect to QHC Controller on {port}\r\nPlease Check connections and try again")
        exit()
    #Request user input for which channel to use
    channel = int(input("Enter the Channel [1,2,3,4]: "))
    #Request user to input a Set Temp for the Channel
    temp = int(input("Enter Desired Temperature: "))
    #Ask user is they want to limit the Duty Cycle
    limit = input("Limit Duty Cycle? (y/n): ")
    if limit == "Y" or limit == "y":
        #Request user to input a Duty Cycle Limit
        limit = -1
        while limit <=0:
            limit = float(input("Enter Duty Cycle Limit [0-1]: "))
        controller.max_duty_cycle = limit
    
    controller.Update_Channels()
    #Set the Temperature Target
    
    controller.Set_Temp(channel, temp)
    controller.Set_Enable(channel, True)
    #controller.Set_Temp(2, 45)
    #ask the user to enter the data cadence in seconds
    read_interval = int(input("Enter the Read Interval in Seconds: "))
    #ask if the user wants to output to a text file
    output = input("Output to File? (y/n): ")
    if output == "Y" or output == "y":
        #get the file name
        filename = input("Enter the File Name: ")
        #open the file
        file = open(filename, "w")
        #write the header
        file.write(f"time\t{controller.info_header()}\n")


    while(True):
        #update the channels
        controller.Update_Channels()
        #create a time stamp
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for channel in controller.Channels:
            data = f"{time_stamp}\t{channel}"
            if output == "y" or output == "Y":
                #write the data
                file = open(filename, "a")
                file.write(f"{data}\n")
                file.close()
            print(data)
            #write a new line
        time.sleep(read_interval)
        
        

